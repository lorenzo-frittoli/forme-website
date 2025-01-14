# Prima di tutto
Controllare che ci siano abbastanza posti per tutti. Le capacità dei laboratori devono essere sufficienti per tutti gli studenti partecipanti.
Assicurarsi di avere tutto il necessario:

Per i laboratori:
- titolo
- descrizione
- locandina
- relatori
- aula
- numero massimo di studenti
- durata

Per gli studenti:
- cognome nome
- classe (preferibilmente)
- mail (preferibilmente)

Per far funzionare il sito:
- le credenziali di https://eu.pythonanywhere.com/
- le credenziali della mail

# Setup database
## Caricare le attività
- Caricare titolo, relatori, descrizione, locandina
- "python3 manage.py load-activities -f [[file json con tutte le attività]]"

## Caricare gli utenti
- Assicurarsi che il file con gli studenti sia nel formato corretto
- Se necessario, aggiungere le mail utilizzando [parse_students](parse_students)
- Selezionare gli studenti staff
- "python3 manage.py load-students -f [[file csv con tutti gli studenti]]" > passwords.txt
- avere cura di tenere il file contente le password per poterle poi mandare via mail.

# Aggiornare le pagine
- Cambiare l'anno (crtl-h ####)
- Aggiornare index.html


# Aggiornare constants.py
**Se una variabile non ha una descrizione qua sotto, probabilmente non devi toccarla.**
- LINK: indirizzo al quale viene hostato il sito
- DAYS: giorni del laboratorio
- TIMESPANS: i moduli dei laboratori come tuple (inizio modulo, fine modulo)
- PERMISSIONS: per ogni giorno, quali tipi di studenti posso iscriversi ai laboratori
- ALLOWED_CLASSES: le classi / sezioni che parteciperanno al ForMe
- ADMIN_EMAILS: le mail degli account admin (**admin != staff, gli admin devono aver letto questa documentazione**)
- ADMIN_PASSWORD: hash della password per la pagina admin, come generato da `werkzeug.security.generate_password_hash`

# Controlli
- Eseguire il sito in locale
- Assicurarsi che tutti gli elementi della pagina 'Attività' siano in ordine e funzionanti.
- Provare a registrarsi, effettuare il login, scaricare il catalogo, prenotare, cancellare prenotazioni, utilizzare la pagina admin

# Deploy

- Caricare tutto su https://eu.pythonanywhere.com/ ()
- "Enable webapp" nel pannello "Web"
- Il sito sarà visibile presso https://formecassini.eu.pythonanywhere.com/
#### Attivare il backup giornaliero automatico nel pannello "Tasks":
script: "python3 /home/ForMeCassini/sito_forme/auto_backup_maker.py" orario: ogni notte

## mandare le mail

# Mentre il sito è funzionante
- Scaricare regolarmente copie del database
- Verificare l'autenticità degli utenti esterni

# Ultimi passaggi
- Chiudere le registrazioni per gli studenti dalla pagina admin
- Scaricare il database dalla pagina admin
- Riempire gli orari degli studenti che non si sono prenotati usando [`fill-schedules`](cli.md)
- Creare i fogli firme con [`make_pdfs.py`](../make_pdfs.py) dunque compilare il latex generato in pdf (eg overleaf.com)
