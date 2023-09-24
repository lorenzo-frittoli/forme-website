#!/usr/bin/env python

from flask.cli import FlaskGroup
import click
import sqlite3
import json
import random

from helpers import make_registration
from constants import *
from app import app


# SETUP
cli = FlaskGroup(app)

@cli.command()
def make_db() -> None:
    """Drops all current tables and sets up new ones in the database"""
    # Create db file if it doesn't exist
    open(DATABASE, "w")
    
    # Initialize sqlite3
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Drop all tables
    TABLE_PARAMETER = "{TABLE_PARAMETER}"
    DROP_TABLE_SQL = f"DROP TABLE {TABLE_PARAMETER};"
    GET_TABLES_SQL = "SELECT name FROM sqlite_schema WHERE type='table' AND name != 'sqlite_sequence';"
    
    cur.execute(GET_TABLES_SQL)
    tables = cur.fetchall()

    for table, in tables:
        sql = DROP_TABLE_SQL.replace(TABLE_PARAMETER, table)
        cur.execute(sql)
    
    # Init the database
    with open(MAKE_DATABASE_COMMAND_FILE, 'r') as sql_file:
        sql_script = sql_file.read()
        
    for command in sql_script.split(";"):
        con.execute(f"{command};")
    
    # Commit changes
    con.commit()

    # Close sqlite3 (optional)
    cur.close()
    con.close()
    

@cli.command()
@click.option("--user-type", help="Type of user whose schedule is going to be filled")
def fill_schedules(user_type: str) -> None:
    """Fill the empty schedules of users of the specified type with random activities"""
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()
    
    slots = [(day, timespan) for day in range(len(DAYS)) for timespan in range(len(TIMESPANS)) if user_type in PERMISSIONS[day]]
    user_ids = cur.execute("SELECT id FROM users WHERE type = ?;", (user_type,)).fetchall()

    # Fill the schedules
    for (user_id,) in user_ids:
        # Fetch all occupied slots
        registrations = cur.execute("SELECT day, module_start, module_end FROM registrations WHERE user_id = ?;", (user_id,)).fetchall()
        booked_slots = []
        
        for day, start, end in registrations:
            for timespan in range(start, end + 1):
                booked_slots.append((day, timespan))
                
        # Fetches available activities
        query = """
        SELECT id, length, availability
        FROM activities
        WHERE id NOT IN (
            SELECT activity_id
            FROM registrations
            WHERE user_id = ?
        );
        """
        non_booked_activities = sorted(cur.execute(query, (user_id,)).fetchall(), key=lambda a: a[1], reverse=True)
        
        print(booked_slots)
        
        # Fill empty slots
        for day, timespan in slots:
            # If the slot is booked, continue
            if (day, timespan) in booked_slots:
                continue
            
            # Check every actvity
            for activity_id, length, availability_str in non_booked_activities:
                availability = json.loads(availability_str)
                
                # Check if actvity length is congruent with the timespan
                if timespan % length != 0:
                    continue
                
                # Check if the slot is available
                elif availability[day][timespan // length] == 0:
                    continue
                
                # Check if the next slots are available (in case of length > 1)
                elif any([(day, pt) in booked_slots for pt in range(timespan, timespan + length) if pt < len(TIMESPANS)]):
                    continue
                                
                # Remove activity
                non_booked_activities.remove((activity_id, length, availability_str))
                
                # Remove used slots
                for partial_timespan in range(timespan, timespan + length):
                    booked_slots.append((day, partial_timespan))
                
                # Add registration
                make_registration(user_id, activity_id, day, timespan // length) # Module 

                break
            
            # If not break (no activity was found)
            else:
                raise ValueError("Not enough activities to cover the whole schedule")

@cli.command()
def make_filler_activity() -> None:
    """Make a new activity"""
    # Init activity details
    TITLE = "Title"
    TYPE = "Type"
    LENGTH = 2
    ABSTRACT = """Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Maecenas volutpat blandit aliquam etiam erat velit scelerisque in. Praesent semper feugiat nibh sed pulvinar proin. Condimentum vitae sapien pellentesque habitant. Mi in nulla posuere sollicitudin aliquam. Commodo viverra maecenas accumsan lacus vel facilisis. Etiam non quam lacus suspendisse faucibus. Eu non diam phasellus vestibulum lorem sed risus ultricies tristique. Egestas pretium aenean pharetra magna ac placerat. Sed velit dignissim sodales ut eu sem integer vitae justo. Facilisi etiam dignissim diam quis enim lobortis scelerisque fermentum dui. In arcu cursus euismod quis.
    Lorem sed risus ultricies tristique nulla. Rhoncus urna neque viverra justo nec ultrices dui sapien. Venenatis urna cursus eget nunc. Tristique sollicitudin nibh sit amet commodo nulla facilisi. Rhoncus aenean vel elit scelerisque. Tempor commodo ullamcorper a lacus vestibulum sed arcu. In hendrerit gravida rutrum quisque non tellus orci ac auctor. Eget felis eget nunc lobortis mattis. Turpis nunc eget lorem dolor sed viverra ipsum nunc. Congue nisi vitae suscipit tellus. Pretium vulputate sapien nec sagittis aliquam malesuada bibendum. Rhoncus aenean vel elit scelerisque. Fermentum odio eu feugiat pretium nibh ipsum consequat nisl vel. Ut sem nulla pharetra diam sit. Natoque penatibus et magnis dis parturient. Lacus sed turpis tincidunt id aliquet risus feugiat in ante. Suspendisse in est ante in nibh mauris cursus. Pulvinar neque laoreet suspendisse interdum. Sollicitudin tempor id eu nisl nunc mi ipsum.
    Imperdiet dui accumsan sit amet nulla facilisi. Tellus elementum sagittis vitae et leo duis ut diam quam. Quam viverra orci sagittis eu volutpat. Nunc sed id semper risus in hendrerit. Fames ac turpis egestas maecenas pharetra convallis posuere. Ultrices vitae auctor eu augue ut. Amet nisl suscipit adipiscing bibendum est ultricies. Habitasse platea dictumst quisque sagittis purus sit. Lobortis mattis aliquam faucibus purus in. Viverra tellus in hac habitasse. Eu scelerisque felis imperdiet proin fermentum leo. Bibendum ut tristique et egestas quis ipsum suspendisse. Sit amet consectetur adipiscing elit pellentesque. Feugiat vivamus at augue eget arcu dictum varius duis at. Duis at tellus at urna condimentum mattis pellentesque id nibh. Morbi non arcu risus quis varius quam. Fringilla urna porttitor rhoncus dolor purus. Nisl nunc mi ipsum faucibus vitae aliquet nec ullamcorper sit. Pellentesque eu tincidunt tortor aliquam nulla facilisi cras fermentum odio. Quis commodo odio aenean sed.
    """

    AVAILABILITY = json.dumps([[20 for _ in range(0, len(TIMESPANS), LENGTH)] for _ in DAYS])
    
    # Init sqlite3
    con = sqlite3.connect(DATABASE)
    cur = con.cursor()

    # Make new activity
    cur.execute("INSERT INTO activities (title, abstract, type, length, availability) VALUES (?, ?, ?, ?, ?);", (TITLE, ABSTRACT, TYPE, LENGTH, AVAILABILITY))
    con.commit()
    
    # Close connection (optional)
    cur.close()
    con.close()


if __name__ == '__main__':
    cli()
