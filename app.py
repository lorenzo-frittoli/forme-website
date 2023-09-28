import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for, g
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import json
import re

from helpers import apology, login_required, activity_already_booked, make_registration, update_availability
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
    # Open the connection to the database
    g.con = sqlite3.connect(DATABASE)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    # I have no idea what this code is even for, don't ask, it just works ok?
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"

    # Close the connection to the database
    g.con.close()

    return response


@app.route("/")
@login_required
def homepage():
    """Homepage"""
    # TODO
    return render_template("homepage.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via GET (as by getting the link)
    if request.method == "GET":
        return render_template("login.html")
    
    # User reached route via POST (as by submitting a form via POST)
    # Ensure username was submitted
    if not request.form.get("email"):
        return apology("email non valida", 400)

    # Ensure password was submitted
    elif not request.form.get("password"):
        return apology("password non valida", 400)

    # Query db for id and hash from email
    cur = g.con.cursor()
    # query_result is like [(id, pw_hash)] 
    query_result = cur.execute("SELECT id, hash FROM users WHERE email = ?;", (request.form.get("email").lower(),)).fetchall()
    
    # If there is no user saved with the provided email
    if not query_result:
        session.clear()
        return apology("email e/o password invalidi", 400)
    
    id, pw_hash = query_result[0]

    # Check password against hash
    if not check_password_hash(pw_hash, request.form.get("password")):
        session.clear()
        return apology("email e/o password invalidi", 400)

    # Fetch user type
    cur.execute("SELECT type FROM users WHERE id = ?;", (id,))
    user_type = cur.fetchone()[0]
    
    # Closing cursor
    cur.close()

    # Remember which user has logged in
    session["user_id"] = id
    session["user_type"] = user_type

    # Redirect user to home page
    return redirect("/")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
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

    # Check that the form was completed
    # Checks if name filed was filled
    if not name:
        return apology("Nome non valido", 400)

    # Checks if surname field was filled
    elif not surname:
        return apology("Cognome non valido", 400)
    
    # Checks if email field was filled
    elif not email:
        return apology("Email non valida", 400)
    
    email = email.lower()
    
    # Checks if email looks valid w/ regex
    if not re.match(EMAIL_REGEX, email):
        return apology("Email non valida", 400)
    
    # Checks if password field was filled
    elif not password:
        return apology("Password non valida", 400)

    # Checks if the confirmation field wass filled
    elif not confirmation:
        return apology("Conferma non valida", 400)

    # Checks if the password and confirmation match
    elif password != confirmation:
        return apology("password e conferma non coincidono", 400)

    # Checks if email is not taken
    cur = g.con.cursor()
    
    # cur.execute returns a list like [(el1,), (el2,)] etc
    emails = cur.execute("SELECT email FROM users WHERE email = ?;", (email,)).fetchall()

    if emails:
        return apology("email registrata", 400)

    # Save the new user & commit
    cur.execute("INSERT INTO users (email, hash, name, surname, type) VALUES (?, ?, ?, ?, ?);",
                (email, generate_password_hash(password), name, surname, "guest"))
    g.con.commit()
    
    
    # Closes cursor
    cur.close()

    # Redirect to the homepage
    return redirect("/")


@app.route("/activities", methods=["GET", "POST"])
@login_required
def activities():
    """List of all activities"""
    
    # If called with POST (clicked the "more info" button)
    if request.method == "POST":
        # Get activity id from buttonpress
        activity_id = request.form.get("activity_id")

        # Redirect to /activity with id in the args
        return redirect(url_for(".activity", id=activity_id))
    
    # If called with GET (loaded the page/clicked link)
    cur = g.con.cursor()
    
    # Query DB for id, title, type of every activity in the form list[tuple[id: int, title: str, type: str]]
    query_output = cur.execute("SELECT id, title, type FROM activities;").fetchall()
    
    # Close cursor
    cur.close()
    
    # If no activity is loaded yet, return apology
    if not query_output:
        return apology("Nessuna attività disponibile al momento")
    
    # Make list of tuples into list of dicts for easy acces with jinja/django (still don't know the difference)
    activities_list = [{"id": activity_id,
                        "title": activity_title,
                        "type": activity_type}
                    for activity_id, activity_title, activity_type in query_output]
    
    return render_template("activities.html", activities=activities_list)
    
    
@app.route("/activity", methods=["GET", "POST"])
@login_required
def activity():
    """Activity page w/ details"""
    # If the page is loaded with GET (eg: clicking a link, getting redirected...)
    if request.method == "GET":        
        # Fetch data
        try:
            activity_id = request.args["id"]
        except KeyError:
            return apology("Invalid http request")
        
        # Setup
        cur = g.con.cursor()
        
        # Query the database
        cur.execute("SELECT title, abstract, type, length, availability FROM activities WHERE id = ?;", (activity_id,))
        query_result = cur.fetchone()
        
        # Close cursor
        cur.close()

        if query_result is None:
            return apology("Invalid http request")

        activity_title, activity_abstract, activity_type, activity_length, activity_availability = query_result

        # Details of the activity
        activity_dict = {"title": activity_title,
                        "abstract": activity_abstract,
                        "type": activity_type
                        }
        
        # JSON string -> list[list[remaining by time] by day]
        activity_availability = json.loads(activity_availability)

        activity_availability = [av for i, av in enumerate(activity_availability) if session["user_type"] in PERMISSIONS[i]]
        
        # Check if the activity has already been booked by the user (to display warning)
        booked = activity_already_booked(session["user_id"], activity_id)

        activity_timespans = tuple(
            (i//activity_length, TIMESPANS[i][0] + "-" + TIMESPANS[i + activity_length - 1][1])
            for i in range(0, len(TIMESPANS)-activity_length+1, activity_length)
        )
        activity_days = tuple((i, day) for i, day in enumerate(DAYS) if session["user_type"] in PERMISSIONS[i])
        
        return render_template("activity.html", id=activity_id, activity=activity_dict, days=activity_days, timespans=activity_timespans, availability=activity_availability, is_booked=booked)

    # If method is POST (booking button has been pressed)
    try:
        activity_id = request.args["id"]
        
    except KeyError:
        return apology("Invalid http request")
    
    # If booking
    if "booking-button" in request.form:    
        # Fetch data
        try:
            day = int(request.form.get('day-button'))
            module = int(request.form.get("timespan-button"))
            
        except (TypeError, ValueError):
            return apology("Invalid http request")

        # Make registration
        try:
            make_registration(session["user_id"], activity_id, day, module)
        
        except ValueError:
            return apology("Prenotazione non valida")
        
    # If unbooking
    elif "unbooking-button" in request.form:
        cur = g.con.cursor()
        
        registration = cur.execute("SELECT day, module_start FROM registrations WHERE user_id = ? AND activity_id = ?;", (session["user_id"], activity_id)).fetchone()
        length = cur.execute("SELECT length FROM activities WHERE id = ?;", (activity_id)).fetchone()[0]
        
        if None in (registration, length):
            return apology("Invalid http request")
        
        day, module_start = registration
        module = module_start // length

        # Update availability
        update_availability(activity_id, day, module, 1)
        
        # Remove registration
        cur.execute("DELETE FROM registrations WHERE user_id = ? AND activity_id = ?;", (session["user_id"], activity_id))
        g.con.commit()
        cur.close()
        
    # Wildcard (error)
    else:
        return apology("Invalid http request")
    
    return redirect("/me")
    

@app.route("/me")
@login_required
def me():
    """Me page w/ your bookings"""
    cur = g.con.cursor()
    
    # Fetch all user registrations -> list[tuple[title, day, timespan]]
    result = """
    SELECT activities.id, activities.title, registrations.day, registrations.module_start, registrations.module_end
        FROM registrations JOIN
        activities ON
            registrations.activity_id = activities.id
        WHERE user_id = ?;
    """
    cur.execute(result, (session["user_id"],))
    query_results = cur.fetchall()
    
    # Make empty schedule
    schedule = {day: {timespan: ("", None)
                      for timespan in TIMESPANS_TEXT}
                for i, day in enumerate(DAYS)
                if session["user_type"] in PERMISSIONS[i]}
        
    # Fill with known data
    for activity_id, title, day, module_start, module_end in query_results:
        for timespan in range(module_start, module_end + 1):
            assert schedule[DAYS[day]][TIMESPANS_TEXT[timespan]] is ("", None)
            link = url_for(".activity", id=activity_id)
            schedule[DAYS[day]][TIMESPANS_TEXT[timespan]] = (title, link)

    # Close cursor
    cur.close()
    
    return render_template("me.html", schedule=schedule)
