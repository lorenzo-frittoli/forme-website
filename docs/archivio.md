# L'archivio

Le attività non sono salvate nel database ma in dei file _JSON_ nella cartella [data](../data/). Insieme al file relativo all'anno corrente sono presenti tutti i file delle attività degli anni passati, che costituiscono l'_archivio_. \
La stessa cosa vale per le locandine dei laboratori, i loghi di ForMe e i cataloghi in formato PDF: nella cartella [static](../static/) sono presenti anche quelli relativi agli anni passati. \
I dati relativi ai vari anni sono poi "registrati" in [archive.py](../archive.py), nella variabile `_ACTIVITIES_CACHE`. \
Si tratta di un dizionario che contiene, per ogni anno, le attività con le relative locandine. I dati relativi all'anno corrente si distinguono solamente perché contrassegnati con `None` come anno.



## La pagina dell'archivio

La pagina html dell'archivio si trova in [templates/archive.html](../templates/archive.html).

La pagina contiene un blocco per ogni anno, con:
- Un link al catalogo online di quell'anno
- Un link al catalogo PDF di quell'anno
- Un'eventuale sezione a tendina contenente il logo dell'anno e ulteriori informazioni

Per aggiungere un nuovo anno è sufficiente aggiungere un nuovo blocco sopra a tutti gli altri.

**La [pagina](../templates/archive.html) d'esempio contiene una spiegazione dettagliata della struttura della pagina dell'archivio.**

> Esiste un backup di tutto l'archivio nella cartella 'data_backup'.
