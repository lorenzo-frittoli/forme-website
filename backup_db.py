import time
import os
from datetime import datetime
from shutil import copyfile

# In seconds
BACKUP_FREQ = 24*60*60 # Each day
MAX_BACKUPS = 5

BACKUPS_DIR = "backups"
FILENAME_FRMT = "database_%Y-%m-%d_%H-%M-%S.db"

DIR_SEP = "\\" if os.name == "nt" else "/"

def backup_db():
    # Delete the old backups
    backups = [(datetime.strptime(backup, FILENAME_FRMT), backup) for backup in os.listdir(BACKUPS_DIR)]
    backups.sort()
    for backup in backups[:1-MAX_BACKUPS]:
        os.remove(BACKUPS_DIR+DIR_SEP+backup[1])

    # Save the new backup
    copyfile("database.db", BACKUPS_DIR+DIR_SEP+datetime.strftime(datetime.now(), FILENAME_FRMT))


def main():
    if not os.path.exists(BACKUPS_DIR):
        os.mkdir(BACKUPS_DIR)

    while True:
        backup_db()
        time.sleep(BACKUP_FREQ)

if __name__ == "__main__":
    print("Ctrl-C to kill")
    main()
