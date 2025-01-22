from helpers import normalize_text

def parse_csv(row: str) -> tuple:
    return tuple(map(str.title, row.rstrip("\n").split(";")))

# Gli studenti sono indicati con 'cognome nome' in questo ordine 
with open("students_remaining.csv", "r", encoding="UTF-8") as remf:
    students = tuple(map(parse_csv, remf.readlines()))

with open("students_parsed.csv", "r", encoding="UTF-8") as outf:
    parsed_students = tuple(map(parse_csv, outf.readlines()))

all_student_names = tuple(normalize_text(student[1]) for student in parsed_students + students)

# Studenti processati
done = set()

with open("students_parsed.csv", "a", encoding="UTF-8") as outf:
    try:
        for student in students:
            name = normalize_text(student[1])
            # Controlla che il nome dello studente sia univoco
            name_cnt = all_student_names.count(name)
            assert name_cnt >= 1
            unique_student = name_cnt == 1
            # Lo script crea in automatico la email per gli studenti con solo un nome e un cognome.
            # Per gli altri, è necessario controllare a mano la mail.
            if name.count(" ") == 1 and unique_student:
                # nome.cognome rimuovendo gli apostrofi
                mail = ".".join(reversed(name.replace("'", "").split()))
            else:
                if not unique_student:
                    print("!!! Più studenti con lo stesso nome !!!")
                    print("Questo studente: ", " - ".join(student))
                # Cercare la mail su teams
                mail = input(f"e-mail per '{name}' ( ???@liceocassini.eu ): ")
            if mail:
                mail += "@liceocassini.eu"
                done.add(student)
                outf.write(";".join(student) + ";" + mail + "\n")
            else:
                print("Saltato")
    except KeyboardInterrupt:
        print("Progresso salvato.")

# Salva gli studenti non ancora processati
with open("remaining_students.csv", "w", encoding="UTF-8") as remf:
    for student in students:
        if student not in done:
            remf.write(";".join(student) + "\n")

print(len(students) - len(done), "rimanenti.")
