import random
import string
from datetime import datetime
import sqlite3
import re

from constants import *


def get_students_from_file(filename: str) -> list[dict]:
    """Returns student data from a csv file.
    
    Args:
        filename (str): name of the file where the data is stored


    Returns:
        list[dict]: list containing one dictionary per user
    """
    output = []
    with open(filename, "r") as students_file:
        # Each line represents a student
        for student in students_file.readlines():
            # The values are ";"-separated
            student = student.rstrip("\n").split(",")
            # The csv is in the format:
            # full_name,email,class,type
            output.append({
                "full_name": student[0],
                "email": student[1],
                "type": student[2],
                "class": student[3]
            })
    
    return output


def generate_password(length: int = GENERATED_PASSWORD_LENGTH) -> str:
    """Generates a password

    Args:
        length (int, optional): length of the password. Configurable in `constants.py`. Defaults to GENERATED_PASSWORD_LENGTH.

    Returns:
        str: password
    """
    letters = string.ascii_letters + string.digits
    
    password = "".join(random.choices(letters, k=length))
    
    return password


def make_backup(dir: str) -> str:
    """Add backup to the rolling storage

    Args:
        dir (str): backup directory
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    FILENAME_FRMT = DATABASE.replace(".", "_%Y-%m-%d_%H-%M-%S.")
    
    # Delete the old backups
    backups = [(datetime.strptime(backup, FILENAME_FRMT), backup) for backup in os.listdir(dir)]
    backups.sort()
    for backup in backups[:1-MAX_BACKUPS]:
        os.remove(dir + DIR_SEP + backup[1])

    # Lock the database and save the new backup
    filename = dir + DIR_SEP + datetime.strftime(datetime.now(), FILENAME_FRMT)
    con_backup = sqlite3.connect(filename)
    con_live = sqlite3.connect(DATABASE)
    con_live.backup(con_backup)
    con_live.close()
    con_backup.commit()
    con_backup.close()

    return filename


def valid_class(_class: str) -> bool:
    return len(_class) == 2 and _class[0] in ALLOWED_CLASSES[0] and _class[1] in ALLOWED_CLASSES[1]


def valid_email(email: str) -> bool:
    return re.match(EMAIL_REGEX, email) is not None


def create_availability(capacity: int, length: int) -> list[list[int]]:
    return [[capacity for _ in range(0, len(TIMESPANS) - length + 1, length)] for _ in DAYS]
