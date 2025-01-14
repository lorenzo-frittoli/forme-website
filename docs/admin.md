# /admin
La pagina admin è pensata per gestire il sito remotamente.\
Per utilizzare la pagina admin è necessario effettuare il login con una delle mail indicate in `constants.py`.
La pagina admin è generata automaticamente, il decoratore [`@command`](../admin.py) aggiunge automaticamente i comandi alla pagina.\
Dopo che si è eseguito un comando è necessario inserire la passworda admin che è **la stessa per tutti**.


#### Consigli:
- `download_db` in assenza di parametri crea un nuovo backup sul momento e lo scarica
- *Risparmia tempo: **usa tab** per selezionare i comandi e inserire la password*

**Ricaricare la pagina ripete il comando appena eseguito.**
