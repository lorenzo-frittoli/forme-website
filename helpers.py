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
    cur.execute("SELECT activity_id FROM registrations WHERE user_id = ? AND activity_id = ?", (user_id, activity_id))
    
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
