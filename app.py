import sqlite3
from flask import Flask, redirect, render_template, request, session, g, Response, abort, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import json
import re
from datetime import datetime
from itertools import groupby

from helpers import apology, login_required, admin_required, staff_required, make_registration, update_availability, get_image_path, fmt_activity_booking, qr_code_for, generate_schedule, fmt_timespan
from manage_helpers import generate_password
import admin
from constants import *

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
# I have no idea what this means just roll with it
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.before_request
def before_request():
    if "/static/" not in request.path:
        # Open the connection to the database
        g.con = sqlite3.connect(DATABASE)

        if session.get("user_id") is None:
            return

        query_result = g.con.execute("SELECT type, name, surname, email, can_book, theme FROM users WHERE id = ?;", (session["user_id"], )).fetchone()

        # If the user has been deleted (this functionality is not implemented, this should not happen)
        if not query_result:
            session.clear()
            return

        # Save all user info
        g.user_type, g.user_name, g.user_surname, g.user_email , g.can_book, g.user_theme = query_result
        g.user_id = session["user_id"]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""

    if "/static/" in request.path:
        # static file
        response.headers["Cache-Control"] = "public, max-age: 2592000"

    else:
        # Close the connection to the database
        g.con.close()
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Expires"] = 0
        response.headers["Pragma"] = "no-cache"

    return response


@app.route("/")
@app.route("/index.html")
def index_page():
    """Homepage"""
    return render_template("index.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by getting the link)
    if request.method == "GET":
        return render_template("login.html")
    
    # User reached route via POST (as by submitting a form via POST)
    email = request.form.get("email")

    if not email:
        return apology("email non valida", 400)

    email = email.lower()

    # Ensure password was submitted
    if not request.form.get("password"):
        return apology("password non valida", 400)

    # Query db for user info
    # query_result is like [(id, pw_hash)]
    query_result = g.con.execute("SELECT id, hash FROM users WHERE email = ?;", (email, )).fetchone()

    # If there is no user saved with the provided email
    if not query_result:
        session.clear()
        return apology("email e/o password invalidi", 400)

    # No need to fully update the session: it will be updated after the redirect
    session["user_id"], pw_hash = query_result

    # Check password against hash
    if not check_password_hash(pw_hash, request.form["password"]):
        session.clear()
        return apology("email e/o password invalidi", 400)

    # Redirect user to home page
    return redirect("/")


@app.route("/logout")
def logout_page():
    """Log user out"""

    # Forget any user_id
    session.clear()

    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register_page():
    """Register user"""

    # If called with GET (loaded the page/clicked link)
    if request.method == "GET":
        # Render the page
        return render_template("register.html")
    
    # If called with POST (submitted the form)
    # Get form data
    name = request.form.get("name")
    surname = request.form.get("surname")
    email = request.form.get("email")
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")

    # Check that the form was filled correctly
    # Checks the name filed
    if not name or len(name) > MAX_FIELD_LENGTH:
        return apology("Nome non valido", 400)

    # Checks the surname field
    if not surname or len(surname) > MAX_FIELD_LENGTH:
        return apology("Cognome non valido", 400)
    
    # Checks the email field
    if not email:
        return apology("Email non valida", 400)

    email = email.lower().strip() # Some mobile browsers insert spaces for no reason
    if len(email) > MAX_FIELD_LENGTH or not re.match(EMAIL_REGEX, email):
        return apology("Email non valida", 400)
    
    # Checks the password field
    if not password or len(password) > MAX_FIELD_LENGTH:
        return apology("Password non valida", 400)
    
    # Checks that password and confirmation match
    if password != confirmation:
        return apology("Password e conferma non coincidono", 400)

    # Check if the email is already taken
    # g.con.execute returns a tuple with the result or None etc
    found = g.con.execute("SELECT 1 FROM users WHERE email = ?;", (email, )).fetchone()

    if found:
        return apology("Email già registrata", 400)

    # Save the new user & commit
    g.con.execute("INSERT INTO users (email, hash, name, surname, type, verification_code) VALUES (?, ?, ?, ?, ?, ?);",
                (email, generate_password_hash(password, method=GENERATE_PASSWORD_METHOD), name, surname, "guest", generate_password(20)))
    g.con.commit()

    # Redirect to the homepage
    return redirect("/login")


@app.route("/activities", methods=["GET"])
@login_required
def activities_page():
    """List of all activities"""

    # Query DB for id, title, type of every activity in the form list[tuple[id: int, title: str, type: str]]
    query_output = g.con.execute("SELECT id, title, type, description, length, image FROM activities;").fetchall()
    
    # If no activity is loaded yet, return apology
    if not query_output:
        return apology("Nessuna attività disponibile al momento", 200)
    
    # Make list of tuples into list of dicts for easy acces with jinja
    activities_list = [{"id": activity_id,
                        "title": activity_title,
                        "type": activity_type,
                        "description": activity_description,
                        "length": activity_length,
                        "booked": fmt_activity_booking(activity_id, g.con),
                        "image": get_image_path(image_name)
                        } for activity_id, activity_title, activity_type, activity_description, activity_length, image_name in query_output]

    return render_template("activities.html", activities=activities_list)


@app.route("/activity", methods=["GET", "POST"])
@login_required
def activity_page():
    """Activity page w/ details"""
    try:
        activity_id = int(request.args["id"])
        
    except (KeyError, ValueError):
        return apology("Invalid http request")

    # Method is GET
    if request.method == "GET":        
        # Query the database
        query_result = g.con.execute("SELECT title, description, type, length, classroom, image, availability FROM activities WHERE id = ?;", [activity_id,]).fetchone()

        if query_result is None:
            return apology("Invalid http request")

        activity_title, activity_description, activity_type, activity_length, activity_classroom, activity_image, activity_availability = query_result

        activity_timespans = tuple(
            (i//activity_length, fmt_timespan(i, i + activity_length - 1))
            for i in range(0, len(TIMESPANS)-activity_length+1, activity_length)
        )

        activity_dict = {
            "title": activity_title,
            "description": activity_description,
            "type": activity_type,
            "classroom": activity_classroom,
            "image": get_image_path(activity_image),
        }

        # JSON string -> list[list[remaining by time] by day]
        activity_availability = json.loads(activity_availability)

        if g.user_type == "staff":
            today = datetime.today().strftime("%d/%m")
            activity_days = list(enumerate(DAYS))

            try:
                day_index = DAYS.index(today)
            except ValueError:
                # No registrations to be shown for today
                return render_template(
                    "activity_staff.html",
                    id=activity_id,
                    activity=activity_dict,
                    days=activity_days,
                    timespans=activity_timespans,
                    availability=activity_availability,
                    has_bookings=False
                )

            query_result = g.con.execute("SELECT name, surname, class, module_start, module_end FROM users JOIN registrations ON users.id = registrations.user_id WHERE activity_id = ? AND day = ? ORDER BY type, surname || name;", (activity_id, day_index)).fetchall()
            
            def parse_registration(booking: tuple) -> tuple:
                if booking[2]:
                    return booking[0], booking[2], int(booking[3]), int(booking[4])
                else:
                    return booking[1] + " " + booking[0], "Esterno", int(booking[3]), int(booking[4])
            
            bookings = list(map(parse_registration, query_result))

            # group the registrations by time
            bookings = sorted(bookings, key=lambda reg: reg[2:4]) # required by groupby
            bookings_by_time = {fmt_timespan(key[0], key[1]): tuple(map(lambda reg: reg[0:2], group)) for key, group in groupby(bookings, lambda reg: reg[2:4])}

            return render_template(
                "activity_staff.html",
                id=activity_id,
                activity=activity_dict,
                days=activity_days,
                timespans=activity_timespans,
                availability=activity_availability,
                has_bookings=True,
                bookings=bookings_by_time
            )
            
        
        # g.user_type != "staff"
        user_registrations = g.con.execute("SELECT day, module_start, module_end FROM registrations WHERE user_id = ?", (g.user_id, )).fetchall()

        # Details of the activity
        activity_dict["booked"] = fmt_activity_booking(activity_id, g.con)

        activity_availability = [av for i, av in enumerate(activity_availability) if g.user_type in PERMISSIONS[i]]

        activity_days = tuple((i, day) for i, day in enumerate(DAYS) if g.user_type in PERMISSIONS[i])
        
        user_free = [[True for _ in TIMESPANS] for _ in DAYS]

        # Fill with known data
        for booking_day, booking_module_start, booking_module_end in user_registrations:
            for booking_timespan in range(booking_module_start, booking_module_end + 1):
                assert user_free[booking_day][booking_timespan]
                user_free[booking_day][booking_timespan] = False

        user_free = [[all(day_free[module_start:module_start+activity_length])
                     for module_start in range(0, len(TIMESPANS)-activity_length+1, activity_length)]
                     for i, day_free in enumerate(user_free) if g.user_type in PERMISSIONS[i]]
        
        return render_template(
            "activity.html",
            id=activity_id,
            activity=activity_dict,
            days=activity_days,
            timespans=activity_timespans,
            availability=activity_availability,
            user_free=user_free,
            can_book=g.can_book
        )

    # Method is POST
    
    # If booking
    if "booking-button" in request.form:
        # Fetch data
        try:
            day = int(request.form['day-button'])
            module = int(request.form["timespan-button"])
            
        except (TypeError, ValueError):
            return apology("Invalid http request")

        # Make registration
        try:
            make_registration(g.user_id, activity_id, day, module, g.user_type, g.con)
        
        except ValueError:
            return apology("Prenotazione non valida")

    # If unbooking
    elif "unbooking-button" in request.form:
        registration = g.con.execute("SELECT day, module_start FROM registrations WHERE user_id = ? AND activity_id = ?;", (g.user_id, activity_id)).fetchone()
        length = g.con.execute("SELECT length FROM activities WHERE id = ?;", (activity_id, )).fetchone()
        
        if None in (registration, length):
            return apology("Invalid http request")
        
        length = length[0]
        day, module_start = registration
        module = module_start // length

        # Update availability
        update_availability(activity_id, day, module, 1, g.con)
        
        # Remove registration
        g.con.execute("DELETE FROM registrations WHERE user_id = ? AND activity_id = ?;", (g.user_id, activity_id))
        g.con.commit()
        
    # Wildcard (error)
    else:
        return apology("Invalid http request")
    
    return redirect("/me")


@app.route("/me")
@login_required
def me_page():
    """Me page w/ your bookings"""

    return render_template(
        "me.html",
        schedule=generate_schedule(g.user_id, g.user_type, g.con),
        user_name = g.user_name,
        user_surname = g.user_surname,
        user_email = g.user_email,
        user_type=g.user_type
    )


@app.route("/privacy")
def privacy_page():
    """Cookie policy and privacy policy"""
    return render_template("privacy.html")


@app.route("/codice_verifica")
@login_required
def qr_code_page():
    return render_template("verification.html")


@app.route("/qr_code.png")
@login_required
def qr_code():
    """Generate the qr code for verification
    """
    result = g.con.execute("SELECT verification_code FROM users WHERE id = ?", (g.user_id, )).fetchone()
    if not result:
        raise RuntimeError(f"User not found in qr_code: user_id {g.user_id}, email {g.user_email}")

    return qr_code_for(LINK + url_for("verification_page", verification_code=result[0]))



@app.route("/redirect_verifica")
def verification_page():
    try:
        verification_code = request.args["verification_code"]

    except (KeyError, ValueError):
        return apology("Invalid http request")

    result = g.con.execute("SELECT id, type, name, surname, email FROM users WHERE verification_code = ?", (verification_code, )).fetchone()
    if not result:
        return apology("Utente non trovato.")

    if result[1] == "staff":
        return apology("Account staff.")

    return render_template(
        "me.html",
        schedule=generate_schedule(int(result[0]), result[1], g.con),
        user_type="impersonate", # This way the warning banner doesn't show up
        user_name = result[2],
        user_surname = result[3],
        user_email = result[4]
    )

@app.route("/user_search", methods=["GET", "POST"])
@staff_required
def search_page():
    if request.method == "GET":
        return render_template("search_page.html")

    # Method is POST
    query = request.form.get("query")

    # Stop the user from dumping the database abusing LIKE clauses
    if query is None or '%' in query or '_' in query or len(query) > 50:
        return apology("Invalid http request", 400)

    query = query.split()

    if max(map(len, query), default=0) < 2:
        return apology("Inserire almeno 2 caratteri per la ricerca")

    search_sql = "(name LIKE ? COLLATE NOCASE OR surname LIKE ? COLLATE NOCASE OR email LIKE ? COLLATE NOCASE OR class = ? COLLATE NOCASE)"
    sql_query = "SELECT surname, name, class, email, verification_code FROM users WHERE " + " AND ".join([search_sql] * len(query)) + " ORDER BY surname || name;"

    results = g.con.execute(
        sql_query,
        sum((('%'+q+'%', '%'+q+'%', '%'+q+'%', q) for q in query), start=tuple())
    ).fetchall()

    def parse_row(row: tuple) -> tuple:
        return (' '.join(row[:2]), url_for("verification_page", verification_code=row[4])), row[2] or "esterno", row[3]

    results = tuple(map(parse_row, results))

    return render_template(
        "search_page.html",
        results=results
    )


@app.route("/set_theme", methods=["POST"])
@login_required
def change_theme():
    """Change theme for this user"""

    new_theme = request.args.get("theme")

    if new_theme not in ("light", "dark"):
        return apology("Invalid http request, 400")

    g.user_theme = new_theme
    g.con.execute("UPDATE users SET theme = ? WHERE id = ?;", (new_theme, g.user_id))
    g.con.commit()

    return "", 204


@app.route("/admin", methods=["GET", "POST"])
@admin_required
def admin_page():
    """Admin page"""
    # On get
    if request.method == "GET":
        return render_template("admin_area.html", commands=admin.command_annotations)
    
    # On post
    command = request.form.get("command")
    password = request.form.get("password")
    if command is None:
        return apology("", 400)

    # Authentication page
    if password is None:
        return render_template("admin_auth.html", command=dict(request.form))

    # Execute the command
    if not check_password_hash(ADMIN_PASSWORD, password):
        return apology("Auth failed", 403)
    
    result = admin.execute(command)
    
    # Different commands return different types of data
    if isinstance(result, Response):
        return result

    assert len(result) == 2
    assert isinstance(result[0], str)
    assert isinstance(result[1], int)
    return render_template("admin_area.html", commands=admin.command_annotations, response=result[0].split("\n")), result[1]
