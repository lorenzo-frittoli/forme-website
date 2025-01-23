from flask import Response, request, send_file, g
import sqlite3
import os
import json
from inspect import signature
from typing import Union
from functools import wraps
from werkzeug.security import generate_password_hash

from helpers import fmt_timespan
from manage_helpers import make_backup, generate_password, valid_class, create_availability
from constants import *

commands = {}
command_annotations = {}

def command(f):
    """Decorator to add a command in the admin area."""
    assert f.__name__ not in commands

    # Add prefix to avoid conflicts
    arguments = [f.__name__ + "_" + arg for arg in signature(f).parameters]
    command_annotations[f.__name__] = arguments

    # All parameters are automatically extracted from the request and passed to the function as strings.
    @wraps(f)
    def wrapper():
        args = {argument.removeprefix(f.__name__ + "_"): request.form.get(argument) for argument in arguments}
        
        if any(map(lambda x: x is None, args)):
            return "", 400

        return f(**args)

    commands[f.__name__] = wrapper
    return f


def all_backups() -> list[str]:
    """Returns a list with all currently present backups."""
    backups = []
    for dir in (AUTO_BACKUPS_DIR, MANUAL_BACKUPS_DIR, TIMED_BACKUPS_DIR):
        if not os.path.exists(dir):
            os.makedirs(dir)
        backups += [dir + DIR_SEP + filename for filename in os.listdir(dir)]
    return sorted(backups)


@command
def backup_db() -> tuple[str, int]:
    """Creates a new backup."""
    filename = make_backup(MANUAL_BACKUPS_DIR)
    return "Backup created: " + filename, 200


@command
def list_backups() -> tuple[str, int]:
    """Shows all currently present backups."""
    return "\n".join(all_backups()), 200


@command
def download_db(backup: str) -> Union[Response, tuple[str, int]]:
    """Downloads a backup.
    If a backup name is specified the selected backup us downloaded, otherwise a new one is created and sent."""
    if not backup:
        backup = make_backup(MANUAL_BACKUPS_DIR)
    elif backup not in all_backups():
        return "Invalid backup name", 200
    return send_file(backup)


@command
def change_pwd(user_email: str, new_password: str) -> tuple[str, int]:
    if user_email in ADMIN_EMAILS:
        return "Cannot change an admin's password", 200

    # Check that the user exists
    if not g.con.execute("SELECT 1 FROM users WHERE email = ?", (user_email, )).fetchone():
        return "Email not found", 200
    
    # Create a random password in none is provided
    if not new_password:
        new_password = generate_password()

    password_hash = generate_password_hash(new_password, method=GENERATE_PASSWORD_METHOD)

    g.con.execute("UPDATE users SET hash = ? WHERE email = ?", (password_hash, user_email))
    g.con.commit()

    return f"New password for {user_email}: {new_password}", 200


@command
def block_students_booking() -> tuple[str, int]:
    g.con.execute("UPDATE users SET can_book = FALSE WHERE type = 'student';")
    g.con.commit()

    return "Bookings blocked", 200


@command
def block_guests_booking() -> tuple[str, int]:
    g.con.execute("UPDATE users SET can_book = FALSE WHERE type = 'guest';")
    g.con.commit()
    
    return "Bookings blocked", 200


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
            "SELECT email FROM users WHERE id IN (SELECT user_id FROM registrations WHERE activity_id = ? AND day = ? AND module_start = ?);",
            (id, day, module * length)
        ).fetchall()
    else:
        # Cancel the entire day
        availability[day] = [-1] * len(availability[day])
        affected_users = g.con.execute(
            "SELECT email FROM users WHERE id IN (SELECT user_id FROM registrations WHERE activity_id = ? AND day = ?);",
            (id, day)
        ).fetchall()

    # The result is a series of tuples with only one value
    affected_users = "\n".join(map(lambda x: x[0], affected_users))

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
def remove_cancelled(id, day, module) -> tuple[str, int]:
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

    # Create a backup
    make_backup(AUTO_BACKUPS_DIR)

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
def recalc_availability(id, new_capacity) -> tuple[str, int]:
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
def make_user(name: str, surname: str, email: str, _type: str, _class: str) -> tuple[str, int]:
    """Create a new account

    Args:
        name (str): name of the user
        surname (str): surname of the user
        email (str): email of the user
        password (str): password of the user
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

    pwd = generate_password()
    pw_hash = generate_password_hash(pwd, GENERATE_PASSWORD_METHOD)
    verification_code = generate_password(VERIFICATION_CODE_LENGTH)
    # Save user
    try:
        g.con.execute("INSERT INTO users (type, email, hash, name, surname, verification_code) VALUES (?, ?, ?, ?, ?, ?)", (_type, email, pw_hash, name, surname, verification_code))
    except sqlite3.DatabaseError as e:
        return f"{e.__class__.__name__}: {' '.join(e.args)}", 400

    g.con.commit()

    return f"User created: {email}\nPassword: {pwd}", 200


def execute(command: str) -> Union[Response, tuple[str, int]]:
    """Executes a command."""
    if command not in commands:
        return "Command not found", 400
    else:
        return commands[command]()
