from constants import *
from jinja2 import Template
from helpers import fmt_timespan
import sqlite3
import json

TEMPLATE = "templates" + DIR_SEP + "cancelled.tex"
DAY = 2

if not os.path.exists(TEX_DIRECTORY):
    os.makedirs(TEX_DIRECTORY)

with open(TEMPLATE, "r") as t_file:
    template = Template(
        t_file.read(),
        line_statement_prefix="%-j-",
    )

con = sqlite3.connect(DATABASE)

activities = con.execute("SELECT id, length, availability FROM activities ORDER BY id;").fetchall()

data = []

for activity_id, activity_length, activity_availability in activities:
    activity_title = get_activity(activity_id)["title"].replace('&', '\\&')
    activity_availability = json.loads(activity_availability)[DAY]

    data.append((activity_id, activity_title, []))

    for module, module_start in enumerate(range(0, len(TIMESPANS)-activity_length+1, activity_length)):
        module_end = module_start + activity_length - 1
        data[-1][2].append((fmt_timespan(module_start, module_end), 'ANNULLATO' if activity_availability[module] == -1 else ''))


with open(TEX_DIRECTORY + "cancelled.tex", "w", encoding="UTF-8") as outf:
    outf.write(
        template.render(
            day=DAYS_TEXT[DAY],
            activities=data,
        )
    )
