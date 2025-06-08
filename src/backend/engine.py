import sqlite3
from pathlib import Path
from typing import List, Dict, Any

DB_PATH = Path(__file__).parent.parent / 'database' / 'trading_engine.db'

class OrderBook:
    def __init__(self):
        self.bids = []  # List of buy orders
        self.asks = []  # List of sell orders

    def add_order(self, order: Dict[str, Any]):
        if order['side'] == 'buy':
            self.bids.append(order)
            self.bids.sort(key=lambda x: (-x['price'], x['created_at']))
        else:
            self.asks.append(order)
            self.asks.sort(key=lambda x: (x['price'], x['created_at']))

    def match_orders(self):
        trades = []
        while self.bids and self.asks and self.bids[0]['price'] >= self.asks[0]['price']:
            bid = self.bids[0]
            ask = self.asks[0]
            trade_qty = min(bid['quantity'], ask['quantity'])
            trade_price = ask['price']
            trades.append({'buyer': bid['user_id'], 'seller': ask['user_id'], 'quantity': trade_qty, 'price': trade_price})
            bid['quantity'] -= trade_qty
            ask['quantity'] -= trade_qty
            if bid['quantity'] == 0:
                self.bids.pop(0)
            if ask['quantity'] == 0:
                self.asks.pop(0)
        return trades

class TradingEngine:
    def __init__(self):
        self.orderbook = OrderBook()
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row

    def place_order(self, user_id: int, symbol: str, side: str, quantity: float, price: float):
        c = self.conn.cursor()
        c.execute('''INSERT INTO orders (user_id, symbol, side, quantity, price, status) VALUES (?, ?, ?, ?, ?, ?)''',
                  (user_id, symbol, side, quantity, price, 'open'))
        order_id = c.lastrowid
        self.conn.commit()
        order = {'id': order_id, 'user_id': user_id, 'symbol': symbol, 'side': side, 'quantity': quantity, 'price': price, 'created_at': 0}  # created_at placeholder
        self.orderbook.add_order(order)
        trades = self.orderbook.match_orders()
        for trade in trades:
            c.execute('''INSERT INTO trades (user_id, symbol, side, quantity, price) VALUES (?, ?, ?, ?, ?)''',
                      (trade['buyer'], symbol, 'buy', trade['quantity'], trade['price']))
            c.execute('''INSERT INTO trades (user_id, symbol, side, quantity, price) VALUES (?, ?, ?, ?, ?)''',
                      (trade['seller'], symbol, 'sell', trade['quantity'], trade['price']))
        self.conn.commit()
        return order_id, trades

    def get_pnl(self, user_id: int) -> float:
        c = self.conn.cursor()
        c.execute('''SELECT side, quantity, price FROM trades WHERE user_id = ?''', (user_id,))
        trades = c.fetchall()
        pnl = 0.0
        for t in trades:
            if t['side'] == 'buy':
                pnl -= t['quantity'] * t['price']
            else:
                pnl += t['quantity'] * t['price']
        return pnl

    def close(self):
        self.conn.close()

if __name__ == '__main__':
    engine = TradingEngine()
    print('Trading engine started.')
