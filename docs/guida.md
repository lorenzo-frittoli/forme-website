Benvenuto nel tuo personalissimo rito di iniziazione alla setta del SitoFormaggio. \
Segui questi """semplici""" passaggi e potrai anche tu entrare nell'Hall of ~~Fail~~ Fame di ForMe.

La documentazione è scritta in _markdown_, consigliamo di visualizzarla da _Visual Studio Code_. È possibile visualizzare i file _markdown_ attraverso il comando _Ctrl + shift + V_.

# Scaricare il codice del sito
- scaricare da <https://codeload.github.com/lorenzo-frittoli/forme-website/legacy.zip/main> \
(oppure `git clone https://github.com/lorenzo-frittoli/forme-website`)
- Installare le librerie necessarie: `pip install --upgrade -r requirements.txt`

# Skill necessarie:
- python (molto base)
- linea di comando
- un po' di pazienza
- SQL, HTML e javascript possono tornare utili nel caso si volesse fare qualche modifica al sito.

> Questa guida è stata scritta in modo da poter essere seguita passo passo anche da persone con limitate competenze tecniche.


# Come funziona il sito

La versione del sito "vera" (ossia quella operativa) è quella su _PythonAnywhere_. Questa versione serve principalmente come piattaforma di testing. Le due versioni sono comunque pressoché identiche, se non che su questa manca l'archivio.

Il sito su _PythonAnywhere_ è già pronto all'utilizzo e non va modificato se non in minima parte.
Ecco tutte le modifiche che vanno fatte al sito online:

- Aggiungere le attività del nuovo anno in [data](../data)
- Aggiungere locandine, catalogo e logo in [static](../static)
- Caricare il [database](../database.db)
- Aggiornare [constants.py](../constants.py)
- Aggiornare [archive.py](../archive.py)
- Aggiornare la [pagina principale](../templates/index.html), [layout 1](../templates/layout.html) e [layout 2](../templates/basic_layout.html)
- A ForMe finito aggiornare l'[archivio](../templates/archive.html)

> Aggiornare è diverso da caricare. Per modificare i file su _PythonAnywhere_ potete usare l'editor integrato nel sito. Se sostituite ciecamente i file che ci sono su _PythonAnywhere_ con quelli che avete in locale rischiate di piallare l'archivio (o fare altri danni). Nel malaugurato caso doveste piallare l'archivio ce n'è un backup in [data_backup](../data_backup/) (sul _PythonAnywhere_ ovviamente).

La guida spiega passo - passo come fare tutte queste cose.

# Prima di tutto
Controllare che ci siano abbastanza posti per tutti. Le capacità dei laboratori devono essere sufficienti per tutti gli studenti partecipanti. Consigliamo di avere un margine del 5 - 10%.

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
- mail

Per far funzionare il sito:
- le credenziali di https://eu.pythonanywhere.com/
- credenziali dell'indirizzo gmail

# Provalo un attimo
Per vedere come funziona il sito, [provalo in locale](README.md#testing).
Mentre prepari il sito, tienilo sempre aperto in locale per vedere come risultano le modifiche. Con il parametro `--debug` il sito si aggiornerà da solo dopo qualsiasi cambio ai file sorgente (*ad eccezione dei file in [static/](../static/)*).

# Setup database

Il setup del database va fatto il locale. Successivamente il database va caricato su _PythonAnywhere_.

`python3 manage.py make-db`

## Caricare le attività
- Salvare le locandine in [static/activity_images](../static/activity_images/)

    *Le locandine non dovrebbero occupare troppo spazio, idealmente meno di 2/3 MB ciascuna.\
    Questo perché vengono scaricate tutte non appena si visita la [pagina delle attività](attivita.md) e considerando che ci saranno decine di laboratori, la pagina impiegherà molto a caricare specialmente da telefono. Inoltre con un account gratuito su _PythonAnywhere_ si hanno solo 500 MB di storage (che devono bastare per le locandine di tutti gli anni precedenti).*
- Salvare le attività in formato json specificando tutti i campi presenti: [data/activities_parsed.json](../data/activities_parsed.json)

    > Se vi sentite particolarmente intraprendenti potete scrivere uno script che vi generi il file json direttamente da un file CSV, Excel o Google Sheets.

- Registrate le nuove attività in [archive.py](./archivio.md).

- `python3 manage.py load-activities`

## Caricare gli utenti
- Assicurarsi che il file con gli studenti sia nel formato corretto (ossia, che contenga gli stessi campi che contiene quello d'esempio)
- Selezionare gli studenti staff
- `python3 manage.py load-students -f [file csv con tutti gli studenti] > data/passwords.txt`
- Avere cura di tenere il file contente le password per poterle poi mandare via mail

A questo punto potete caricare il database aggiornato su _PythonAnywhere_.

# Caricare locandine, catalogo e logo in [static/](../static/)

Indicate l'anno nel nome di ogni file:
- `/static/Catalogo ForMe [ANNO].pdf`
- `/static/images_[ANNO]/`
- `/static/logo_forme_[ANNO].[jpg/jpeg/png]`

# Aggiornare le pagine html su _PythonAnywhere_

Non è strettamente necessario cambiare le pagine html in locale in quanto hanno una funzione puramente estetica.

- Cambiare l'anno in [layout.html](../templates/layout.html)
- Cabiate il logo in [basic_layout.html](../templates/basic_layout.html). Basta cambiare il seguente link: \
    `<link href="/static/logo_forme.jpg" rel="icon">` \
    Aggiungendo il logo dell'anno corrente.
- Aggiornate [index.html](../templates/index.html) con le informazioni che ritenete più importanti.

    Se esiste un pdf con il catalogo, caricalo in [static/](../static/) e aggiungi un link per scaricarlo.
    ```html
    <!-- index.html normalmente contiene il link per il download sotto il logo di ForMe: -->
    <a href="/static/Catalogo ForMe [ANNO].pdf" target="_blank">
        <b>Scarica il catalogo in formato PDF</b>
    </a>
    ```

# Aggiornare constants.py e caricarlo su _PythonAnywhere_
**Se una variabile non ha una descrizione qua sotto, probabilmente non devi toccarla.**
- LINK: l'indirizzo al quale viene hostato il sito
- DAYS: i giorni del laboratorio
- DAYS_TEXT: i giorni del laboratorio, in forma estesa
- TIMESPANS: i moduli dei laboratori come tuple (inizio modulo, fine modulo)
- PERMISSIONS: per ogni giorno, quali tipi di utenti posso iscriversi ai laboratori
- ADMIN_EMAILS: le mail degli account admin (**[admin](./admin.md) != [staff](./staff.md)**)
- ADMIN_PASSWORD: l'hash della password admin (*una buona password per favore!*), come generato da `werkzeug.security.generate_password_hash`

    > Se si indica `None` la password non verrà richiesta. A vostro rischio e pericolo: se lasciate il computer aperto qualcuno può fare casini senza che voi ve ne accorgiate.
    In ogni caso ricordatevi di fare backup frequenti (e che ci sono i backup automatici giornalieri).

# Controlli
- Eseguire il sito in locale
- Assicurarsi che tutti gli elementi della pagina 'Attività' siano in ordine e funzionanti.
- Provare a registrarsi, effettuare il login, scaricare il catalogo, prenotare, cancellare prenotazioni, utilizzare la pagina admin

# Deploy

Dopo aver aggiornato tutti i file su _PythonAnywhere_ assicuratevi si selezionare "Reload webapp" nel pannello "Web".

- Attivare il backup giornaliero automatico nel pannello "Tasks";

# Inviare le credenziali agli studenti
[Vedi la pagina dedicata](send_emails.md)

# Mentre il sito è funzionante
- Scaricare regolarmente copie del database
- Monitorare la mail per rispondere agli [esterni](esterni.md) che vogliono partecipare e agli studenti nel caso si presentassero problemi
    > La mail va monitorata **molto** regolarmente, più volte al giorno. Consigliamo di darsi i turni a rispondere.

# Ultimi passaggi
- Chiudere le registrazioni per gli studenti dalla pagina admin
- Scaricare il database dalla pagina admin
- Riempire gli orari degli studenti che non si sono prenotati usando [`fill-schedules`](cli.md)
- Creare [fogli firme ed elenco dei laboratori cancellati](./cli.md)
- A ForMe finito, **aggiornate l'[archivio](./archivio.md)** e **tenete attivo il sito**.

> Su _PythonAnywhere_ il sito viene disattivato automaticamente dopo 3 mesi. Per [motivi](https://it.wikipedia.org/wiki/Ottimizzazione_per_i_motori_di_ricerca) (e anche perché sarebbe carino se l'archivio rimanesse sempre disponibile) vi chiediamo per favore di **_tenere il sito sempre funzionante_**. È sufficiente mettervi sul calendario un reminder una volta al mese di andare sul pannello "Web" e selezionare "Run until 3 months from today".


# Finito?
- [Facci sapere](README.md#contribute--contact-us) se sei riuscito ad utilizzare il sito, aggiungeremo il tuo nome nella [sezione dedicata](README.md#deployed-by).
