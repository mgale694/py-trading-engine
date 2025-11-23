"""Database connection manager for transactional database."""
import sqlite3
from pathlib import Path
from .models import SCHEMA

DB_PATH = Path(__file__).parent / 'trading_engine.db'


class TransactionalDB:
    """Manager for transactional database operations."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self):
        """Initialize database schema."""
        c = self.conn.cursor()
        for stmt in SCHEMA:
            c.execute(stmt)
        self.conn.commit()

    def add_client(self, name, type, description=None):
        """Add a new client."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO clients (name, type, description) VALUES (?, ?, ?)''',
            (name, type, description)
        )
        self.conn.commit()
        return c.lastrowid

    def get_clients(self):
        """Get all clients."""
        c = self.conn.cursor()
        c.execute('SELECT * FROM clients')
        return c.fetchall()

    def add_user(self, username, password_hash):
        """Add a new user."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO users (username, password_hash) VALUES (?, ?)''',
            (username, password_hash)
        )
        self.conn.commit()
        return c.lastrowid

    def get_user_by_username(self, username):
        """Get user by username."""
        c = self.conn.cursor()
        c.execute('SELECT * FROM users WHERE username = ?', (username,))
        return c.fetchone()

    def place_order(self, user_id, symbol, side, quantity, price):
        """Place a new order."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO orders (user_id, symbol, side, quantity, price, status) 
               VALUES (?, ?, ?, ?, ?, ?)''',
            (user_id, symbol, side, quantity, price, 'open')
        )
        self.conn.commit()
        return c.lastrowid

    def record_trade(self, user_id, symbol, side, quantity, price):
        """Record a trade."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO trades (user_id, symbol, side, quantity, price) 
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, symbol, side, quantity, price)
        )
        self.conn.commit()
        return c.lastrowid

    def update_order_status(self, order_id, status):
        """Update order status."""
        c = self.conn.cursor()
        c.execute(
            '''UPDATE orders SET status = ? WHERE id = ?''',
            (status, order_id)
        )
        self.conn.commit()

    def close(self):
        """Close database connection."""
        self.conn.close()


def init_db(db_path=DB_PATH):
    """Initialize the database with schema."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for stmt in SCHEMA:
        c.execute(stmt)
    conn.commit()
    conn.close()
    print(f'Transactional database initialized at {db_path}')


if __name__ == '__main__':
    init_db()
