"""KDB+ client for historical time-series data."""
import pykx as kx
from typing import Dict, List, Any
import logging

logger = logging.getLogger(__name__)


class KDBClient:
    """Client for interacting with KDB+ database."""
    
    def __init__(self, host='localhost', port=8080):
        """Initialize KDB+ connection."""
        self.host = host
        self.port = port
        self.q = None
        self.connect()
    
    def connect(self):
        """Connect to KDB+ database."""
        try:
            self.q = kx.QConnection(host=self.host, port=self.port)
            logger.info(f"Connected to KDB+ at {self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Failed to connect to KDB+: {e}")
            raise
    
    def insert_trade(self, trade_data: Dict[str, Any]):
        """Insert a trade into the trade table."""
        try:
            trade_table = kx.Table(data={
                'id': [str(trade_data['id'])],
                'timestamp': [trade_data['timestamp']],
                'symbol': [str(trade_data.get('symbol', ''))],
                'quantity': [trade_data.get('quantity', 0)],
                'price': [trade_data.get('price', 0)],
                'buyer': [str(trade_data.get('buyer', ''))],
                'seller': [str(trade_data.get('seller', ''))]
            })
            self.q('insert', 'trade', trade_table)
            logger.debug(f"Inserted trade: {trade_data['id']}")
        except Exception as e:
            logger.error(f"Failed to insert trade into KDB+: {e}")
            raise
    
    def insert_quote(self, quote_data: Dict[str, Any]):
        """Insert a quote into the quote table."""
        try:
            quote_table = kx.Table(data={
                'timestamp': [quote_data['timestamp']],
                'symbol': [str(quote_data['symbol'])],
                'bid': [quote_data.get('bid', 0)],
                'ask': [quote_data.get('ask', 0)],
                'bid_size': [quote_data.get('bid_size', 0)],
                'ask_size': [quote_data.get('ask_size', 0)]
            })
            self.q('insert', 'quote', quote_table)
            logger.debug(f"Inserted quote for {quote_data['symbol']}")
        except Exception as e:
            logger.error(f"Failed to insert quote into KDB+: {e}")
            raise
    
    def query_trades(self, symbol: str = None, start_time: float = None, end_time: float = None):
        """Query trades with optional filters."""
        try:
            query = "select from trade"
            conditions = []
            
            if symbol:
                conditions.append(f"symbol=`{symbol}")
            if start_time:
                conditions.append(f"timestamp>={start_time}")
            if end_time:
                conditions.append(f"timestamp<={end_time}")
            
            if conditions:
                query += " where " + ",".join(conditions)
            
            result = self.q(query)
            return result
        except Exception as e:
            logger.error(f"Failed to query trades: {e}")
            raise
    
    def close(self):
        """Close KDB+ connection."""
        if self.q:
            self.q.close()
            logger.info("KDB+ connection closed")
