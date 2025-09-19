## CLI
La CLI (Command Line Interface) è un insieme di comandi definiti in manage.py.
Questi comandi sono pensati per essere eseguiti solamente in locale.

Esegui `python3 manage.py --help` per elencare tutti i comandi presenti.

Alcuni comandi hanno bisogno di dei parametri, per esempio:

`python3 manage.py load-students -f [FILE CSV]`

#### Comandi utilizzati per creare il database:
- `make-db`
- `load-activities`
- `load-students -f [FILE CSV]`

#### Comandi utilizzati a registrazioni terminate:
- `fill-schedules`

    Questo comando permette di riempire casualmente le prenotazioni degli studenti che hanno lasciato alcuni moduli del proprio orario vuoti (o che non si sono proprio prenotati).

    > Il comando non fa alcuna modifica al database ma si limita a calcolare le prenotazioni mancanti. Le prenotazioni vengono poi eseguite dal comando admin `load_filled_schedules`.

    La procedura è automatizzata, spesso non riesce a riempire subito tutti gli orari e quindi effettua automaticamente più tentativi. \
    È possibile che il programma non riesca a completare tutti gli orari anche dopo centinaia di tentativi.\
    In questo caso, siete nella melma! \
    Il modo più immediato di risolvere il problema è aggiungere posti ad alcuni laboratori tramite il comando admin `recalculate_availability` (contattate prima i relatori per assicurarvi che possano effettivamente gestire più persone di quanto previsto).

    > È possibile che sia matematicamente impossibile riempire tutti i laboratori anche se i posti totali sono più del numero di studenti! \
    Se per esempio rimane da prenotare anche un solo studente ma ci sono posti liberi in solo due o tre laboratori (anche se questi posti liberi sono tanti!) risulta impossibile prenotare lo studente senza fargli fare lo stesso laboratorio più volte. \
    Per evitare scenari del genere consigliamo di avere un margine del 5 - 10% sul numero di posti disponibili.

    > Il comando va necessariamente eseguito in locale perché 1. richiede più potenza computazionale di quanta ne abbiano i server (gratuiti) su cui è hostato il sito 2. se viene eseguito sul database in uso può fare grandissimi danni.

- `make-cancelled -d [DAY]`

    Genera il codice _latex_ per il documento _PDF_ che riassume quali laboratori sono stati cancellati, da inviare ai relatori prima delle giornate dedicate esclusivamente agli esterni. Questo perché normalmente ci sono (relativamente) poche prenotazioni e si vuole evitare che i relatori si presentino a scuola con nessuna (o molte poche) prenotazioni al loro laboratorio.
    Accetta come parametro il giorno per cui generare il documento (0-based).

- `make-pdfs`

    Genera il codice _latex_ per i `fogli firme`, utilizzati dai docenti per fare l'appello prima dell'inizio di ogni laboratorio.

> È necessario compilare a mano il codice _latex_ in _PDF_. Il metodo più immediato è utilizzare un editor _latex_ online (e.g. https://overleaf.com)