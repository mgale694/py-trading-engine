import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'trading_engine.db'
CLIENT_DB_PATH = Path(__file__).parent.parent / 'database' / 'clients.db'

# Schema definitions
SCHEMA = [
    '''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL, -- 'buy' or 'sell'
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )''',
    '''CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        side TEXT NOT NULL, -- 'buy' or 'sell'
        quantity REAL NOT NULL,
        price REAL NOT NULL,
        status TEXT NOT NULL, -- 'open', 'filled', 'cancelled'
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )'''
]

class ClientDB:
    def __init__(self, db_path=CLIENT_DB_PATH):
        self.conn = sqlite3.connect(db_path)
        self._init_schema()

    def _init_schema(self):
        c = self.conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                type TEXT NOT NULL, -- 'trader', 'system', 'external'
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()

    def add_client(self, name, type, description=None):
        c = self.conn.cursor()
        c.execute('''INSERT INTO clients (name, type, description) VALUES (?, ?, ?)''', (name, type, description))
        self.conn.commit()
        return c.lastrowid

    def get_clients(self):
        c = self.conn.cursor()
        c.execute('SELECT * FROM clients')
        return c.fetchall()

    def close(self):
        self.conn.close()

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for stmt in SCHEMA:
        c.execute(stmt)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print('Database initialized at', DB_PATH)
    db = ClientDB()
    print('Clients table initialised at', CLIENT_DB_PATH)
