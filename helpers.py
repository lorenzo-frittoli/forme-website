from flask import redirect, render_template, session, g, url_for, send_file, Response
from functools import wraps
import qrcode
from io import BytesIO
import json
import unicodedata
import re
import string
from datetime import datetime
import random
import sqlite3

from constants import *


def apology(message="Invalid http request", code=400):
    """Render message as an apology to user."""
    return render_template("apology.html", message=message), code


def login_required(f):
    """
    Decorate routes to require login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")

        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    """Decorate to require admin login. Requires login with `@login_required`.

    Args:
        f (_type_): function to decorate

    Returns:
        _type_: decorated function
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if g.user_email not in ADMIN_EMAILS:
            return apology("Auth failed", 403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def staff_required(f):
    """Decorate to require staff account. Requires login with `@login_required`.

    Args:
        f (_type_): function to decorate

    Returns:
        _type_: decorated function
    """
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if g.user_type != "staff":
            return apology("Auth failed", 403)
        
        return f(*args, **kwargs)
    
    return decorated_function


def activity_already_booked(user_id: int, activity_id: int, con: sqlite3.Connection) -> bool:
    """Checks wether a course has been booked already by that student.

    Args:
        user_di (int): id of the user
        activity_id (int): id of the activity

    Returns:
        bool: True if already booked, False if not
    """
    
    return bool(
        con.execute("SELECT activity_id FROM registrations WHERE user_id = ? AND activity_id = ?;", (user_id, activity_id)).fetchall()
    )


def slot_already_booked(user_id: int, day: int, module_start: int, module_end: int, con: sqlite3.Connection) -> bool:
    """Checks if a slot (a day/timespan couple) is already occupied by the user

    Args:
        user_id (int): id of the user
        day (str): day
        timespan (str): timespan (will be decomposed using decompose_timespan)

    Returns:
        bool: True if booked, False if not
    """
    # Searches for ranges intersecting (module_start, module_end)
    
    return bool(
        con.execute("SELECT activity_id FROM registrations WHERE user_id = ? AND day = ? AND module_end >= ? AND module_start <= ?;", (user_id, day, module_start, module_end)).fetchall()
    )


def make_registration(user_id: int, activity_id: int, day: int, module: int, user_type: str, con: sqlite3.Connection):
    """Add a registration to the database

    Args:
        user_id (int): id of the user
        activity_id (int): id of the activity
        day (int): day
        module (int): if length = 2, module 0 = timespans 0, 1. Compute with: timespan // length
        user_type (str)
        con (sqlite3.Connection)
        do_commit (bool): if the transaction should be immediately committed. Defaults to True

    Raises:
        ValueError: Bookings are closed
        ValueError: Activity already booked by the user
        ValueError: Module out of bounds
        ValueError: Occupied slot
        ValueError: Activity not available
    """
    if day < 0 or day >= len(DAYS) or user_type not in PERMISSIONS[day]:
        raise ValueError("Invalid day")
    
    length = con.execute("SELECT length FROM activities WHERE id = ?;", (activity_id,)).fetchone()
    if length is None:
        raise ValueError("Invalid activity id")
    
    length = length[0]
    
    # Check if the user has already booked this activity
    if activity_already_booked(user_id, activity_id, con):
        raise ValueError("Activity already booked")

    # Check if the module is valid
    module_start = module * length
    module_end = module_start + length - 1

    if module_start < 0 or module_end >= len(TIMESPANS):
        raise ValueError("Module out of bounds")

    # Check if the user has already booked this day-timespan combo
    if slot_already_booked(user_id, day, module_start, module_end, con):
        raise ValueError("Occupied slot")
    
    # Update availability (raises ValueError if the availability is already 0)
    update_availability(activity_id, day, module, -1, con)
    
    # Update registrations
    con.execute("INSERT INTO registrations (user_id, activity_id, day, module_start, module_end) VALUES (?, ?, ?, ?, ?);", (user_id, activity_id, day, module_start, module_end))


def update_availability(activity_id: int, day: int, module: int, amount: int, con: sqlite3.Connection) -> None:
    """Updates the availability

    Args:
        activity_id (int): id of the activity
        day (int): day to update
        module (int): if length = 2, module 0 = timespans 0, 1. Compute with: timespan // length
        amount (int): amount to change the availability by
        con (sqlite3.Connection)
        do_commit (bool): if the transaction should be immediately committed. Defaults to True
    
    Raises:
        ValueError if the availability is already 0.
    """
    # Load availability
    result = con.execute("SELECT availability FROM activities WHERE id = ?;", (activity_id,)).fetchone()
    if not result:
        raise ValueError()

    availability = json.loads(result[0])

    # Check if we are removing bookings from a cancelled activity (availability[][] = -1)
    if availability[day][module] == -1 and amount > 0:
        # keep the availability to -1 for a cancelled activity
        return

    # Modify availability
    availability[day][module] += amount
    if availability[day][module] < 0:
        raise ValueError()
    availability = json.dumps(availability)
    
    # Update availability
    con.execute("UPDATE activities SET availability = ? WHERE id = ?;", (availability, activity_id))


def normalize_text(text: str):
    """Remove accents and use lower case"""
    return unicodedata.normalize('NFKD', text).encode('ASCII', 'ignore').decode().lower()


def fmt_timespan(start: int, end: int):
    """Return the formatted text for the range [start, end]"""
    return TIMESPANS[start][0] + ' - ' + TIMESPANS[end][1]


def fmt_activity_booking(activity_id: int, con: sqlite3.Connection) -> str:
    span = con.execute("SELECT day, module_start, module_end FROM registrations WHERE user_id = ? AND activity_id = ?;", (g.user_id, activity_id)).fetchone()

    if span is None:
        return ""
    else:
        return fmt_timespan(span[1], span[2]) + " del " + DAYS[span[0]]


def qr_code_for(url: str) -> Response:
    """
    Args:
        url (str): link to create a qr code for.
    """
    img_io = BytesIO()
    qrcode.make(url).save(img_io, "PNG")
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")


def generate_schedule(user_id: int, user_type: str, con: sqlite3.Connection):
    """Generate the schedule for the me page."""

    user_registrations = con.execute(
        "SELECT activity_id, day, module_start, module_end FROM registrations WHERE user_id = ?;",
        (user_id, )
    ).fetchall()

    # Make empty schedule
    schedule = {day: {timespan: ("", None) for timespan in TIMESPANS_TEXT}
                for i, day in enumerate(DAYS) if user_type in PERMISSIONS[i]}
    
    # Fill with known data
    for activity_id, day, module_start, module_end in user_registrations:
        for timespan in range(module_start, module_end + 1):
            assert DAYS[day] in schedule
            assert schedule[DAYS[day]][TIMESPANS_TEXT[timespan]] == ("", None)
            link = url_for(".activity_page", id=activity_id)
            schedule[DAYS[day]][TIMESPANS_TEXT[timespan]] = (get_activity(activity_id)["title"], link)

    return schedule


def generate_password(length: int = GENERATED_PASSWORD_LENGTH) -> str:
    """Generates a password

    Args:
        length (int, optional): length of the password. Configurable in `constants.py`. Defaults to GENERATED_PASSWORD_LENGTH.

    Returns:
        str: password
    """
    letters = string.ascii_letters + string.digits
    
    password = "".join(random.choices(letters, k=length))
    
    return password


def make_backup(dir: str) -> str:
    """Add backup to the rolling storage

    Args:
        dir (str): backup directory
    """
    if not os.path.exists(dir):
        os.makedirs(dir)
    
    FILENAME_FRMT = DATABASE.replace(".", "_%Y-%m-%d_%H-%M-%S.")
    
    # Delete the old backups
    backups = [(datetime.strptime(backup, FILENAME_FRMT), backup) for backup in os.listdir(dir)]
    backups.sort()
    for backup in backups[:1-MAX_BACKUPS]:
        os.remove(dir + DIR_SEP + backup[1])

    # Lock the database and save the new backup
    filename = dir + DIR_SEP + datetime.strftime(datetime.now(), FILENAME_FRMT)
    con_backup = sqlite3.connect(filename)
    con_live = sqlite3.connect(DATABASE)
    con_live.backup(con_backup)
    con_live.close()
    con_backup.commit()
    con_backup.close()

    return filename


def valid_class(_class: str) -> bool:
    return len(_class) == 2 and _class[0] in ALLOWED_CLASSES[0] and _class[1] in ALLOWED_CLASSES[1]


def valid_email(email: str) -> bool:
    return re.match(EMAIL_REGEX, email) is not None


def create_availability(capacity: int, length: int) -> list[list[int]]:
    return [[capacity for _ in range(0, len(TIMESPANS) - length + 1, length)] for _ in DAYS]
