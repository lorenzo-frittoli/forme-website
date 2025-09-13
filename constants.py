import os
import json
import copy

# Hosting
# LINK = "https://formecassini.eu.pythonanywhere.com"
LINK = "http://localhost:5000"


# Event details
DAYS = ("09/10", "10/10", "11/10")
DAYS_TEXT = ("Giovedì 9 Novembre", "Venerdì 10 Novembre", "Sabato 11 Novembre")
TIMESPANS = (("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00"))
TIMESPANS_TEXT = tuple("-".join(timespan) for timespan in TIMESPANS)
PERMISSIONS = (("student", ), ("student", "guest"), ("guest", ))

assert len(set(DAYS)) == len(DAYS)
assert len(PERMISSIONS) == len(DAYS)
assert len(DAYS_TEXT) == len(DAYS)


# Database
DATABASE = "database.db"
MAKE_DATABASE_COMMAND_FILE = "make_database.sql"


# Accounts
MAX_FIELD_LENGTH = 50


# Backups
MAX_BACKUPS = 100

DIR_SEP = os.sep
TEX_DIR = "tex" + DIR_SEP
TEMPLATES_DIR = "templates" + DIR_SEP
BACKUPS_DIR = "backups"
MANUAL_BACKUPS_DIR = BACKUPS_DIR + DIR_SEP + "manual"
TIMED_BACKUPS_DIR = BACKUPS_DIR + DIR_SEP + "timed"
AUTO_BACKUPS_DIR = BACKUPS_DIR + DIR_SEP + "auto"


# Admins (list of emails)
ADMIN_EMAILS = [
    "j@j.j"
]

# The admin password is "abcd"
ADMIN_PASSWORD = "pbkdf2:sha256:600000$XMc76EeQ2aZvB1gB$b56d9e43481a1baf0f18ff04cca361cb9755b69a27d2dee12e5e002315fddf13"


# Util
EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""


# Activities
def _load_activities(file: str, images_dir: str) -> tuple[list[dict], dict[int, dict]]:
    """Load the activities in json format from the given filename"""
    with open("data" + DIR_SEP + file, "r") as inf:
        activities = json.load(inf)

    activities.sort(key=lambda x: x["id"])
    for i, activity in enumerate(activities):
        activity["image"] = images_dir + activity["image"]

        if i > 0:
            activities[i-1]["next"] = activity["id"]
        if i + 1 < len(activities):
            activities[i+1]["prev"] = activity["id"]

    return activities, {activity["id"]: activity for activity in activities}

# This is a sort of cache to avoid opening a file or reading from the database
# Using getters with deepcopy allows adding values to the dictionaries without modifying the original data
_ACTIVITIES_CACHE = {
    None: _load_activities("activities_parsed.json", "/static/images/"), # Current year
    "23-24": _load_activities("activities_23-24.json", "/static/images_23-24/"),
}

def get_activities(year=None) -> list[dict]:
    """Returns a list of the activities sorted by id. Raises KeyError"""
    return copy.deepcopy(_ACTIVITIES_CACHE[year][0])

def get_activity(id: int, year=None) -> dict:
    """Get the information for one activity. Raises KeyError"""
    return copy.deepcopy(_ACTIVITIES_CACHE[year][1][id])
