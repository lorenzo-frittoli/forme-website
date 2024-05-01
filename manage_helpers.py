import random
import json
import string
from datetime import datetime
import sqlite3

from constants import *


def get_students_from_file(filename: str) -> list[dict]:
    """Returns student data from a csv file.
    
    Args:
        filename (str): name of the file where the data is stored


    Returns:
        list[dict]: list of students data: [{name, surname, class, email}, ...]
    """
    output = []
    with open(filename, "r") as students_file:
        # Each line represents a student
        for student in students_file.readlines():
            # The values are ";"-separated
            student = student.rstrip("\n").split(";")
            # The csv is in the format:
            # ...; name+surname; ...; ...; ...; ...; class; email
            output.append({
                "name": student[1],
                "surname": "",
                "class": student[6],
                "email": student[7]
            })
    
    return output


def get_activities_from_file(filename: str) -> list[dict]:
    """Read activities from a file

    Args:
        filename (str): name of the file where the data is stored

    Returns:
        list[dict]: list of activity data: [{title, description, type, length, availability}]
    """


    def parse_row(row: str) -> list[str]:
        """Parse a csv row.
        """
        return row.rstrip("\n").split(";")

    with open(filename, "r", encoding="UTF-8") as file:
        data = [
            {
                "image": data[0],
                "length": int(data[2]),
                "classroom": data[3],
                "availability": json.dumps([[int(data[1]) for _ in range(0, len(TIMESPANS) - int(data[2]) + 1, int(data[2]))] for _ in DAYS]),
                "title": data[4],
                "speakers": data[5],
                "description": data[6],
                "type": data[7]
            }
        for data in map(parse_row, file.readlines())]
    
    return data


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
    filename = datetime.strftime(datetime.now(), FILENAME_FRMT)
    con_backup = sqlite3.connect(dir + DIR_SEP + filename)
    con_live = sqlite3.connect(DATABASE)
    con_live.backup(con_backup)
    con_live.close()
    con_backup.commit()
    con_backup.close()

    return filename
