# Codebase Tour
This file is meant to give you a short tour of the codebase and the technologies used.

## Tech Stack
This are the technologies we use.
It's not important that you memorize everything, just use this as a reference in case you need to look things up.
In general, we use the same technologies as **Django** so if you need to look up anything you can probably refer to their docs.

### Frontend
The frontend is the stuff that happens on the user's device.
Basically, this is what the user sees.
- **HTML5 + CSS** : to modify the looks of webpages (eg: adding a button)
- **JavaScript (JS)** : to add logic to the frontend (eg: make the button do something)
- **Jinja** : to add information from the server into the frontend (eg: a counter that shows how many people signed up)

### Backend
The backend is what happens on the server (server-side).
For example, once a user clicks the sign-up button on an activity, a request will be sent to the server and it will sign the user up.
- **Python3 + Flask** : flask is a library that allows us to use python as a backend

### Database
The database (or DB) is where data is stored.
For example, every user has a unique id and a list of activities they have booked.
This is all stored on the db.
- **SQLite3** : this is a simplified version of SQL that plays well with flask

## Project Structure
- [data](/data) : this folder is used to store data before it is added to the database
- [src](/src) : this is where the majority of the source code is
- [static](/static) : here we keep images (such as the year's logo) and the [`styles.css`](/static/styles.css) which is our css file.
- [templates](/templates) : this is where templates are stored; a template is an HTML file that defines the layout of a webpage.

