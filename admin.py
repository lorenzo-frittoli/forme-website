from flask import Response, request, send_file, g
import sqlite3
import os
import json
from inspect import signature
from typing import Union
from functools import wraps

from helpers import *
from constants import *

commands = {}
command_annotations = []

def command(f):
    """Decorator to add a command in the admin area."""
    assert f.__name__ not in commands

    arguments = [
        {
            "name": f.__name__ + '_' + arg,
            "real_name": arg
        } for arg in signature(f).parameters
    ]
    command_annotations.append({
        "name": f.__name__,
        "args": arguments,
        "doc": f.__doc__
    })

    # All parameters are automatically extracted from the request and passed to the function as strings.
    @wraps(f)
    def wrapper():
        args = {arg["real_name"]: request.form.get(arg["name"]) for arg in arguments}
        
        if any(map(lambda x: x is None, args)):
            return "", 400

        return f(**args)

    commands[f.__name__] = wrapper
    return f


@command
def backup_db() -> tuple[str, int]:
    """Creates a new backup."""
    filename = make_backup()
    return "Backup created: " + filename, 200


@command
def list_backups() -> tuple[str, int]:
    """Shows all currently present backups."""
    return "\n".join(reversed(all_backups())), 200


@command
def download_db(backup: str) -> Union[Response, tuple[str, int]]:
    """Downloads a backup.
    If a backup name is specified the selected backup us downloaded, otherwise a new one is created and sent."""
    if not backup:
        backup = make_backup()
    elif backup not in all_backups():
        return "Invalid backup name", 400
    return send_file(BACKUPS_DIR + backup)


@command
def block_students_booking() -> tuple[str, int]:
    g.con.execute("UPDATE users SET can_book = FALSE WHERE type = 'student';")
    g.con.commit()

    return "Student bookings blocked", 200


# ##### TODO ##### Is useless as it does not stop new users from booking
# @command
def block_guests_booking() -> tuple[str, int]:
    g.con.execute("UPDATE users SET can_book = FALSE WHERE type = 'guest';")
    g.con.commit()
    
    return "Guest bookings blocked", 200


@command
def allow_booking() -> tuple[str, int]:
    g.con.execute("UPDATE users SET can_book = TRUE;")
    g.con.commit()

    return "Bookings allowed", 200


@command
def cancel_activity(id, day, module) -> tuple[str, int]:
    """Cancel an activity (setting the availability to -1)

    Args:
        id (convertible to int): id of the activity
        day (convertible to int): day in which the activity is cancelled
        module (empty or convertible to int): index of the timespan in which the activity is cancelled or empty to cancel the entire day
    """
    try:
        id = int(id)
        day = int(day)
        module = int(module) if module else None

    except ValueError:
        return "Invalid activity id, day or timespan index", 400

    if day < 0 or day >= len(DAYS):
        return "Out of bounds day", 400

    result = g.con.execute("SELECT length, availability FROM activities WHERE id = ?;", (id, )).fetchone()
    if not result:
        return "Invalid activity id", 400

    length, availability = result[0], json.loads(result[1])

    # possible BUG: `if module:` treats 0 as false 
    if module is not None:
        # Cancel only one timespan
        if module < 0 or module >= len(availability[day]):
            return "Out of bounds module", 400
        availability[day][module] = -1
        # Find the affected users
        affected_users = g.con.execute(
            "SELECT full_name, email FROM users WHERE id IN (SELECT user_id FROM registrations WHERE activity_id = ? AND day = ? AND module_start = ?);",
            (id, day, module * length)
        ).fetchall()
    else:
        # Cancel the entire day
        availability[day] = [-1] * len(availability[day])
        affected_users = g.con.execute(
            "SELECT full_name, email FROM users WHERE id IN (SELECT user_id FROM registrations WHERE activity_id = ? AND day = ?);",
            (id, day)
        ).fetchall()

    # The result is a series of tuples with only one value
    affected_users = "\n".join(map(lambda x: str(x[0]) + " (" + str(x[1]) + ")", affected_users))

    availability = json.dumps(availability)
    g.con.execute("UPDATE activities SET availability = ? WHERE id = ?;", (availability, id))
    g.con.commit()

    return f"""Cancelled activity {id} on day {day} {"timespan " + fmt_timespan(module*length, module*length + length - 1) if module is not None else "(entire day)"}
To revert, run "Recalculate availability" (before running "remove bookings") for this activity.
Consider informing the affected users via email.
Then consider removing the bookings for the affected users with "Remove bookings for cancelled activity".

Affected users:

{affected_users}
""", 200


@command
def remove_cancelled_activity_registrations(id, day, module) -> tuple[str, int]:
    """Remove bookings from a cancelled activity

    Args:
        id (convertible to int): id of the activity
        day (convertible to int): day in which the activity is cancelled
        module (empty or convertible to int): index of the timespan in which the activity is cancelled or empty to cancel the entire day
    """
    try:
        id = int(id)
        day = int(day)
        module = int(module) if module else None

    except ValueError:
        return "Invalid activity id, day or timespan index", 400

    if day < 0 or day >= len(DAYS):
        return "Out of bounds day", 400

    result = g.con.execute("SELECT length, availability FROM activities WHERE id = ?;", (id, )).fetchone()
    if not result:
        return "Invalid activity id", 400

    length, availability = result[0], json.loads(result[1])

    make_backup()

    # possible BUG: `if module:` treats 0 as false 
    if module is not None:
        # Cancel only one timespan
        if module < 0 or module >= len(availability[day]):
            return "Out of bounds module", 400

        if availability[day][module] != -1:
            # The activity should have already been cancelled
            return "This activity has not been cancelled", 400

        g.con.execute(
            "DELETE FROM registrations WHERE activity_id = ? AND day = ? AND module_start = ?;",
            (id, day, module * length)
        )
    else:
        # Cancel the entire day
        if availability[day].count(-1) != len(availability[day]):
            # The activity should have already been cancelled
            return "This activity has not been cancelled", 400

        g.con.execute(
            "DELETE FROM registrations WHERE activity_id = ? AND day = ?;",
            (id, day)
        )

    g.con.commit()

    return f"""BACKUP CREATED.
Deleted registrations for activity {id} on day {day} {"timespan " + fmt_timespan(module*length, module*length + length - 1) if module is not None else "(entire day)"}""", 200


@command
def recalculate_availability(id, new_capacity) -> tuple[str, int]:
    """Uses:
    - recalculate the availability of an activity when its capacity changes
    - revert a cancel_activity command by executing this command to recompute the original availability

    Args:
        id (convertible to int): id of the activity
        new_capacity (convertible to int): new capacity () of the activity
    """
    try:
        id = int(id)
        new_capacity = int(new_capacity)

    except ValueError:
        return "Invalid activity id, day or capacity", 400

    if new_capacity < 0:
        return "Negative capacity", 400

    result = g.con.execute("SELECT length, availability FROM activities WHERE id = ?;", (id, )).fetchone()
    if not result:
        return "Invalid activity id", 400

    length, availability = result[0], json.loads(result[1])

    # TODO Negative values (overbooked activities)
    # TODO change indexes

    new_availability = create_availability(new_capacity, length)

    for day in range(len(DAYS)):
        for module in range(len(TIMESPANS) // length):
            new_availability[day][module] -= g.con.execute(
                "SELECT count(*) FROM registrations WHERE activity_id = ? AND day = ? AND module_start = ?;",
                (id, day, module * length)
            ).fetchone()[0]
            if new_availability[day][module] < 0:
                return "Too many registrations for this capacity", 400

    g.con.execute("UPDATE activities SET availability = ? WHERE id = ?;", (json.dumps(new_availability), id))
    g.con.commit()

    return f"""Recalculated availability for activity {id}, new capacity {new_capacity}.
Old availability: {availability}
New availability: {new_availability}""", 200


@command
def make_user(full_name: str, email: str, _type: str, _class: str) -> tuple[str, int]:
    """Create a new account

    Args:
        full_name (str): surname || name of the user
        email (str): email of the user
        _type (str): type of the account
        _class (str): class of the user
    """
    if _type not in ("staff", "guest", "student"):
        return "Invalid user type: " + _type, 400

    if _type == "student":
        if not valid_class(_class):
            return "Invalid class: " + _class, 400
    elif _class != "":
        return "Class would be empty for " + _type, 400

    full_name = full_name.strip()
    email = email.strip()

    # Save user
    try:
        login_code = g.con.execute("INSERT INTO users (type, email, full_name) VALUES (?, ?, ?, ?) RETURNING login_code;", (_type, email, full_name)).fetchone()[0]
    except sqlite3.DatabaseError as e:
        return f"{e.__class__.__name__}: {' '.join(e.args)}", 400

    g.con.commit()

    return f"""Salve, può accedere al suo account tramite questo link:

{LINK}/utente?id={login_code}

Selezionando "Catalogo laboratori" dal menù in alto può visualizzare i laboratori che vengono tenuti dagli studenti e iscriversi a quelli che le interessano.

Buon ForMe!
""", 200


@command
def retrieve_login_code(email: str):
    result = g.con.execute("SELECT login_code FROM users WHERE email = ?;", (email, )).fetchone()

    if result is None:
        return "Email not found", 400

    return f"{email}: {LINK}/utente?id={result[0]}", 200


@command
def load_filled_schedules(registrations_json: str):
    """Load registrations created by fill_schedules"""
    try:
        registrations = json.loads(registrations_json)
        for registration in registrations:
            make_registration(*(registration + [g.con]))

    except json.decoder.JSONDecodeError:
        return "Invalid JSON", 400
    except ValueError:
        g.con.rollback()
        return "Update failed (are registrations closed?)", 400

    g.con.commit()

    return f"{len(registrations)} registrations uploaded successfully", 200


@command
def statistics() -> tuple[str, int]:
    """Show summaries about the status of bookings."""
    users_by_modules = g.con.execute(
        "SELECT users.type, (SELECT CAST(TOTAL(module_end - module_start + 1) AS INTEGER) FROM registrations WHERE user_id=users.id) as modules, count(*) FROM users GROUP BY users.type, modules;"
    ).fetchall()

    users_by_modules = '\n'.join(
        f"'{_type}' con {modules} moduli prenotati: {count}" for _type, modules, count in users_by_modules
    )

    modules_count = g.con.execute(
        "SELECT users.type, CAST(total(module_end - module_start + 1) AS integer) FROM registrations JOIN users ON user_id=users.id GROUP BY users.type;"
    ).fetchall()

    modules_count = '\n'.join(
        f"'{_type}': {modules} moduli prenotati" for _type, modules in modules_count
    )

    missing_by_class = g.con.execute(
        "SELECT class, count(*) FROM users WHERE id NOT IN (SELECT user_id FROM registrations) AND type='student' GROUP BY class;"
    ).fetchall()

    missing_by_class = '\n'.join(
        f"{_class}: {count} senza prenotazioni" for _class, count in missing_by_class
    )

    can_book_status = g.con.execute(
        "SELECT type, can_book, count() FROM users GROUP BY type, can_book;"
    ).fetchall()

    can_book_status = '\n'.join(
        f"'{_type}' con {can_book=}: {count}" for _type, can_book, count in can_book_status    
    )

    owned_guest_cnt = g.con.execute("SELECT count(*) FROM users WHERE type='guest' AND owner IS NOT NULL;").fetchone()[0]
    ind_guest_cnt = g.con.execute("SELECT count(*) FROM users WHERE type='guest' AND owner IS NULL;").fetchone()[0]

    guest_cnt = f"{owned_guest_cnt} esterni registrati da studenti\n{ind_guest_cnt} esterni registrati da admin"

    owners = g.con.execute(
        "SELECT email, owned, list FROM users JOIN (SELECT owner, count(*) as owned, group_concat(full_name) AS list FROM users GROUP BY owner) AS subquery ON subquery.owner=id ORDER BY owned;"
    ).fetchall()

    owners = '\n'.join(
        f"{email}: {count} esterni ({esterni})" for email, count, esterni in owners
    )

    return "\n\n".join((users_by_modules, modules_count, missing_by_class, can_book_status, guest_cnt, owners)), 200


def execute(command: str) -> Union[Response, tuple[str, int]]:
    """Executes a command."""
    if command not in commands:
        return "Command not found", 400
    else:
        return commands[command]()
