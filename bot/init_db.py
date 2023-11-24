import sqlite3
import json
import logging



SOURCE_PATH = "/app/data/source.json"
DB_PATH = "/app/data/"
DB = "{}/wine.db".format(DB_PATH)




# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

def initialize():
    # Connect to the database (it will be created if it doesn't exist)
    conn = sqlite3.connect(DB)
    c = conn.cursor()

    # Create the users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            tid INTEGER UNIQUE NOT NULL,
            picked INTEGER DEFAULT 0
        )
    ''')

    # Create the wines table
    c.execute('''
        CREATE TABLE IF NOT EXISTS wines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT UNIQUE NOT NULL,
            quantity INTEGER NOT NULL
        )
    ''')

    # Create the transactions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            wine_id INTEGER,
            quantity INTEGER NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(wine_id) REFERENCES wines(id)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
    
def populate():
    try:
        logger.info("Connecting to database...")
        conn = sqlite3.connect(DB)
        c = conn.cursor()
        logger.info("Connectio succeded!")
    except Exception as e:
        logger.error(e)
        return
    
    try:
        logger.info("Populating database...")
        
        # Load data from JSON file
        with open(SOURCE_PATH) as f:
            data = json.load(f)

        # Iterate over data and insert each item into the database
        for item in data:
            c.execute("INSERT INTO wines(type, quantity) VALUES(?, ?)", 
                        (item['type'], item['quantity']))
                        
        logger.info("Populating succeded!")
    except Exception as e:
        logger.error(e)
        return
    
    try:
        logger.info("Committing changes...")
        conn.commit()
        logger.info("Commit succeded!")
    except Exception as e:
        logger.error(e)
        return
    
    try:
        logger.info("Closing connection...")
        conn.close()
        logger.info("Connection closed!")
    except Exception as e:
        logger.error(e)
        return
    
    
def main() -> None:
    try:
        logger.info("Creating database...")
        initialize()
        logger.info("Database created!")
    except Exception as e:
        logger.error(e)
        return
        
    try:
        logger.info("Initializing database...")
        populate()
        logger.info("Database initialized!")
    except Exception as e:
        logger.error(e)
        
if __name__ == '__main__':
    main()