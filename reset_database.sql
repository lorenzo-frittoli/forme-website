-- Drops all tables
DROP TABLE users;
DROP TABLE activities;
DROP TABLE registrations;

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
    availability TEXT DEFAULT '{"09/11": {"1": 20, "2": 20, "3": 20, "4": 20}, "10/11": {"1": 20, "2": 20, "3": 20, "4": 20}, "11/11": {"1": 20, "2": 20, "3": 20, "4": 20}}'
);

-- Registrations table. Links users to activities by day and timestamp.
CREATE TABLE registrations (
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    hour INTEGER CHECK( hour >= 1 AND hour <= 4) NOT NULL,
    day INTEGER CHECK( day >= 1 AND day <= 3) NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(activity_id) REFERENCES activities(activity_id),
    PRIMARY KEY (user_id, activity_id, hour, day)
);