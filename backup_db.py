import time
import os
from datetime import datetime
from shutil import copyfile

BACKUP_FREQ = 30
MAX_BACKUPS = 5

BACKUPS_DIR = "backups"
BACKUP_PREFIX = "database"

DIR_SEP = "\\" if os.name == "nt" else "/"

if not os.path.exists(BACKUPS_DIR):
    os.mkdir(BACKUPS_DIR)

print("Ctrl-C to kill.")

def extract_time(backup: str) -> datetime:
    name, extension = backup.split(".")
    assert extension == "db"
    prefix, creation_time = name.split("_", 1)
    assert prefix == BACKUP_PREFIX
    return datetime.strptime(creation_time, "%Y-%m-%d_%H-%M-%S")

while True:
    # Delete the old backups
    backups = [(extract_time(backup), backup) for backup in os.listdir(BACKUPS_DIR)]
    backups.sort()
    for backup in backups[:1-MAX_BACKUPS]:
        os.remove(BACKUPS_DIR+DIR_SEP+backup[1])

    # Save the new backup
    copyfile("database.db", BACKUPS_DIR+DIR_SEP+BACKUP_PREFIX+"_"+datetime.strftime(datetime.now(), "%Y-%m-%d_%H-%M-%S")+".db")

    time.sleep(BACKUP_FREQ)
