from flask.cli import FlaskGroup
import click
import sqlite3
import json
import random
from werkzeug.security import generate_password_hash
from jinja2 import Template


from helpers import make_registration, make_backup, generate_password, create_availability, valid_class, valid_email, fmt_timespan
from constants import *


# SETUP
cli = FlaskGroup()

@cli.command()
def make_db() -> None:
    """Create a new empty database"""
    if os.path.exists(DATABASE):
        make_backup(AUTO_BACKUPS_DIR)
        os.remove(DATABASE)

    with open(MAKE_DATABASE_COMMAND_FILE, 'r') as f:
        sql_script = f.read()   # Command file as string

    con = sqlite3.connect(DATABASE)

    con.executescript(sql_script)

    con.commit()
    con.close()

@cli.command()
def backup_db() -> None:
    """Create a backup of the database"""
    make_backup(MANUAL_BACKUPS_DIR)


@cli.command()
def load_activities() -> None:
    """Populates the database with the activities loaded in constants.py"""
    # Setup sqlite3
    con = sqlite3.connect(DATABASE)

    activities = get_activities()
    for activity in activities:
        activity["availability"] = json.dumps(
            create_availability(activity["capacity"], activity["length"])
        )

    # Load activities in db
    con.executemany("INSERT INTO activities (id, length, availability) VALUES (:id, :length, :availability);", activities)
    con.commit()

    # Close sqlite3
    con.close()


@cli.command()
@click.option("-f", "--filename", "filename", required=True, help="File where the student data is stored")
def load_students(filename: str) -> None:
    """Loads students from a file

    Args:
        filename (str): name of the file where the student data is stored
    """
    # Setup sqlite3
    con = sqlite3.connect(DATABASE)

    # Load student data
    students = []
    with open(filename, "r") as students_file:
        # Each line represents a student
        for student in students_file.readlines():
            student = student.rstrip("\n").split(",")
            students.append({
                "full_name": student[0],
                "email": student[1],
                "type": student[2],
                "class": student[3]
            })

    for student in students:
        password = generate_password()
        student["full_name"] = student["full_name"].title()
        student["email"] = student["email"].lower()
        student["class"] = student["class"].upper()
        student["hash"] = generate_password_hash(password, method=GENERATE_PASSWORD_METHOD)

        print(student["email"], password)
        assert valid_class(student["class"])
        assert valid_email(student["email"])
        assert student["type"] in ("student", "staff")
    
    # Write to DB
    con.executemany("INSERT INTO users (type, email, hash, full_name, class) VALUES (:type, :email, :hash, :full_name, :class)", students)
    con.commit()

    # Close sqlite3
    con.close()


def try_fill_schedules(user_type: str, k: int, seed: int, con: sqlite3.Connection) -> bool:
    """
    Args:
        user_type (str)
        k (int): a parameter for the fill. If k is high long activities will be filled first.
        con (sqlite3.Connection)
    Returns:
        pair[int, int]: number of filled modules, number of non-filled modules
    """
    # The days which are to be filled
    fill_days: list[int] = [day for day in range(len(DAYS)) if user_type in PERMISSIONS[day]]
    # All the users with the matching type
    user_ids = list(map(lambda x: x[0], con.execute("SELECT id FROM users WHERE type = ?;", (user_type,)).fetchall()))
    # A different order will give different results.
    random.seed(seed)
    random.shuffle(user_ids)
    # All the activities
    activities = con.execute("SELECT id, length, availability FROM activities;").fetchall()
    # A list with an entry for each pair (activity, timespan) grouped by availability. Faster alternative to sorting
    # We save the index of the last successful booking we made +1 for this slot to avoid checking the same users over and over.
    # [id, day, module, length, next user index]
    slots_by_avail: list[list[list[int]]] = []

    for id, length, availability in activities:
        availability = json.loads(availability)
        for day in fill_days:
            for module in range(len(TIMESPANS)//length):
                # When k is large, longer modules will be filled first.
                priority = max(0, availability[day][module]) + length*k
                while len(slots_by_avail) <= priority:
                    slots_by_avail.append([])
                slots_by_avail[priority].append([id, day, module, length, 0])

    for slots in slots_by_avail:
        random.shuffle(slots)

    # Fill the slots with the most availability first.
    filled_modules = 0
    for curr_avail in range(len(slots_by_avail)-1, 0, -1):
        # Fill the longer activities first
        slots_by_avail[curr_avail].sort(key=lambda x: -x[3])
        for slot in slots_by_avail[curr_avail]:
            for users_index in range(slot[4], len(user_ids)):
                try:
                    make_registration(user_ids[users_index], slot[0], slot[1], slot[2], user_type, con)
                except ValueError:
                    pass
                else:
                    # The registration was successful
                    filled_modules += slot[3] # Length of the activity
                    slot[4] = users_index+1
                    slots_by_avail[curr_avail-1].append(slot)
                    break
            # If the registration could not be made the slot will not be moved to the next iteration

    # Check that all schedules are filled
    non_filled_modules = 0
    for user_id in user_ids:
        module_booked = [[False for _ in TIMESPANS] for _ in DAYS]
        # Fetch all activities from the user
        registrations = con.execute("SELECT day, module_start, module_end FROM registrations WHERE user_id = ?;", (user_id, )).fetchall()
        for day, module_start, module_end in registrations:
            for module in range(module_start, module_end+1):
                assert not module_booked[day][module]
                module_booked[day][module] = True
        for day in fill_days:
            non_filled_modules += module_booked[day].count(False)
    
    # Print info to terminal
    if non_filled_modules:
        print(f"{filled_modules} moduli riempiti, {non_filled_modules} moduli non riempiti.")
    else:
        print(f"Tutti i {filled_modules} moduli sono stati riempiti.")

    return non_filled_modules == 0


@cli.command()
@click.option("-t", "--user-type", "user_type", required=True, help="Type of user whose schedule is going to be filled")
def fill_schedules(user_type: str) -> None:
    """Fill the empty schedules of users of the specified type with random activities"""
    # Avoid conflicts with people booking from the app
    if input("Eseguire solamente in locale. Proseguire? Y/n: ") != "Y":
        return
    # Make a backup in case the fill isn't successful.
    make_backup(AUTO_BACKUPS_DIR)
    print("Backup creato")

    # Setup sqlite3
    con = sqlite3.connect(DATABASE)

    for k in range(20):
        for seed in range(50):
            print(f"Tentativo {k=}, {seed=}:", end='\t')
            if try_fill_schedules(user_type, k, seed, con):
                # The fill was successful
                break
            con.rollback()
        else:
            # Keep searching
            continue
        break

    con.commit()
    con.close()


def render_pdf(input, output, **kwargs) -> None:
    if not os.path.exists(TEX_DIR):
        os.makedirs(TEX_DIR)

    with open(TEMPLATES_DIR + input, "r") as t_file, open(TEX_DIR + output, "w") as outf:
        outf.write(Template(t_file.read(), line_statement_prefix="%-j-").render(**kwargs))


@cli.command()
def make_pdfs():
    def chunks(lst, n):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    con = sqlite3.connect(DATABASE)

    # Create a separate pdf for each day
    for day_index, day in enumerate(DAYS):
        data = []

        for activity in get_activities():
            activity["title"] = activity["title"].replace('&', '\\&')
            activity["speakers"] = activity["speakers"].replace('&', '\\&')

            data.append((str(activity["id"]) + " - " + activity["title"], activity["speakers"], []))

            for module_start in range(0, len(TIMESPANS)-activity["length"]+1, activity["length"]):
                result = con.execute(
                    "SELECT full_name, class FROM users JOIN registrations ON users.id = registrations.user_id WHERE activity_id = ? AND day = ? AND module_start = ? ORDER BY full_name;",
                    (activity["id"], day_index, module_start)
                ).fetchall()

                if len(result) % 2:
                    result.append(("", ""))

                data[-1][2].append((
                    fmt_timespan(module_start, module_start + activity["length"] - 1),
                    [(_class0 or "", full_name0, _class1 or "", full_name1) for (full_name0, _class0), (full_name1, _class1) in chunks(result, 2)],
                ))

        # File con '/' nel nome non sono validi
        render_pdf(
            "pdfs.tex",
            day.replace("/", "_")+".tex",
            day=DAYS_TEXT[day_index],
            activities=data,
        )


@cli.command()
def make_cancelled():
    DAY = 2

    con = sqlite3.connect(DATABASE)

    activities = con.execute("SELECT id, length, availability FROM activities ORDER BY id;").fetchall()

    data = []

    for activity_id, activity_length, activity_availability in activities:
        activity_title = get_activity(activity_id)["title"].replace('&', '\\&')
        activity_availability = json.loads(activity_availability)[DAY]

        data.append((activity_id, activity_title, []))

        for module, module_start in enumerate(range(0, len(TIMESPANS)-activity_length+1, activity_length)):
            module_end = module_start + activity_length - 1
            data[-1][2].append((fmt_timespan(module_start, module_end), 'ANNULLATO' if activity_availability[module] == -1 else ''))

    render_pdf(
        "cancelled.tex",
        "cancelled.tex",
        day=DAYS_TEXT[DAY],
        activities=data,
    )


if __name__ == '__main__':
    cli()
