# Moretti Telegram Bot
## Descrizione
Uno stupido bot che aiuta a tenere il conto delle bottiglie prese dalla cantina, per evitare di doverlo fare a mano.

## Comandi
- `/aiuto` - Mostra i comandi a disposizione, ovvero:

- `/segna` - Segna le bottiglie presa dalla cantina, chiedendo prima di quale tipo di vino.
- `/controlla` - Controlla le bottiglie rimanenti nella cantina.
- `/cancella` - Cancella l'operazione di segnatura delle bottiglie.
- `/ciucciatori` - Mostra chi ha preso più bottiglie.
- `/mischiatutto` - Mostra un consiglio per la miscelazione del vino.
- `/se_semo_presi` - Mostra chi ha preso cosa, ovvero quante bottiglie per ogni tipo di vino.
- `me_so_sbajato` - Cancella l'ultima segnatura fatta da un utente.


## Installazione
Per installare il bot è necessario avere Docker e Docker Compose installati sul proprio sistema.

1. Clonare il repository
2. Creare un file `source.json` partendo dal file `source.template.json` e inserire i dati relativi ai vini con relative quantità.
3. Creare un file `.env` partendo dal file `env.template` e inserire il token del bot e ed i percorsi per:
   1. la cartella che conterrà il database
   2. il file `source.json` per initializzare il database
4. Esportare il file `.env` come variabile d'ambiente con il comando `export $(cat .env | xargs)`
5. Eseguire il comando `docker-compose up -d` per avviare il bot.

## Informazioni aggiuntive per lo sviluppo
La versione di python utilizata è la **3.11**, mentre la gestione delle dipendenze è affidata a [Poetry](https://python-poetry.org) alla versione **1.6.1**.  
La comunicazione con le API di Telegram è affidata alla libreria [python-telegram-bot](https://python-telegram-bot.org) alla versione **20.6**.  
Il database utilizzato è un semplice sqlite3 alla versione **3.39.5**, gestito tramite la libreria [sqlite3](https://docs.python.org/3/library/sqlite3.html) alla versione **3.12.0**, inclusa nelle standard library di python.

## Warning
Il database utilizza un singolo file `wine.db` e non ha un sistema di backup, dunque se si vuole garantire la persistenza dei dati è necessario eseguire un backup del file `wine.db`, previa interruzione del bot per un backup a freddo. Per sostituire il database con uno nuovo, è necessario interrompere il bot, rimuovere il file `wine.db` e riavviare il bot. Il docker compose prevede la creazione ed inizializzazione del database al primo avvio, grazie al file `init_db.py`, dunque non è necessario eseguire alcuna operazione per inizializzare il database, se non quella di creare il file `source.json` con i dati relativi ai vini.

## TODO
- [ ] Aggiungere un controllo per evitare che il bot venga avviato senza il file `.env` contenente il token del bot.
- [ ] Aggiungere un controllo per evitare che il bot venga avviato senza il file `source.json` contenente i dati relativi ai vini.
- [ ] Migliorare il logging e la gestione degli errori.
- [ ] Aggiungere un sistema per salvare i log in un file o in un database.
- [ ] Aggiungere un controllo sulla quantità di bottiglie rimanenti prima di segnare una bottiglia. Se non ce ne sono, avvisare l'utente.

