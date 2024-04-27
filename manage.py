from flask.cli import FlaskGroup
import click
import sqlite3
import json
from werkzeug.security import generate_password_hash


from helpers import make_registration
from manage_helpers import make_backup, get_activities_from_file, get_students_from_file, generate_password
from constants import *
from app import app


# SETUP
cli = FlaskGroup(app)

@cli.command()
def make_db() -> None:
    """Drops all current tables and sets up new ones in the database"""
    # Create db file if it doesn't exist
    open(DATABASE, "w").close()
    
    # Initialize sqlite3
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Drop all tables
    TABLE_PARAMETER = "{TABLE_PARAMETER}"
    DROP_TABLE_SQL = f"DROP TABLE {TABLE_PARAMETER};"
    GET_TABLES_SQL = "SELECT name FROM sqlite_schema WHERE type='table' AND name != 'sqlite_sequence';"
    
    cur.execute(GET_TABLES_SQL)
    tables = cur.fetchall()

    for table, in tables:
        sql = DROP_TABLE_SQL.replace(TABLE_PARAMETER, table)
        cur.execute(sql)
    
    # Init the database
    with open(MAKE_DATABASE_COMMAND_FILE, 'r') as sql_file:
        sql_script = sql_file.read()
        
    for command in sql_script.split(";"):
        con.execute(f"{command};")
    
    # Commit changes
    con.commit()

    # Close sqlite3 (optional)
    cur.close()
    con.close()
    

@cli.command()
def backup_db() -> None:
    make_backup(MANUAL_BACKUPS_DIR)


@cli.command()
@click.option("-f", "--filename", "filename", required=True, help="File where the activity data is stored")
def load_activities(filename: str) -> None:
    """Loads activities from a file

    Args:
        filename (str): name of the file where the activity data is stored
    """

    # Setup sqlite3
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    activities = get_activities_from_file(filename)

    qry = """
        INSERT INTO activities (title, description, type, length, classroom, image, speakers, availability)
            VALUES (:title, :description, :type, :length, :classroom, :image, :speakers, :availability);
        """

    # Load activities in db
    cur.executemany(qry, activities)
    con.commit()

    # Close sqlite3
    cur.close()
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
    cur = con.cursor()
    
    # Load student data
    students = get_students_from_file(filename)
    for student in students:
        password = generate_password()
        print(student["email"], password)
        student["hash"] = generate_password_hash(password, method=GENERATE_PASSWORD_METHOD)
        student["verification_code"] = generate_password(VERIFICATION_CODE_LENGTH)
    
    # Write to DB
    cur.executemany("INSERT INTO users (type, email, hash, name, surname, class, verification_code) VALUES ('student', :email, :hash, :name, :surname, :class, :verification_code)", students)
    con.commit()

    # Close sqlite3
    cur.close()
    con.close()           


@cli.command()
@click.option("-t", "--user-type", "user_type", required=True, help="Type of user whose schedule is going to be filled")
def fill_schedules(user_type: str) -> None:
    """Fill the empty schedules of users of the specified type with random activities"""
    # Setup sqlite3
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    # Setup constants for the users loop
    slots = [(day, timespan) for day in range(len(DAYS)) for timespan in range(len(TIMESPANS)) if user_type in PERMISSIONS[day]]
    user_ids = cur.execute("SELECT id FROM users WHERE type = ?;", (user_type,)).fetchall()

    # Fill the schedules
    for (user_id,) in user_ids:
        # Fetch all occupied slots
        registrations = cur.execute("SELECT day, module_start, module_end FROM registrations WHERE user_id = ?;", (user_id,)).fetchall()
        booked_slots = []
        
        for day, start, end in registrations:
            for timespan in range(start, end + 1):
                booked_slots.append((day, timespan))
                
        # Fetches available activities
        query = """
        SELECT id, length, availability
        FROM activities
        WHERE id NOT IN (
            SELECT activity_id
            FROM registrations
            WHERE user_id = ?
        );
        """
        non_booked_activities = sorted(cur.execute(query, (user_id,)).fetchall(), key=lambda a: a[1], reverse=True)
                
        # Fill empty slots
        for day, timespan in slots:
            # If the slot is booked, continue
            if (day, timespan) in booked_slots:
                continue
            
            # Check every actvity
            for activity_id, length, availability_str in non_booked_activities:
                availability = json.loads(availability_str)
                
                # Check if actvity length is congruent with the timespan
                if timespan % length != 0:
                    continue
                
                # Check if the slot is available
                elif availability[day][timespan // length] == 0:
                    continue
                
                # Check if the next slots are available (in case of length > 1)
                elif any([(day, pt) in booked_slots for pt in range(timespan, timespan + length) if pt < len(TIMESPANS)]):
                    continue
                                
                # Remove activity
                non_booked_activities.remove((activity_id, length, availability_str))
                
                # Remove used slots
                for partial_timespan in range(timespan, timespan + length):
                    booked_slots.append((day, partial_timespan))
                
                # Add registration
                make_registration(user_id, activity_id, day, timespan // length) # Module 

                break
            
            # If not break (no activity was found)
            else:
                raise ValueError("Not enough activities to cover the whole schedule")


# @cli.command()
# @click.option("-n", "--name", required=True, help="Name of the staff member")
# @click.option("-s", "--surname", required=True, help="Surname of the staff member")
# @click.option("-e", "--email", required=True, help="Email of the staff member")
# @click.option("-p", "--pw", "--password", "password", required=True, help="Password of the account")
# # REMOVE? alaready admin command
# def make_staff(name: str, surname: str, email: str, password: str) -> None:
#     """Make a new staff account
#     Args:
#         name (str): name of the staff member
#         surname (str): surname of the staff member
#         email (str): email of the staff member
#         password (str): password of the account
#     """
#     # Open DB connection
#     con = sqlite3.connect(DATABASE)
#     cur = con.cursor()

#     # Save user
#     pw_hash = generate_password_hash(password, GENERATE_PASSWORD_METHOD)
#     cur.execute("INSERT INTO users (type, email, hash, name, surname, verification_code) VALUES ('staff', ?, ?, ?, ?, ?)", (email, pw_hash, name, surname))
#     con.commit()
    
#     # Close DB connection
#     cur.close()
#     con.close()


if __name__ == '__main__':
    cli()
