from flask import Response, request, send_file
import os
from inspect import signature
from typing import Union
from werkzeug.security import generate_password_hash

from manage_helpers import make_backup
from manage import make_staff
from constants import *

commands = {}
command_annotations = {}

def command(f):
    """Decorator to add a command in the admin area."""
    arguments = list(signature(f).parameters)
    command_annotations[f.__name__] = arguments

    # All parameters are automatically extracted from the request and passed to the function as strings.
    def wrapper():
        args = {argument: request.form.get(argument) for argument in arguments}
        
        if any(map(lambda x: x is None, args)):
            return "", 400

        return f(**args)

    wrapper.__name__ = f.__name__
    commands[f.__name__] = wrapper
    return f


def all_backups() -> list[str]:
    """Returns a list with all currently present backups."""
    backups = []
    for dir in (AUTO_BACKUPS_DIR, MANUAL_BACKUPS_DIR):
        if not os.path.exists(dir):
            os.makedirs(dir)
        backups += [dir + DIR_SEP + filename for filename in os.listdir(dir)]
    return backups


def change_user_password(email: str, new_password: str) -> None:
    """Changes a users pw

    Args:
        email (str): email of the user
        new_password (str): new password (plain text)
        
    Raises:
        ValueError: email is not registered
    """

    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    cur.execute("SELECT 1 FROM users WHERE email = ?", (email, ))
    if not cur.fetchone():
        raise ValueError("Email not found")
    
    elif email in ADMIN_EMAILS:
        raise ValueError("Cannot change an admin's password")
    
    password_hash = generate_password_hash(new_password, method=GENERATE_PASSWORD_METHOD)
    cur.execute("UPDATE users SET hash = ? WHERE email = ?", (password_hash, email))
    con.commit()
    
    cur.close()
    con.close()
    

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
def download_db(backup) -> Response:
    """Downloads a backup.
    If a backup name is specified the selected backup us downloaded, otherwise a new one is created and sent."""
    if not backup:
        backup = MANUAL_BACKUPS_DIR + DIR_SEP + make_backup(MANUAL_BACKUPS_DIR)
    elif backup not in all_backups():
        return "Invalid backup name", 200
    return send_file(backup)


@command
def change_password(user_email, new_password) -> tuple[str, int]:
    """Admin page command to change a user's password"""
    try:
        change_user_password(user_email, new_password)

    except ValueError as val_error:
        return val_error.args[0], 200
    
    return f"Password changed for {user_email}!", 200


def execute(command: str) -> Union[Response, tuple[str, int]]:
    """Executes a command."""
    if command not in commands:
        return "Command not found", 400
    else:
        return commands[command]()
