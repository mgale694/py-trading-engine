"""Model parameters and reference data storage."""
import sqlite3
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / 'utilities.db'

UTILITIES_SCHEMA = [
    '''CREATE TABLE IF NOT EXISTS model_params (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        model_name TEXT NOT NULL,
        param_name TEXT NOT NULL,
        param_value TEXT NOT NULL,
        data_type TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(model_name, param_name)
    )''',
    '''CREATE TABLE IF NOT EXISTS instruments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT UNIQUE NOT NULL,
        name TEXT NOT NULL,
        asset_class TEXT NOT NULL,
        tick_size REAL NOT NULL,
        lot_size REAL NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS holidays (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        exchange TEXT NOT NULL,
        date DATE NOT NULL,
        description TEXT,
        UNIQUE(exchange, date)
    )''',
    '''CREATE TABLE IF NOT EXISTS risk_limits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        limit_type TEXT NOT NULL,
        limit_value REAL NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS feature_flags (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        flag_name TEXT UNIQUE NOT NULL,
        is_enabled BOOLEAN DEFAULT 0,
        description TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )'''
]


class ModelParamsDB:
    """Manager for model parameters and reference data."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Initialize utilities schema."""
        c = self.conn.cursor()
        for stmt in UTILITIES_SCHEMA:
            c.execute(stmt)
        self.conn.commit()
    
    def set_param(self, model_name, param_name, param_value, data_type='string'):
        """Set or update a model parameter."""
        c = self.conn.cursor()
        # Convert complex types to JSON
        if isinstance(param_value, (dict, list)):
            param_value = json.dumps(param_value)
            data_type = 'json'
        else:
            param_value = str(param_value)
        
        c.execute(
            '''INSERT INTO model_params (model_name, param_name, param_value, data_type)
               VALUES (?, ?, ?, ?)
               ON CONFLICT(model_name, param_name) 
               DO UPDATE SET param_value=?, data_type=?, updated_at=CURRENT_TIMESTAMP''',
            (model_name, param_name, param_value, data_type, param_value, data_type)
        )
        self.conn.commit()
    
    def get_param(self, model_name, param_name):
        """Get a model parameter."""
        c = self.conn.cursor()
        c.execute(
            'SELECT param_value, data_type FROM model_params WHERE model_name=? AND param_name=?',
            (model_name, param_name)
        )
        row = c.fetchone()
        if row:
            value, data_type = row['param_value'], row['data_type']
            if data_type == 'json':
                return json.loads(value)
            elif data_type == 'int':
                return int(value)
            elif data_type == 'float':
                return float(value)
            return value
        return None
    
    def add_instrument(self, symbol, name, asset_class, tick_size, lot_size):
        """Add a new instrument."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO instruments (symbol, name, asset_class, tick_size, lot_size)
               VALUES (?, ?, ?, ?, ?)''',
            (symbol, name, asset_class, tick_size, lot_size)
        )
        self.conn.commit()
        return c.lastrowid
    
    def get_instrument(self, symbol):
        """Get instrument details."""
        c = self.conn.cursor()
        c.execute('SELECT * FROM instruments WHERE symbol=? AND is_active=1', (symbol,))
        return c.fetchone()
    
    def set_feature_flag(self, flag_name, is_enabled, description=None):
        """Set or update a feature flag."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO feature_flags (flag_name, is_enabled, description)
               VALUES (?, ?, ?)
               ON CONFLICT(flag_name) 
               DO UPDATE SET is_enabled=?, updated_at=CURRENT_TIMESTAMP''',
            (flag_name, is_enabled, description, is_enabled)
        )
        self.conn.commit()
    
    def is_feature_enabled(self, flag_name):
        """Check if a feature flag is enabled."""
        c = self.conn.cursor()
        c.execute('SELECT is_enabled FROM feature_flags WHERE flag_name=?', (flag_name,))
        row = c.fetchone()
        return bool(row['is_enabled']) if row else False
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def init_utilities_db(db_path=DB_PATH):
    """Initialize utilities database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for stmt in UTILITIES_SCHEMA:
        c.execute(stmt)
    conn.commit()
    conn.close()
    print(f'Utilities database initialized at {db_path}')


if __name__ == '__main__':
    init_utilities_db()
