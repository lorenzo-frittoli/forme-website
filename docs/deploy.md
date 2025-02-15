Benvenuto nel tuo personalissimo rito di iniziazione alla setta del SitoFormaggio. \
Segui questi """semplici""" passaggi e potrai anche tu entrare nell'Hall of ~~Fail~~ Fame del ForMe.

# Skill necessarie:
- python
- html (un minimo, proprio poco poco)
- linea di comando
- tanta pazienza

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
[Come ottenere le informazioni per gli studenti](studenti.md)
- cognome nome
- classe (preferibilmente)
- mail (preferibilmente. [Perché?](invio_credenziali.md))

Per far funzionare il sito:
- le credenziali di https://eu.pythonanywhere.com/
- credenziali dell'indirizzo gmail

# Scaricare il codice del sito
- scaricare da <https://codeload.github.com/lorenzo-frittoli/forme-website/legacy.zip/main>
- Installare le librerie necessarie: `pip install -r requirements.txt`

# Provalo un attimo
Per vedere come funziona il sito, [provalo in locale](README.md#testing) .
Mentre prepari il sito, tienilo sempre aperto in locale per vedere come risultano le modifiche. Con il parametro `--debug` il sito si aggiornerà da solo dopo qualsiasi cambio ai file sorgente (*ad eccezione dei file in [static/](../static/)*).

# Setup database
## Caricare le attività
- Salvare le locandine in [static/activity_images](../static/activity_images/)

    *Le locandine non dovrebbero occupare troppo spazio, idealmente meno di 2/3 MB ciascuna.\
    Questo perché vengono scaricate tutte non appena si visita la [pagina delle attività](attivita.md) e considerando che ci saranno decine di laboratori, la pagina impiegherà molto a caricare specialmente da telefono.*
- Salvare le attività in formato json specificando tutti i campi presenti: [data/activities_parsed.json](../data/activities_parsed.json)
- `python3 manage.py load-activities -f [file json con tutte le attività]`

## Caricare gli utenti
- Assicurarsi che il file con gli studenti sia nel formato corretto
- Se necessario, aggiungere le mail utilizzando [parse_students](parse_students)
- Selezionare gli studenti staff
- `python3 manage.py load-students -f [file csv con tutti gli studenti] > passwords.txt`
- Avere cura di tenere il file contente le password per poterle poi mandare via mail

# Aggiornare le pagine
- Cambiare l'anno (ctrl-h #### in [layout.html](../templates/layout.html), [index.html](../templates/index.html), [admin_layout.html](../templates/admin_layout.html))
- Aggiornare [index.html](../templates/index.html): come esempio è caricata la pagina del 2025.
- Se esiste un pdf con il catalogo, caricarlo in [static/](../static/) e aggiungi un link per scaricarlo in [index.html](../templates/index.html).
```html
<!-- index.html così come scaricato contiene il link per il download sotto il logo del ForMe: -->
<a href="/static/Catalogo ForMe.pdf" target="_blank">
    <b>Scarica il catalogo in formato PDF</b>
</a>
```
- Caricare il logo dell'anno corrente come [static/logo_forme.jpg](../static/logo_forme.jpg)

# Aggiornare constants.py
**Se una variabile non ha una descrizione qua sotto, probabilmente non devi toccarla.**
- LINK: l'indirizzo al quale viene hostato il sito
- DAYS: i giorni del laboratorio
- DAYS_TEXT: i giorni del laboratorio, in forma estesa
- TIMESPANS: i moduli dei laboratori come tuple (inizio modulo, fine modulo)
- PERMISSIONS: per ogni giorno, quali tipi di utenti posso iscriversi ai laboratori
- ALLOWED_CLASSES: le classi / sezioni che parteciperanno al ForMe
- ADMIN_EMAILS: le mail degli account admin (**admin != staff, gli admin devono aver letto questa documentazione**)
- ADMIN_PASSWORD: l'hash della password admin (*una buona password per favore!*), come generato da `werkzeug.security.generate_password_hash`

# Controlli
- Eseguire il sito in locale
- Assicurarsi che tutti gli elementi della pagina 'Attività' siano in ordine e funzionanti.
- Provare a registrarsi, effettuare il login, scaricare il catalogo, prenotare, cancellare prenotazioni, utilizzare la pagina admin

# Deploy

- Effettuare il login su https://eu.pythonanywhere.com/
- Rinominare la cartella 'sito_forme' utilizzata l'anno precedente in 'sito_forme_ANNO_SCORSO' (pannello "Files")
- Caricare una zip contenente il nuovo sito
- Aprire un console (pannello "Consoles")
- Estrarre la zip con `unzip`, rinominare la cartella in 'sito_forme'
- Installare le librerie necessarie: `pip install --upgrade -r requirements.txt`
- "Enable webapp" nel pannello "Web"
- Il sito sarà visibile presso https://formecassini.eu.pythonanywhere.com/

Attivare il backup giornaliero automatico nel pannello "Tasks"

# Inviare le credenziali agli studenti
[Vedi la pagina dedicata](send_emails.md)

# Mentre il sito è funzionante
- Scaricare regolarmente copie del database
- Verificare l'autenticità degli utenti esterni

# Ultimi passaggi
- Chiudere le registrazioni per gli studenti dalla pagina admin
- Scaricare il database dalla pagina admin
- Riempire gli orari degli studenti che non si sono prenotati usando [`fill-schedules`](cli.md)
- Creare i fogli firme con [`make_pdfs.py`](../make_pdfs.py), compilare il latex generato in pdf (eg overleaf.com), stampare

# Finito?
- [Facci sapere](README.md#contribute--contact-us) se sei riuscito ad utilizzare il sito, aggiungeremo il tuo nome nella [sezione dedicata](README.md#deployed-by).
