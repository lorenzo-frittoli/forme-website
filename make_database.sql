-- "Double quotes" indicate an identifier. E.g. "group" has to be escaped because it is a sql keyword.
-- 'Single quotes' indicate string literals.

-- Users table. Contains both users and guests
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT KEY UNIQUE,
    full_name TEXT NOT NULL,
    type TEXT NOT NULL,
    class TEXT,
    verification_code TEXT KEY NOT NULL UNIQUE DEFAULT (hex(RANDOMBLOB(5))),
    login_code TEXT KEY NOT NULL UNIQUE DEFAULT (hex(RANDOMBLOB(5))),
    can_book INTEGER NOT NULL DEFAULT 1,
    theme TEXT NOT NULL DEFAULT 'light',
    owner INTEGER KEY
);

-- Activities table
CREATE TABLE activities (
    id INTEGER PRIMARY KEY,
    length INTEGER NOT NULL,
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
