## CLI
La CLI (Command Line Interface) è un insieme di comandi definiti in manage.py.
Questi comandi sono pensati per essere eseguiti solamente in locale.

Esegui `python3 manage.py --help` per elencare tutti i comandi presenti.

Alcuni comandi hanno bisogno di dei parametri, per esempio:

`python3 manage.py load-students -f [FILE CSV]`

I comandi più importanti sono quattro:

#### Comandi utilizzati per caricare il database:
- `make-db`
- `load-activities -f [FILE JSON]`
- `load-students -f [FILE CSV]`

#### Comandi utilizzati a registrazioni terminate:
- `fill-schedules -t [USER TYPE]`

    Questo comando permette di riempire casualmente le prenotazioni degli studenti che hanno lasciato alcuni moduli del proprio orario vuoti.\
    Accetta come parametro il tipo degli utenti ai quali va riempito l'orario, normalmente `student`.\
    Prima di procedere viene effettuato un backup del database.\
    La procedura è automatizzata, spesso non riesce a riempire subito tutti gli orari e quindi effettua automaticamente più tentativi.\
    È possibile (ma molto difficile) che il programma non riesca a completare tutti gli orari neanche dopo centinaia di tentativi. Potrebbe star succedendo una di due cose:
    - `fill-schedules` è rotto. Non dovrebbe succedere, è stato testato molte volte.
    - Non ci sono abbastanza posti per tutti. In questo caso, siete nella melma!\
    Attualmente non c'è modo di risolvere questa cosa facilmente. Una possibile soluzione è aggiungere qualche posto a tutte le attività, però la cosa non è stata implementata e quindi c'è da scrivere un po' di codice.
