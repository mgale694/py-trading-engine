"""Analytics database for aggregated metrics and reporting."""
import sqlite3
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / 'analytics.db'

ANALYTICS_SCHEMA = [
    '''CREATE TABLE IF NOT EXISTS daily_pnl (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        date DATE NOT NULL,
        realized_pnl REAL NOT NULL,
        unrealized_pnl REAL NOT NULL,
        total_pnl REAL NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS trader_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        total_trades INTEGER NOT NULL,
        winning_trades INTEGER NOT NULL,
        losing_trades INTEGER NOT NULL,
        avg_win REAL NOT NULL,
        avg_loss REAL NOT NULL,
        sharpe_ratio REAL,
        max_drawdown REAL,
        period_start DATE NOT NULL,
        period_end DATE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''',
    '''CREATE TABLE IF NOT EXISTS system_performance (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TIMESTAMP NOT NULL,
        metric_name TEXT NOT NULL,
        metric_value REAL NOT NULL,
        unit TEXT
    )''',
    '''CREATE TABLE IF NOT EXISTS trade_analytics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        trade_id INTEGER NOT NULL,
        symbol TEXT NOT NULL,
        execution_time_ms REAL NOT NULL,
        slippage REAL,
        spread REAL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )'''
]


class AnalyticsDB:
    """Manager for analytics database operations."""
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()
    
    def _init_schema(self):
        """Initialize analytics schema."""
        c = self.conn.cursor()
        for stmt in ANALYTICS_SCHEMA:
            c.execute(stmt)
        self.conn.commit()
    
    def insert_daily_pnl(self, user_id, date, realized_pnl, unrealized_pnl, total_pnl):
        """Insert daily PnL record."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO daily_pnl (user_id, date, realized_pnl, unrealized_pnl, total_pnl)
               VALUES (?, ?, ?, ?, ?)''',
            (user_id, date, realized_pnl, unrealized_pnl, total_pnl)
        )
        self.conn.commit()
        return c.lastrowid
    
    def insert_trader_metrics(self, user_id, total_trades, winning_trades, losing_trades,
                            avg_win, avg_loss, period_start, period_end, 
                            sharpe_ratio=None, max_drawdown=None):
        """Insert trader performance metrics."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO trader_metrics 
               (user_id, total_trades, winning_trades, losing_trades, avg_win, avg_loss,
                sharpe_ratio, max_drawdown, period_start, period_end)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
            (user_id, total_trades, winning_trades, losing_trades, avg_win, avg_loss,
             sharpe_ratio, max_drawdown, period_start, period_end)
        )
        self.conn.commit()
        return c.lastrowid
    
    def insert_system_performance(self, timestamp, metric_name, metric_value, unit=None):
        """Insert system performance metric."""
        c = self.conn.cursor()
        c.execute(
            '''INSERT INTO system_performance (timestamp, metric_name, metric_value, unit)
               VALUES (?, ?, ?, ?)''',
            (timestamp, metric_name, metric_value, unit)
        )
        self.conn.commit()
        return c.lastrowid
    
    def get_trader_pnl(self, user_id, start_date=None, end_date=None):
        """Get PnL history for a trader."""
        c = self.conn.cursor()
        query = 'SELECT * FROM daily_pnl WHERE user_id = ?'
        params = [user_id]
        
        if start_date:
            query += ' AND date >= ?'
            params.append(start_date)
        if end_date:
            query += ' AND date <= ?'
            params.append(end_date)
        
        query += ' ORDER BY date DESC'
        c.execute(query, params)
        return c.fetchall()
    
    def close(self):
        """Close database connection."""
        self.conn.close()


def init_analytics_db(db_path=DB_PATH):
    """Initialize analytics database."""
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    for stmt in ANALYTICS_SCHEMA:
        c.execute(stmt)
    conn.commit()
    conn.close()
    print(f'Analytics database initialized at {db_path}')


if __name__ == '__main__':
    init_analytics_db()
