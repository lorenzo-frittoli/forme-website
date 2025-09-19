import os

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

TEX_DIR = "tex" + os.sep
TEMPLATES_DIR = "templates" + os.sep
BACKUPS_DIR = "backups" + os.sep

# Admins (list of emails)
ADMIN_EMAILS = [
    "j@j.j"
]

# The default admin password is "abcd"
ADMIN_PASSWORD = "pbkdf2:sha256:600000$XMc76EeQ2aZvB1gB$b56d9e43481a1baf0f18ff04cca361cb9755b69a27d2dee12e5e002315fddf13"


# Util
EMAIL_REGEX = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
