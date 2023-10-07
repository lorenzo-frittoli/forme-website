import random
import json
import string
from datetime import datetime
import sqlite3
from werkzeug.security import generate_password_hash

from constants import *


def get_students_from_file(filename: str) -> list[dict]:
    """RETURNS DUMMY OUTPUT. Returns student data from a file.
    
    Args:
        filename (str): name of the file where the data is stored


    Returns:
        list[dict]: list of students data: [{name, surname, class, email}, ...]
    """
    dummy_output = [
        {"name": "Giovanni",
         "surname": "Giorgio",
         "class": "5A",
         "email": "giovanni.giorgio@liceocassini.eu"},
        
        {"name": "Nicola",
         "surname": "Gay",
         "class": "5J",
         "email": "nicola.gay@liceocassini.eu"}
    ]
    
    return dummy_output
    
    
def get_activities_from_file(filename: str) -> list[dict]:
    """RETURNS DUMMY OUTPUT. Returns student data from a file

    Args:
        filename (str): name of the file where the data is stored

    Returns:
        list[dict]: list of activity data: [{title, description, type, length, availability}]
    """
    titles = ("Title 1", "Title 2")
    types = ("Type 1", "Type 2")
    lengths = (1, 2)
    classrooms = ("4.20", "6.9")
    description = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Maecenas volutpat blandit aliquam etiam erat velit scelerisque in. Praesent semper feugiat nibh sed pulvinar proin. Condimentum vitae sapien pellentesque habitant. Mi in nulla posuere sollicitudin aliquam. Commodo viverra maecenas accumsan lacus vel facilisis. Etiam non quam lacus suspendisse faucibus. Eu non diam phasellus vestibulum lorem sed risus ultricies tristique. Egestas pretium aenean pharetra magna ac placerat. Sed velit dignissim sodales ut eu sem integer vitae justo. Facilisi etiam dignissim diam quis enim lobortis scelerisque fermentum dui. In arcu cursus euismod quis.
    Lorem sed risus ultricies tristique nulla. Rhoncus urna neque viverra justo nec ultrices dui sapien. Venenatis urna cursus eget nunc. Tristique sollicitudin nibh sit amet commodo nulla facilisi. Rhoncus aenean vel elit scelerisque. Tempor commodo ullamcorper a lacus vestibulum sed arcu. In hendrerit gravida rutrum quisque non tellus orci ac auctor. Eget felis eget nunc lobortis mattis. Turpis nunc eget lorem dolor sed viverra ipsum nunc. Congue nisi vitae suscipit tellus. Pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Rhoncus aenean vel elit scelerisque. Fermentum odio eu feugiat pretium nibh ipsum consequat nisl vel. Ut sem nulla pharetra diam sit. Natoque penatibus et magnis dis parturient. Lacus sed turpis tincidunt id aliquet risus feugiat in ante. Suspendisse in est ante in nibh mauris cursus. Pulvinar neque laoreet suspendisse interdum. Sollicitudin tempor id eu nisl nunc mi ipsum.
    Imperdiet dui accumsan sit amet nulla facilisi. Tellus elementum sagittis vitae et leo duis ut diam quam. Quam viverra orci sagittis eu volutpat. Nunc sed id semper risus in hendrerit. Fames ac turpis egestas maecenas pharetra convallis posuere. Ultrices vitae auctor eu augue ut. Amet nisl suscipit adipiscing bibendum est ultricies. Habitasse platea dictumst quisque sagittis purus sit. Lobortis mattis aliquam faucibus purus in. Viverra tellus in hac habitasse. Eu scelerisque felis imperdiet proin fermentum leo. Bibendum ut tristique et egestas quis ipsum suspendisse. Sit amet consectetur adipiscing elit pellentesque. Feugiat vivamus at augue eget arcu dictum varius duis at. Duis at tellus at urna condimentum mattis pellentesque id nibh. Morbi non arcu risus quis varius quam. Fringilla urna porttitor rhoncus dolor purus. Nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit. Pellentesque eu tincidunt tortor aliquam nulla facilisi cras fermentum odio. Quis commodo odio aenean sed.
    """
    data = [
        {
            "title": tit,
            "description": description,
            "type": typ,
            "length": l,
            "classroom": c,
            "availability": json.dumps([[20 for _ in range(0, len(TIMESPANS) - l + 1, l)] for _ in DAYS])
        }
    for tit, typ, c, l in zip(titles, types, classrooms, lengths)]
    
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


def make_backup(dir: str) -> None:
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

