-- Users table. Contains both users and guests
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    type TEXT NOT NULL,
    class TEXT
);

-- Activities table
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    type TEXT NOT NULL,
    length INTEGER NOT NULL,
    availability TEXT NOT NULL
);

-- Registrations table. Links users to activities by day and timespan.
CREATE TABLE registrations (
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    day string NOT NULL,
    timespan string NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(activity_id) REFERENCES activities(activity_id),
    PRIMARY KEY (user_id, activity_id, day, timespan)
);