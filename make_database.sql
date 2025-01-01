-- Users table. Contains both users and guests
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT KEY NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    type TEXT NOT NULL,
    class TEXT,
    verification_code TEXT KEY NOT NULL UNIQUE,
    can_book INTEGER NOT NULL DEFAULT 1,
    theme TEXT NOT NULL DEFAULT "light"
);

-- Activities table
CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    type TEXT NOT NULL,
    length INTEGER NOT NULL,
    classroom TEXT NOT NULL,
    image TEXT,
    speakers TEXT,
    availability TEXT NOT NULL
);

-- Registrations table. Links users to activities by day and timespan.
CREATE TABLE registrations (
    user_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    day INTEGER NOT NULL,
    module_start INTEGER NOT NULL,
    module_end INTEGER NOT NULL,
    PRIMARY KEY (user_id, activity_id)
);
