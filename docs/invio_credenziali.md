# Invio credenziali
**COSA NON FARE:** *lasciare che gli studenti si registrino da soli. Te ne pentirai.*

Dopo aver registrato tutti gli studenti è necessario fargli avere in qualche modo le credenziali. Il metodo consigliato è inviargliele all'indirizzo email scolastico in modo automatizzato.

*Una possibile alternativa è stampare un foglio con le credenziali degli studenti per ogni classe e consegnare i fogli a mano. Forse richiede meno conoscenze tecniche ma probabilmente è molto più incasinato (e dovete implementarvelo voi). Fate Vobis.*

## Invio via email

Il modo più semplice per inviare grandi quantità di email in modo automatizzato è utilizzare il protocollo [SMTP](https://support.google.com/a/answer/176600?hl=it).

Lo script [send_emails.py](../data/send_emails.py) si connette ai server di Google ed invia le email.

Ha bisogno di:
- `passwords.txt`: File contenente le email degli studenti con le password corrispondenti (generato da `manage.py load-students`)
- `SENDER`: account gmail dal quale vengono inviate le email
- `TOKEN`: password per le app dell'account gmail

Le password per le app si possono gestire da

<https://myaccount.google.com> > "Sicurezza" > "Verifica in due passaggi" > "Password per le app"

*È possibile utilizzare le password per le app solo se la verifica in due passaggi è attiva*

**CONSIGLI**
- Inserisci ll'interno del file `passwords.txt` varie righe con il tuo indirizzo email scolastico e un contatore:
    ```
    [50 credenziali]
    [il tuo indirizzo]@liceocassini.eu 50
    [altre 50]
    [il tuo indirizzo]@liceocassini.eu 100
    [altre 50]
    [il tuo indirizzo]@liceocassini.eu 150
    ...
    ```
    In questo modo è possibile verificare che le credenziali siano state inviate correttamente.

- Il limite giornaliero di invio tramite i server Google è di 1000 email (al momento della scrittura di questo documento). Assicurati di non eccedere il limite.

- Spesso anche se non vengono raggiunti i limiti giornalieri l'invio di grandi quantità di email in poco tempo può causare dei blocchi temporanei. Per questo [send_emails.py](../data/send_emails.py) resetta la connessione al server ogni 50 email.\
Nel caso dovesse disconnettersi il server, riprendete l'invio delle mail dall'ultima non inviata.
