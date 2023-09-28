import sqlite3

# Event details
DAYS = ("07/10", "08/10", "09/10")
TIMESPANS = (("08:00", "09:00"), ("09:00", "10:00"), ("10:00", "11:00"), ("11:00", "12:00"))
TIMESPANS_TEXT = tuple("-".join(timespan) for timespan in TIMESPANS)
PERMISSIONS = (("student", ), ("student", "guest"), ("guest", ))

assert len(PERMISSIONS) == len(DAYS)

# Database
DATABASE = "database.db"
MAKE_DATABASE_COMMAND_FILE = "make_database.sql"
CONNECTION = sqlite3.connect(DATABASE, check_same_thread=False)

# Util
EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
