import time

from constants import AUTO_BACKUPS_DIR, BACKUP_FREQ
from manage_helpers import make_backup


def main():
    """Automatically creates backups of the db
    """        
    while True:
        make_backup(AUTO_BACKUPS_DIR)
        time.sleep(BACKUP_FREQ)


if __name__ == "__main__":
    print("Ctrl-C to kill")
    main()
