import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / 'trading_engine.db'

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
