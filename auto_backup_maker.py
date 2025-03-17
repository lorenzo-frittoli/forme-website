from constants import TIMED_BACKUPS_DIR
from helpers import make_backup

# This script is meant to be run each day as a scheduled task.

if __name__ == "__main__":
    make_backup(TIMED_BACKUPS_DIR)
