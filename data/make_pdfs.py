from constants import *
from helpers import fmt_timespan
import sqlite3

TEX_DIRECTORY = "tex" + DIR_SEP
DAYS_TEXT = ["Giovedì 9 Novembre", "Venerdì 10 Novembre", "Sabato 11 Novembre"]

con = sqlite3.connect("database.db")

activities = con.execute("SELECT title, length, id FROM activities ORDER BY id;").fetchall()

# Create a separate pdf for each day
for day_index, day in enumerate(DAYS):
    # File con '/' nel nome non sono validi
    with open(TEX_DIRECTORY + day.replace("/", "_")+".tex", "w", encoding="UTF-8") as outf:
        def put(*args, **kwargs):
            print(*args, **kwargs, file=outf)

        put(
"""\\documentclass{article}

\\usepackage[italian]{babel}
\\usepackage[a4paper,top=2cm,bottom=2cm,left=2cm,right=2cm,marginparwidth=1.75cm]{geometry}
\\usepackage{array}

% Set section numbers only for the first level (sections)
\\setcounter{secnumdepth}{1}
% Disable page numbers
\\pagenumbering{gobble}

\\begin{document}"""
        )
        for activity_title, activity_length, activity_id in activities:
            put(
f"""\\Large\\textbf{{Foglio firme - {DAYS_TEXT[day_index]}}}
\\section{{{activity_title}}}"""
            )
            for module_start in range(0, len(TIMESPANS)-activity_length+1, activity_length):
                module_end = module_start + activity_length - 1
                # Double { } are not formatted by the f-string
                put(
f"""\\subsection{{{fmt_timespan(module_start, module_end)}}}
\\begin{{tabular}}{{| m{{7.2cm}} | m{{1.6cm}} | m{{7.2cm}} |}}
\\hline"""
                )
                # Get the registrations from the database
                result = con.execute(
                    # Sort by type than by surname
                    "SELECT name, surname, class FROM users JOIN registrations ON users.id = registrations.user_id WHERE activity_id = ? AND day = ? AND module_start = ? ORDER BY type, surname || name;",
                    (activity_id, day_index, module_start)
                )
                for name, surname, _class in result:
                    # \\ : newline
                    put(surname + " " + name, "&", _class if _class else "esterno", " & \\\\")
                    put("\\hline")
                put("\\end{tabular}")
            put("\\newpage")
        put("\\end{document}")
