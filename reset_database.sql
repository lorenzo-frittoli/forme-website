DROP TABLE students;
DROP TABLE activities;
DROP TABLE registrations;

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    surname TEXT NOT NULL,
    class TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL
);

CREATE TABLE activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    abstract TEXT NOT NULL,
    type TEXT NOT NULL,
    length INTEGER NOT NULL,
    availability TEXT DEFAULT '{"09/11": {"1": 20, "2": 20, "3": 20, "4": 20}, "10/11": {"1": 20, "2": 20, "3": 20, "4": 20}, "11/11": {"1": 20, "2": 20, "3": 20, "4": 20}}'
);

CREATE TABLE registrations (
    student_id INTEGER NOT NULL,
    activity_id INTEGER NOT NULL,
    hour INTEGER CHECK( hour >= 1 AND hour <= 4) NOT NULL,
    day INTEGER CHECK( day >= 1 AND day <= 3) NOT NULL,
    FOREIGN KEY(student_id) REFERENCES students(student_id),
    FOREIGN KEY(activity_id) REFERENCES activities(activity_id),
    PRIMARY KEY (student_id, activity_id, hour, day)
);