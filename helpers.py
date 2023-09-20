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
        return f(*args, **kwargs)
    return decorated_function


def activity_already_booked(user_id: int|str, activity_id: int|str) -> bool:
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
    cur.execute("SELECT activity_id FROM registrations WHERE user_id = ?", (user_id,))
    
    # Fetchall returns list[tuple[id,]]
    if (activity_id,) in cur.fetchall():
        return True
    
    return False


def slot_already_booked(user_id: int, day: str, timespan: str) -> bool:
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
    
    relevant_timespans = tuple(decompose_timespan(timespan))    
    cur.execute(f"SELECT activity_id FROM registrations WHERE user_id = ? AND day = ? AND timespan IN {relevant_timespans};", (user_id, day))
    
    if not cur.fetchall():
        return False
    
    return True


def decompose_timespan(timespan: str) -> list[str]:
    """Given a timespan, it maps it to the provided timespans list.
    eg:
        with TIMESPANS = ["09:00-10:00", "11:00-12:00", "12:00-13:00"]
        decompose_timespan("09:00-12:00") -> ["09:00-10:00", "11:00-12:00]

    Args:
        timespan (str): timespan to decompose

    Raises:
        ValueError: the timespan is not valid

    Returns:
        list[str]: list of timespans that start at the start of the timespan and end at the end of the timespan
    """
    split_timespans = list(map(lambda t: t.split("-"), TIMESPANS))
    starts = [t[0] for t in split_timespans]
    ends = [t[1] for t in split_timespans]
    
    start_end = timespan.split("-")
    
    if len(start_end) != 2:
        raise ValueError(f"Invalid timespan: {timespan}")
    
    start, end = start_end
    start_index = starts.index(start)
    end_index = ends.index(end)
    
    return TIMESPANS[start_index : end_index + 1]