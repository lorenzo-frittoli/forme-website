# ~~Come trovare gli indirizzi email degli studenti. Breve storia triste.~~

~~[parse_students.py](../data/parse_students.py) è uno script creato per porre rimedio al fatto che, almeno per quanto ne sappiamo noi, non esiste una lista degli indirizzi email degli studenti.~~

# Breve storia felice
A quanto pare **esiste** una lista degli studenti con le relative mail, ed è pure accessibile a chiunque con un account microsoft.
È sufficiente visitare <https://portal.azure.com/>, effettuare il login con il proprio account scolastico e selezionare `Users`.

A questo punto dovrebbe apparire una lista degli utenti ed in cima un bottone `Downloads users` che scarica il tutto in formato CSV.

Una volta scaricato il file CSV è necessario fare un bel po' di pulizia (in particolare togliere tutti gli account che non sono di studenti).\
Consigliamo  [questa estensione](vscode:extension/janisdd.vscode-edit-csv) di VS code per editare i file CSV (se no anche Microsoft Excel o equivalenti possono andare bene).

***È possibile che, ad un certo punto, Microsoft Azure venga disabilitato per gli studenti. In questo caso, chiedere al professore che gestisce gli account Microsoft di scaricare i dati.***

## parse_students.py

Anche se non dovrebbe essere più necessario, rimane comunque la possibilità di utilizzare [parse_students.py](../data/parse_students.py).

Lo script legge i dati degli studenti da un CSV in input e tenta di ricostruire l'indirizzo email da nome e cognome. Nel caso di nomi più lunghi, il programma chiede di controllare l'email manualmente (cercare su Microsoft Teams è il modo più facile).

Siccome possono esserci centinaia di utenti con un nome più complicato in pratica questo approccio richiede ore.


Per semplificare il lavoro lo script è configurato in questo modo:

- Se non si inserisce nulla quando viene richiesto l'indirizzo email lo studente in questione viene saltato
- Gli utenti ai quali è stata assegnata l'email vengono salvati in un file CSV separato
- Se in qualsiasi momento si interrompe lo script con `Ctrl C`:
    - Gli studenti processati fino a quel momento vengono aggiunti al file di output e rimossi da quello di input
    - Gli studenti saltati o non ancora processati vengono riscritti nel file di input per essere processati in un secondo momento.

Quindi è possibile interrompere il lavoro per rincominciarlo in qualsiasi momento.

***Attenzione agli apostrofi. Non ci devono essere apostrofi nelle email. Questa cosa ha già fatto abbastanza danni (anche se parse_students.py dovrebbe toglierli)***
