from flask import Response, request, send_file
import os
from inspect import signature
from typing import Union

from manage_helpers import make_backup
from constants import *

commands = {}
command_annotations = {}

def command(f):
    """Decorator to add a command in the admin area."""
    arguments = list(signature(f).parameters)
    command_annotations[f.__name__] = arguments

    # All parameters are automatically estracted from the request and passed to the function as strings.
    def wrapper():
        args = {argument: request.form.get(argument) for argument in arguments}
        return f(**args)

    wrapper.__name__ = f.__name__
    commands[f.__name__] = wrapper
    return wrapper


def all_backups() -> list[str]:
    """Returns a list with all currently present backups."""
    backups = []
    for dir in (AUTO_BACKUPS_DIR, MANUAL_BACKUPS_DIR):
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
def download_db(backup) -> Response:
    """Downloads a backup.
    If a backup name is specified the selected backup us downloaded, otherwise a new one is created and sent."""
    if backup is None:
        return "", 400
    if not backup:
        backup = MANUAL_BACKUPS_DIR + DIR_SEP + make_backup(MANUAL_BACKUPS_DIR)
    elif backup not in all_backups():
        return "Invalid backup name", 200
    return send_file(backup)


@command
def download_logs() -> tuple[str, int]:
    raise NotImplementedError


@command
def change_password(user, new_password) -> tuple[str, int]:
    raise NotImplementedError


def execute(command: str) -> Union[Response, tuple[str, int]]:
    """Executes a command."""
    if command not in commands:
        return "Command not found", 400
    else:
        return commands[command]()
