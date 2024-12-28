from flask import Response, request, send_file, g
import sqlite3
import os
from inspect import signature
from typing import Union
from werkzeug.security import generate_password_hash

from manage_helpers import make_backup, generate_password
from constants import *

commands = {}
command_annotations = {}

def command(f):
    """Decorator to add a command in the admin area."""
    # Add prefix to avoid conflicts
    arguments = [f.__name__ + "_" + arg for arg in signature(f).parameters]
    command_annotations[f.__name__] = arguments

    # All parameters are automatically extracted from the request and passed to the function as strings.
    def wrapper():
        args = {argument.removeprefix(f.__name__ + "_"): request.form.get(argument) for argument in arguments}
        
        if any(map(lambda x: x is None, args)):
            return "", 400

        return f(**args)

    wrapper.__name__ = f.__name__
    commands[f.__name__] = wrapper
    return f


def all_backups() -> list[str]:
    """Returns a list with all currently present backups."""
    backups = []
    for dir in (AUTO_BACKUPS_DIR, MANUAL_BACKUPS_DIR, TIMED_BACKUPS_DIR):
        if not os.path.exists(dir):
            os.makedirs(dir)
        backups += [dir + DIR_SEP + filename for filename in os.listdir(dir)]
    return backups


@command
def backup_db() -> tuple[str, int]:
    """Creates a new backup."""
    filename = make_backup(MANUAL_BACKUPS_DIR)
    return "Backup created: " + MANUAL_BACKUPS_DIR + DIR_SEP + filename, 200


@command
def list_backups() -> tuple[str, int]:
    """Shows all currently present backups."""
    return "\n".join(all_backups()), 200


@command
def download_db(backup) -> Response | tuple[str, int]:
    """Downloads a backup.
    If a backup name is specified the selected backup us downloaded, otherwise a new one is created and sent."""
    if not backup:
        backup = MANUAL_BACKUPS_DIR + DIR_SEP + make_backup(MANUAL_BACKUPS_DIR)
    elif backup not in all_backups():
        return "Invalid backup name", 200
    return send_file(backup)


@command
def change_password(user_email, new_password) -> tuple[str, int]:
    if user_email in ADMIN_EMAILS:
        return "Cannot change an admin's password", 200

    cur = g.con.cursor()

    # Check that the user exists
    cur.execute("SELECT 1 FROM users WHERE email = ?", (user_email, ))
    if not cur.fetchone():
        return "Email not found", 200
    
    # Create a random password in none is provided
    if not new_password:
        new_password = generate_password()

    password_hash = generate_password_hash(new_password, method=GENERATE_PASSWORD_METHOD)

    cur.execute("UPDATE users SET hash = ? WHERE email = ?", (password_hash, user_email))
    g.con.commit()

    cur.close()
    
    return f"New password for {user_email}: {new_password}", 200


@command
def block_students_booking() -> tuple[str, int]:
    cur = g.con.cursor()

    cur.execute("UPDATE users SET can_book = FALSE WHERE type = 'student';")
    
    g.con.commit()
    cur.close()

    return "Bookings blocked", 200


@command
def block_guests_booking() -> tuple[str, int]:
    cur = g.con.cursor()

    cur.execute("UPDATE users SET can_book = FALSE WHERE type = 'guest';")
    
    g.con.commit()
    cur.close()
    
    return "Bookings blocked", 200


@command
def allow_booking() -> tuple[str, int]:
    cur = g.con.cursor()

    cur.execute("UPDATE users SET can_book = TRUE;")

    g.con.commit()
    cur.close()

    return "Bookings allowed", 200


@command
def make_user(name: str, surname: str, email: str, _type: str, _class: str) -> tuple[str, int]:
    """Make a new staff account

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
        if len(_class) != 2 or _class[0] not in ALLOWED_CLASSES[0] or _class[1] not in ALLOWED_CLASSES[1]:
            return "Invalid class: " + _class, 400
    elif _class != "":
        return "Class would be empty for " + _type, 400

    cur = g.con.cursor()

    pwd = generate_password()
    pw_hash = generate_password_hash(pwd, GENERATE_PASSWORD_METHOD)
    verification_code = generate_password(VERIFICATION_CODE_LENGTH)
    # Save user
    try:
        cur.execute("INSERT INTO users (type, email, hash, name, surname, verification_code) VALUES (?, ?, ?, ?, ?, ?)", (_type, email, pw_hash, name, surname, verification_code))
    except sqlite3.DatabaseError as e:
        return f"{e.__class__.__name__}: {' '.join(e.args)}", 400

    g.con.commit()
    cur.close()

    return f"User created: {email}\nPassword: {pwd}", 200


def execute(command: str) -> Union[Response, tuple[str, int]]:
    """Executes a command."""
    if command not in commands:
        return "Command not found", 400
    else:
        return commands[command]()
