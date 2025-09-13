import sqlite3
from flask import Flask, redirect, render_template, request, session, g, Response, url_for
from flask_session import Session
from werkzeug.security import check_password_hash
import json
from itertools import groupby

from helpers import *
import admin
from constants import *

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
# I have no idea what this means just roll with it
app.config["SESSION_PERMANENT"] = True
app.config["SESSION_TYPE"] = "filesystem"
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True
Session(app)

@app.before_request
def before_request():
    if not request.path.startswith("/static/"):
        # Open the connection to the database
        g.con = sqlite3.connect(DATABASE)

        if session.get("user_id") is None:
            return

        query_result = g.con.execute("SELECT type, full_name, email, can_book, theme FROM users WHERE id = ?;", (session["user_id"], )).fetchone()

        # If the user has been deleted (this functionality is not implemented, this should not happen)
        if not query_result:
            session.clear()
            return

        # Save all user info
        g.user_type, g.user_full_name, g.user_email , g.can_book, g.user_theme = query_result
        g.user_id = session["user_id"]


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""

    if request.path.startswith("/static/"):
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
def index_page():
    """Homepage"""
    return render_template("index.html")


@app.route("/logout")
def logout_page():
    """Log user out"""

    # Forget any user_id
    session.clear()

    return redirect("/")


@app.route("/activities", methods=["GET"])
def activities_page():
    """List of all activities"""

    activities = get_activities()

    # If no activity is loaded yet, return apology
    if not activities:
        return apology("Nessuna attività disponibile al momento", 200)

    for activity in activities:
        if "user_id" in session:
            activity["booked"] = fmt_activity_booking(activity["id"], g.con)

    return render_template("activities.html", activities=activities)


@app.route("/activity", methods=["GET", "POST"])
def activity_page():
    """Activity page w/ details"""
    try:
        activity_id = int(request.args["id"])
        # Check that the activity exists
        activity_dict = get_activity(activity_id)

    except (KeyError, ValueError):
        return apology()

    # Method is GET
    if request.method == "GET":        
        # Query the database
        query_result = g.con.execute("SELECT availability FROM activities WHERE id = ?;", (activity_id, )).fetchone()

        if query_result is None:
            return apology()

        # JSON string -> list[list[remaining by time] by day]
        activity_availability = json.loads(query_result[0])

        activity_timespans = tuple(
            (i//activity_dict["length"], fmt_timespan(i, i + activity_dict["length"] - 1))
            for i in range(0, len(TIMESPANS)-activity_dict["length"]+1, activity_dict["length"])
        )

        if "user_id" not in session:
            # For users not logged in

            return render_template(
                "activity_readonly.html",
                id=activity_id,
                activity=activity_dict,
                days=tuple(enumerate(DAYS)),
                timespans=activity_timespans,
                availability=activity_availability
            )

        if g.user_type == "staff":
            bookings = g.con.execute(
                "SELECT full_name, class, day, module_start, module_end FROM users JOIN registrations ON users.id = registrations.user_id WHERE activity_id = ? ORDER BY type, full_name;",
                (activity_id, )
            ).fetchall()

            # group the registrations by time
            bookings = sorted(bookings, key=lambda reg: reg[2:5]) # required by groupby
            bookings_by_time = (
                (DAYS_TEXT[key[0]] + " " + fmt_timespan(key[1], key[2]), map(lambda reg: reg[0:2], group))
                for key, group in groupby(bookings, lambda reg: reg[2:5])
            )

            return render_template(
                "activity_staff.html",
                id=activity_id,
                activity=activity_dict,
                days=tuple(enumerate(DAYS)),
                timespans=activity_timespans,
                availability=activity_availability,
                bookings=bookings_by_time
            )
            
        
        # g.user_type != "staff"
        user_registrations = g.con.execute("SELECT day, module_start, module_end FROM registrations WHERE user_id = ?;", (g.user_id, )).fetchall()

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

        user_free = [[all(day_free[module_start:module_start+activity_dict["length"]])
                     for module_start in range(0, len(TIMESPANS)-activity_dict["length"]+1, activity_dict["length"])]
                     for i, day_free in enumerate(user_free) if g.user_type in PERMISSIONS[i]]
        
        return render_template(
            "activity.html",
            id=activity_id,
            activity=activity_dict,
            days=activity_days,
            timespans=activity_timespans,
            availability=activity_availability,
            user_free=user_free
        )

    # Method is POST

    if "user_id" not in session:
        return apology()

    if not g.can_book:
        return apology()
 
    # If booking
    if "booking-button" in request.form:
        # Fetch data
        try:
            day = int(request.form['day-button'])
            module = int(request.form["timespan-button"])
            
        except (TypeError, ValueError):
            return apology()

        # Make registration
        try:
            make_registration(g.user_id, activity_id, day, module, g.user_type, g.con)
            g.con.commit()
        
        except ValueError:
            return apology("Prenotazione non valida", 200)

    # If unbooking
    elif "unbooking-button" in request.form:
        registration = g.con.execute("SELECT day, module_start FROM registrations WHERE user_id = ? AND activity_id = ?;", (g.user_id, activity_id)).fetchone()
        
        if registration is None:
            return apology()

        day, module_start = registration
        module = module_start // activity_dict["length"]

        # Update availability
        update_availability(activity_id, day, module, 1, g.con)
        
        # Remove registration
        g.con.execute("DELETE FROM registrations WHERE user_id = ? AND activity_id = ?;", (g.user_id, activity_id))
        g.con.commit()
        
    # Wildcard (error)
    else:
        return apology()
    
    return redirect("/me")


@app.route("/me")
@login_required
def me_page():
    """Me page w/ your bookings"""

    return render_template(
        "me.html",
        schedule=generate_schedule(g.user_id, g.user_type, g.con),
    )


@app.route("/esterni", methods=["GET", "POST"])
@login_required
def group_page():
    """Manage and add accounts of family members / friends"""

    if g.user_type == "guest":
        return apology()

    if request.method == "GET":
        group_members = g.con.execute(
            "SELECT login_code, full_name FROM users WHERE owner = ?;",
            (g.user_id, )
        ).fetchall()

        return render_template("groups.html", group_members=group_members, link=LINK)

    # Method is POST

    name = request.form.get("name")
    surname = request.form.get("surname")

    if not name or len(name) > MAX_FIELD_LENGTH:
        return apology("Nome non valido", 200)

    if not surname or len(surname) > MAX_FIELD_LENGTH:
        return apology("Cognome non valido", 200)

    full_name = surname.strip() + ' ' + name.strip()

    # Create a new user that can only be accessed via this page
    g.con.execute(
        "INSERT INTO users (full_name, type, owner) VALUES (?, ?, ?);",
        (full_name, "guest", g.user_id)
    )
    g.con.commit()

    # Redirect to a get request
    return redirect("/esterni")


@app.route("/utente", methods=["GET"])
def group_login():
    """Log-in using a login code."""

    login_code = request.args.get("id")

    if not login_code:
        return apology()

    result = g.con.execute(
        "SELECT id FROM users WHERE login_code = ?;",
        (login_code, )
    ).fetchone()

    if result is None:
        return apology("Codice non valido")

    session["user_id"] = result[0]

    return redirect("/")


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
    result = g.con.execute("SELECT verification_code FROM users WHERE id = ?;", (g.user_id, )).fetchone()
    if not result:
        raise RuntimeError(f"User not found in qr_code: user_id {g.user_id}, email {g.user_email}")

    return qr_code_for(LINK + url_for("verification_page", verification_code=result[0]))


@app.route("/redirect_verifica")
def verification_page():
    try:
        verification_code = request.args["verification_code"]

    except (KeyError, ValueError):
        return apology()

    result = g.con.execute("SELECT id, type, full_name, email FROM users WHERE verification_code = ?;", (verification_code, )).fetchone()
    if not result:
        return apology("Utente non trovato.")

    if result[1] == "staff":
        return apology("Account staff.", 200)

    return render_template(
        "verify_me.html",
        schedule=generate_schedule(int(result[0]), result[1], g.con),
        user_type="impersonate", # This way the warning banner doesn't show up
        user_full_name = result[2],
        user_email = result[3]
    )


@app.route("/user_search")
@staff_required
def search_page():
    query = request.args.get("query")

    # Also check empty queries
    if not query:
        return render_template("search_page.html")

    # Escape wildcard characters
    query = query.replace("%", "\\%").replace("_", "\\_")

    query = query.lower().split()

    if not query:
        return render_template("search_page.html")

    search_sql = "(full_name LIKE ? COLLATE NOCASE OR email LIKE ? COLLATE NOCASE OR class = ? COLLATE NOCASE)"
    sql_query = "SELECT full_name, class, email, verification_code FROM users WHERE " + " AND ".join([search_sql] * len(query)) + " ORDER BY full_name;"

    results = g.con.execute(
        sql_query,
        # Use normalized text for the email
        sum((('%'+q+'%', '%'+normalize_text(q)+'%', q) for q in query), start=tuple())
    ).fetchall()

    # normalize text for the search that follows
    query = list(map(normalize_text, query))

    # Counts the numbers of keywords in the search that are exactly matched
    def count_exact_matches(res):
        res = res[0] # using only full name
        res = map(normalize_text, res)
        res = sum(map(str.split, res), start=[])
        return sum(q in res for q in query)

    # Stable sort: sorts the results by match precision while keeping the alphabetical order from the sql query
    results.sort(key=lambda res: count_exact_matches(res), reverse=True)

    def parse_row(row: tuple) -> tuple:
        return (row[0], url_for("verification_page", verification_code=row[3])), row[1] or "esterno", row[2]

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
        return "", 400

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

    if ADMIN_PASSWORD is not None:
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


@app.route("/archive")
def archive_page():
    return render_template("archive.html")


@app.route("/archive/<year>/activities")
def archive_activities_page(year: str):
    """List of all activities"""
    try:
        activities = get_activities(year)

    except KeyError:
        # invalid year
        return apology()

    return render_template("activities.html", activities=activities, year=year)


@app.route("/archive/<year>/activity")
def archive_activity_page(year: str):
    """Activity page w/ details"""
    try:
        activity_id = int(request.args["id"])
        # Check that the activity exists
        activity_dict = get_activity(activity_id, year)

    except (KeyError, ValueError):
        return apology()

    return render_template(
        "activity_noavail.html",
        id=activity_id,
        activity=activity_dict,
        days=tuple(enumerate(DAYS))
    )
