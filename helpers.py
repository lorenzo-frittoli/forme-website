# import csv
# import datetime
# import pytz
# import requests
# import subprocess
# import urllib
# import uuid

from flask import redirect, render_template, session, g, url_for
from functools import wraps
import sqlite3
import json
from typing import Union
import random

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

        cur = g.con.cursor()
        id = cur.execute("SELECT id FROM users WHERE id = ?;", (session.get("user_id"), )).fetchall()
        cur.close()

        if not id:
            return redirect("/login")
        
        return f(*args, **kwargs)
    return decorated_function


def activity_already_booked(user_id: int, activity_id: int) -> bool:
    """Checks wether a course has been booked already by that student.

    Args:
        user_di (int): id of the user
        activity_id (int): id of the activity

    Returns:
        bool: True if already booked, False if not
    """
    
    cur = g.con.cursor()
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
    cur = g.con.cursor()
    cur.execute(f"SELECT activity_id FROM registrations WHERE user_id = ? AND day = ? AND module_end >= ? AND module_start <= ?;", (user_id, day, module_start, module_end))
    
    return bool(cur.fetchall())


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
    
    cur = g.con.cursor()

    length = cur.execute("SELECT length FROM activities WHERE id = ?;", (activity_id,)).fetchone()[0]
    if length is None:
        raise ValueError("Invalid activity id")
    
    # Check if the user has already booked this activity  
    if activity_already_booked(user_id, activity_id):
        raise ValueError("Activity already booked")

    # Check if the module is valid
    module_start = module * length
    module_end = module_start + length - 1

    if module_start < 0 or module_end >= len(TIMESPANS):
        raise ValueError("Module out of bounds")

    # Check if the user has already booked this day-timespan combo
    if slot_already_booked(user_id, day, module_start, module_end):
        raise ValueError("Occupied slot")
    
    # Update availability
    update_availability(activity_id, day, module, -1)
    
    # Update registrations
    cur.execute("INSERT INTO registrations (user_id, activity_id, day, module_start, module_end) VALUES (?, ?, ?, ?, ?);", (user_id, activity_id, day, module_start, module_end))
    g.con.commit()
    
    # Close cursor
    cur.close()


def update_availability(activity_id: int, day: int, module: int, amount: int) -> None:
    """Updates the availability

    Args:
        activity_id (int): id of the activity
        day (int): day to update
        module (int): if length = 2, module 0 = timespans 0, 1. Compute with: timespan // lenght
        amount (int): amount to change the availability by
    """
    # SQL setup
    cur = g.con.cursor()
    
    # Load availability
    availability = cur.execute("SELECT availability FROM activities WHERE id = ?", (activity_id,)).fetchone()[0]
    availability = json.loads(availability)
    
    # Modify availability
    availability[day][module] += amount
    availability = json.dumps(availability)
    
    # Update availability
    cur.execute("UPDATE activities SET availability = ? WHERE id = ?;", (availability, activity_id))  
    g.con.commit()
    
    # SQL close
    cur.close()
    
    
def get_students_from_file(filename: str) -> list[dict]:
    """RETURNS DUMMY OUTPUT. Returns student data from a file.
    
    Args:
        filename (str): name of the file where the data is stored


    Returns:
        list[dict]: list of students data: [{name, surname, class, email}, ...]
    """
    dummy_output = [
        {"name": "Giovanni",
         "surname": "Giorgio",
         "class": "5A",
         "email": "giovanni.giorgio@liceocassini.eu"},
        
        {"name": "Nicola",
         "surname": "Gay",
         "class": "5J",
         "email": "nicola.gay@liceocassini.eu"}
    ]
    
    return dummy_output


def generate_password(length: int = GENERATED_PASSWORD_LENGTH) -> str:
    """Generates a password

    Args:
        length (int, optional): length of the password. Configurable in `constants.py`. Defaults to GENERATED_PASSWORD_LENGTH.

    Returns:
        str: password
    """
    lowercase = "abcdefghijklmnopqrstuvwxyz"
    uppercase = lowercase.upper()
    numbers = "0123456789"
    letters = lowercase + uppercase + numbers
    
    password = "".join(random.choices(letters, k=length))
    
    return password
    
    
def get_activities_from_file(filename: str) -> list[dict]:
    """RETURNS DUMMY OUTPUT. Returns student data from a file

    Args:
        filename (str): name of the file where the data is stored

    Returns:
        list[dict]: list of activity data: [{title, description, type, length, availability}]
    """
    titles = ("Title 1", "Title 2")
    types = ("Type 1", "Type 2")
    lengths = (1, 2)
    classrooms = ("4.2", "6.9")
    description = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Maecenas volutpat blandit aliquam etiam erat velit scelerisque in. Praesent semper feugiat nibh sed pulvinar proin. Condimentum vitae sapien pellentesque habitant. Mi in nulla posuere sollicitudin aliquam. Commodo viverra maecenas accumsan lacus vel facilisis. Etiam non quam lacus suspendisse faucibus. Eu non diam phasellus vestibulum lorem sed risus ultricies tristique. Egestas pretium aenean pharetra magna ac placerat. Sed velit dignissim sodales ut eu sem integer vitae justo. Facilisi etiam dignissim diam quis enim lobortis scelerisque fermentum dui. In arcu cursus euismod quis.
    Lorem sed risus ultricies tristique nulla. Rhoncus urna neque viverra justo nec ultrices dui sapien. Venenatis urna cursus eget nunc. Tristique sollicitudin nibh sit amet commodo nulla facilisi. Rhoncus aenean vel elit scelerisque. Tempor commodo ullamcorper a lacus vestibulum sed arcu. In hendrerit gravida rutrum quisque non tellus orci ac auctor. Eget felis eget nunc lobortis mattis. Turpis nunc eget lorem dolor sed viverra ipsum nunc. Congue nisi vitae suscipit tellus. Pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Rhoncus aenean vel elit scelerisque. Fermentum odio eu feugiat pretium nibh ipsum consequat nisl vel. Ut sem nulla pharetra diam sit. Natoque penatibus et magnis dis parturient. Lacus sed turpis tincidunt id aliquet risus feugiat in ante. Suspendisse in est ante in nibh mauris cursus. Pulvinar neque laoreet suspendisse interdum. Sollicitudin tempor id eu nisl nunc mi ipsum.
    Imperdiet dui accumsan sit amet nulla facilisi. Tellus elementum sagittis vitae et leo duis ut diam quam. Quam viverra orci sagittis eu volutpat. Nunc sed id semper risus in hendrerit. Fames ac turpis egestas maecenas pharetra convallis posuere. Ultrices vitae auctor eu augue ut. Amet nisl suscipit adipiscing bibendum est ultricies. Habitasse platea dictumst quisque sagittis purus sit. Lobortis mattis aliquam faucibus purus in. Viverra tellus in hac habitasse. Eu scelerisque felis imperdiet proin fermentum leo. Bibendum ut tristique et egestas quis ipsum suspendisse. Sit amet consectetur adipiscing elit pellentesque. Feugiat vivamus at augue eget arcu dictum varius duis at. Duis at tellus at urna condimentum mattis pellentesque id nibh. Morbi non arcu risus quis varius quam. Fringilla urna porttitor rhoncus dolor purus. Nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit. Pellentesque eu tincidunt tortor aliquam nulla facilisi cras fermentum odio. Quis commodo odio aenean sed.
    """
    data = [
        {
            "title": tit,
            "description": description,
            "type": typ,
            "length": l,
            "classroom": c,
            "availability": json.dumps([[20 for _ in range(0, len(TIMESPANS) - l + 1, l)] for _ in DAYS])
        }
    for tit, typ, l, c in zip(titles, types, lengths, classrooms)]
    
    return data
