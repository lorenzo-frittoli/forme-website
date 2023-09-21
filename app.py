import sqlite3
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import json

from helpers import apology, login_required, activity_already_booked, slot_already_booked, decompose_timespan
from constants import *

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
# I have no idea what this means just roll with it
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    # I have no idea what this code is even for, don't ask, it just works ok?
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
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
    con = sqlite3.connect(DATABASE)

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
    cur = con.cursor()
    # query_result is like [(id, pw_hash)] 
    query_result = cur.execute("SELECT id, hash FROM users WHERE email = ?;", (request.form.get("email"),)).fetchall()
    
    # Closing db connection
    cur.close()
    con.close()
    
    # If there is no user saved with the provided email
    if not query_result:
        return apology("email e/o password invalidi", 400)
    
    id, pw_hash = query_result[0]

    # Check password against hash
    if not check_password_hash(pw_hash, request.form.get("password")):
        return apology("email e/o password invalidi", 400)

    # Remember which user has logged in
    session["user_id"] = id

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
    user_class = request.form.get("class")
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

    # Checks if class field was filled
    elif not user_class:
        return apology("Classe non valida", 400)
    
    # Checks if email field was filled
    elif not email:
        return apology("Email non valida", 400)
    
    # Checks if password field was filled
    elif not password:
        return apology("Password non valida", 400)

    # Checks if the confirmation field wass filled
    elif not confirmation:
        return apology("Conferma non valida", 400)

    # Cheks if the password and confirmation match
    elif password != confirmation:
        return apology("password e conferma non coincidono", 400)

    # Checks if email is not taken
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    # cur.execute returns a list like [(el1,), (el2,)] etc
    emails = map(lambda x: x[0], cur.execute("SELECT email FROM users").fetchall())
    if email in emails:
        return apology("email registrata", 400)

    # Save the new user & commit
    cur.execute("INSERT INTO users (email, hash, name, surname, type, class) VALUES (?, ?, ?, ?, ?, ?)",
                (email, generate_password_hash(password), name, surname, "student", user_class))
    con.commit()
    
    
    # Closes cursor and connection
    cur.close()
    con.close()

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
    # Setup database connection
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    # Query DB for id, title, type of every activity in the form list[tuple[id: int, title: str, type: str]]
    query_output = cur.execute("SELECT id, title, type FROM activities").fetchall()
    
    # Closing database connection
    cur.close()
    con.close()
    
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
        # Setup database connection
        con = sqlite3.connect(DATABASE)
        cur = con.cursor()
        
        # Fetch data
        activity_id = request.args["id"]
        cur.execute("SELECT title, abstract, type, availability FROM activities WHERE id = ?;", (activity_id,))
        activity_title, activity_abstract, activity_type, activity_availability = cur.fetchone()
        
        # Close connection to db
        cur.close()
        con.close()
        
        # Details of the activity
        activity_dict = {"title": activity_title,
                        "abstract": activity_abstract,
                        "type": activity_type,
                        }
        
        # JSON string -> dict[day: dict[time: availability]]
        activity_availability = json.loads(activity_availability)
        
        # Check if the activity has already been booked by the user (to display warning)
        booked = activity_already_booked(session["user_id"], activity_id)
        
        return render_template("activity.html", id=activity_id, activity=activity_dict, availability=activity_availability, is_booked=booked)


    # If method is POST (booking button has been pressed)
    # Make connection    
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Fetch data
    activity_id = request.args["id"]
    day = request.form.get('day-button')
    timespan = request.form.get("timespan-button")

    # Check if the user has already booked this activity  
    if activity_already_booked(session["user_id"], activity_id):
        return apology("hai giá prenotato questa attivitá")
    
    # Check if the user has already booked this day-timespan combo
    elif slot_already_booked(session["user_id"], day, timespan):
        return apology("questo slot e' occupato")
    
    
    # Update availability
    length = cur.execute("SELECT length FROM activities WHERE id = ?", (activity_id,)).fetchone()[0]
    availability = json.loads(cur.execute("SELECT availability FROM activities WHERE id = ?", (activity_id,)).fetchone()[0],)
    availability[day][timespan] -= 1
    availability = str(json.dumps(availability))
    cur.execute("UPDATE activities SET availability = ? WHERE id = ?", (f'{availability}', activity_id))    
    
    # Update registrations
    # If there is just 1 timespan to update, do it
    if length == 1:
        cur.execute("INSERT INTO registrations (user_id, activity_id, day, timespan) VALUES (?, ?, ?, ?)", (session["user_id"], activity_id, day, timespan))
    
    # Else, update each relevant timespan
    else:
        for t in decompose_timespan(timespan):
            cur.execute("INSERT INTO registrations (user_id, activity_id, day, timespan) VALUES (?, ?, ?, ?)", (session["user_id"], activity_id, day, t))
    
    # Commit and close connection
    con.commit()
    cur.close()
    con.close()
    
    return redirect("/me")
    

@app.route("/me")
@login_required
def me():
    """Me page w/ your bookings"""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    # Fetch all user registrations -> list[tuple[title, day, timespan]]
    result = """
    SELECT activities.title, registrations.day, registrations.timespan
        FROM registrations JOIN
        activities ON
            registrations.activity_id = activities.id
        WHERE user_id = ?
    """
    cur.execute(result, (session["user_id"],))
    query_results = cur.fetchall()
    
    # Make empty schedule
    schedule = {day: {timespan: ""
                      for timespan in TIMESPANS}
                for day in DAYS}
    
    # Fill with known data
    for title, day, timespan in query_results:
        schedule[day][timespan] = title
        
    # Close connection to db
    cur.close()
    con.close()
        
    return render_template("me.html", schedule=schedule)