import sqlite3

from constants import *

# File where the make database command is stored 
MAKE_DATABASE_COMMAND_FILE = "make_database.sql"

def main() -> None:
    """Drops all current tables and sets up new ones in the database"""
    # Initialize sqlite3
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Drop all tables
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cur.fetchall()
    
    cur.executemany("DROP TABLE IF EXISTS ?;", tables)
    
    # Init the database
    qry = open(MAKE_DATABASE_COMMAND_FILE, "r")

    cur.execute(qry)
    con.commit()

    # Close sqlite3 (optional)
    cur.close()
    con.close()
    
    
if __name__ == '__main__':
    main()