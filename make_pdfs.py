from constants import *
from helpers import fmt_timespan
from jinja2 import Template
import sqlite3

TEMPLATE = "templates" + DIR_SEP + "pdfs.tex"

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]

if not os.path.exists(TEX_DIRECTORY):
    os.makedirs(TEX_DIRECTORY)

with open(TEMPLATE, "r") as t_file:
    template = Template(
        t_file.read(),
        line_statement_prefix="%-j-",
    )

con = sqlite3.connect(DATABASE)

# Create a separate pdf for each day
for day_index, day in enumerate(DAYS):
    data = []

    for activity in get_activities():
        activity["title"] = activity["title"].replace('&', '\\&')
        activity["speakers"] = activity["speakers"].replace('&', '\\&')

        bookings = []

        for module_start in range(0, len(TIMESPANS)-activity["length"]+1, activity["length"]):
            result = con.execute(
                "SELECT full_name, class FROM users JOIN registrations ON users.id = registrations.user_id WHERE activity_id = ? AND day = ? AND module_start = ? ORDER BY full_name;",
                (activity["id"], day_index, module_start)
            ).fetchall()

            if len(result) % 2:
                result.append(("", ""))

            bookings.append([
                fmt_timespan(module_start, module_start + activity["length"] - 1),
                [(_class0 or "", full_name0, _class1 or "", full_name1) for (full_name0, _class0), (full_name1, _class1) in chunks(result, 2)],
            ])

        data.append([str(activity["id"]) + " - " + activity["title"], activity["speakers"], bookings])

    # File con '/' nel nome non sono validi
    with open(TEX_DIRECTORY + day.replace("/", "_")+".tex", "w", encoding="UTF-8") as outf:
        outf.write(
            template.render(
                day=DAYS_TEXT[day_index],
                activities=data,
            )
        )
