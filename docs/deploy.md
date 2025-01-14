# Setup database
## Caricare le attività
- Caricare titolo, relatori, descrizione, locandina
- "python3 manage.py load-activities -f [[file json con tutte le attività]]"

## Caricare gli utenti
- Assicurarsi che il file con gli studenti sia nel formato corretto
- Aggiungere le mail con data/parse_students.py
- Selezionare gli studenti staff
- "python3 manage.py load-students -f [[file csv con tutti gli studenti]]"

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
- ADMIN_EMAILS: le email degli account admin (**admin != staff, gli account admin dovrebbero essere al massimo due o tre**)
- ADMIN_PASSWORD: hash della password per la pagina admin, come generato da `werkzeug.security.generate_password_hash`

# Controlli
- Assicurarsi che titoli troppo lunghi delle attività non creino problemi
- Provare a registrarsi, effettuare il login, scaricare il catalogo, prenotare, cancellare prenotazioni, utilizzare la pagina admin

# Deploy

- Caricare tutto sul sito: https://eu.pythonanywhere.com/user/ForMeCassini/
- "Enable webapp" nel pannello "Web"
- Il sito sarà visibile presso https://formecassini.eu.pythonanywhere.com/
#### Attivare il backup giornaliero automatico nel pannello "Tasks":
script: "python3 /home/ForMeCassini/sito_forme/auto_backup_maker.py" orario: ogni notte

# Last steps
## mandare le mail

# Mentre il sito è funzionante
- Scaricare regolarmente copie del database
- Verificare l'autenticità degli utenti esterni

# Ultimi passaggi
- Chiudere le registrazioni dalla pagina admin
- Creare i fogli firme con make_pdfs.py dunque compilare il latex generato in pdf (eg overleaf.com)
