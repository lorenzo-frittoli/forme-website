# import csv
# import datetime
# import pytz
# import requests
# import subprocess
# import urllib
# import uuid

from flask import redirect, render_template, session
from functools import wraps
import sqlite3
import json
from typing import Union

from constants import *

def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")

        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        id = cur.execute("SELECT id FROM users WHERE id = ?;", (session.get("user_id"), )).fetchall()
        cur.close()
        con.close()

        if not id:
            return redirect("/login")
        
        return f(*args, **kwargs)
    return decorated_function


def activity_already_booked(user_id: Union[int, str], activity_id: Union[int, str]) -> bool:
    """Checks wether a course has been booked already by that student.

    Args:
        user_di (int): id of the user
        activity_id (int): id of the activity

    Returns:
        bool: True if already booked, False if not
    """
    user_id = int(user_id)
    activity_id = int(activity_id)
    
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    cur.execute("SELECT activity_id FROM registrations WHERE user_id = ? AND activity_id = ?;", (user_id, activity_id))
    
    return bool(cur.fetchall())


def slot_already_booked(user_id: int, day: str, module_start: int, module_end: int) -> bool:
    """Checks if a slot (a day/timespan couple) is already occupied by the user

    Args:
        user_id (int): id of the user
        day (str): day
        timespan (str): timespan (will be decomposed using decompose_timespan)

    Returns:
        bool: True if booked, False if not
    """
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    cur.execute(f"SELECT activity_id FROM registrations WHERE user_id = ? AND day = ? AND module_end >= ? AND module_start <= ?;", (user_id, day, module_start, module_end))
    
    return bool(cur.fetchall())


def fetch_schedule(user_id: int, user_type: int):
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    # Fetch all user registrations -> list[tuple[title, day, timespan]]
    result = """
    SELECT activities.title, registrations.day, registrations.module_start, registrations.module_end
        FROM registrations JOIN
        activities ON
            registrations.activity_id = activities.id
        WHERE user_id = ?;
    """
    cur.execute(result, (user_id,))
    query_results = cur.fetchall()
    
    # Make empty schedule
    schedule = {day: {timespan: ""
                      for timespan in TIMESPANS_TEXT}
                for i, day in enumerate(DAYS)
                if user_type in PERMISSIONS[i]}
        
    # Fill with known data
    for title, day, module_start, module_end in query_results:
        for module in range(module_start, module_end+1):
            assert schedule[DAYS[day]][TIMESPANS_TEXT[module]] == ""
            schedule[DAYS[day]][TIMESPANS_TEXT[module]] = title

    # Close connection to db
    cur.close()
    con.close()

    # Return
    return schedule


def make_registration(user_id: int, activity_id: int, day: int, module: int):
    """Add a registration to the database

    Args:
        user_id (int): id of the user
        activity_id (int): id of the activity
        day (int): day
        module (int): if length = 2, module 0 = timespans 0, 1. Compute with: timespan // lenght

    Raises:
        ValueError: Activity already booked by the user
        ValueError: Module out of bounds
        ValueError: Occupied slot
    """
    if day < 0 or day >= len(DAYS) or session["user_type"] not in PERMISSIONS[day]:
        raise ValueError("Invalid day")
    
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    query_result = cur.execute("SELECT availability, length FROM activities WHERE id = ?;", (activity_id,)).fetchone()
    if query_result is None:
        cur.close()
        con.close()
        raise ValueError("Invalid activity id")

    availability, length = query_result
    
    # Check if the user has already booked this activity  
    if activity_already_booked(user_id, activity_id):
        raise ValueError("Activity already booked")

    module_start = module * length
    module_end = module_start + length - 1

    if module_start < 0 or module_end >= len(TIMESPANS):
        raise ValueError("Module out of bounds")

    # Check if the user has already booked this day-timespan combo
    if slot_already_booked(user_id, day, module_start, module_end):
        raise ValueError("Occupied slot")
    
    # Update availability
    availability = json.loads(availability)
    availability[day][module] -= 1
    availability = json.dumps(availability)
    cur.execute("UPDATE activities SET availability = ? WHERE id = ?;", (availability, activity_id))    
    
    # Update registrations
    cur.execute("INSERT INTO registrations (user_id, activity_id, day, module_start, module_end) VALUES (?, ?, ?, ?, ?);", (user_id, activity_id, day, module_start, module_end))
    
    # Commit and close connection
    con.commit()
    cur.close()
    con.close()
