# Checklist per Production/Deployment
Benvenuto nel tuo personalissimo rito di iniziazione alla setta del SitoFormaggio.
Segui questi """semplici""" passaggi e potrai anche tu entrare nell'Hall of ~Fail~ Fame del ForMe.

## Requisiti
Ci sono un paio di cose da scaricare:
!TODO 4release
- [Python3](https://www.python.org/downloads/).
- [Codice del sito](https://codeload.github.com/lorenzo-frittoli/forme-website/legacy.zip/main).

Adesso apri un terminale e naviga alla cartella del codice del sito (quella che hai scaricato prima).

A questo punto dobbiamo installare le librerie di python, con il comando:
```pip install -r requirements.txt```

## Creare il DB
Prima di tutto bisogna inizializzare il database, che conterra' le prenotazioni.
Per fare questo, basta eseguire il comando:
```python3 manage.py make-db```
**NB: a seconda del sistema che state utilizzando, il comando `python` potrebbe avere nomi diversi.**
**Nel caso il comando non fosse trovato, provate a sostituire `python` con `py`, `python3`, `py3`.**

## Caricare i dati sul DB
!TODO 
Dopo aver parsato i dati degli studenti e delle attivita', caricali nel db con:
```python3 manage.py load-students -f [filename]```
```python3 manage.py load-activities -f [filename]```
Ovviamente sostituendo con filename i path relativi ai file in questione.

## Testa in Locale
Per provare il sito in locale basta navigare a `localhost:5000/` dopo aver usato il comando:
```flask run```

## Production
Carica la cartella su [PythonAnywhere](https://pythonanywhere.com) e divertiti!.
