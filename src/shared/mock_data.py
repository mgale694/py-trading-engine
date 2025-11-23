"""
Mock data generator for development and testing.
Generates realistic trading data for order book, users, trades, and instruments.
"""
import random
import time
from datetime import datetime, timedelta
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class MockDataGenerator:
    """Generates mock trading data for development."""
    
    # Development-only symbols (limited set)
    DEV_SYMBOLS = [
        'AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN',
        'META', 'NVDA', 'JPM', 'BAC', 'WMT'
    ]
    
    # Price ranges for each symbol (min, max, tick_size)
    SYMBOL_PRICES = {
        'AAPL': (150.0, 200.0, 0.01),
        'GOOGL': (130.0, 180.0, 0.01),
        'MSFT': (350.0, 450.0, 0.01),
        'TSLA': (200.0, 300.0, 0.01),
        'AMZN': (140.0, 180.0, 0.01),
        'META': (300.0, 400.0, 0.01),
        'NVDA': (450.0, 550.0, 0.01),
        'JPM': (140.0, 180.0, 0.01),
        'BAC': (30.0, 45.0, 0.01),
        'WMT': (150.0, 180.0, 0.01),
    }
    
    # Trader name templates
    TRADER_NAMES = [
        'Alice', 'Bob', 'Charlie', 'Diana', 'Eve',
        'Frank', 'Grace', 'Henry', 'Iris', 'Jack',
        'Kate', 'Liam', 'Mia', 'Noah', 'Olivia',
        'Peter', 'Quinn', 'Ruby', 'Sam', 'Tina'
    ]
    
    def __init__(self):
        """Initialize mock data generator."""
        self.user_counter = 1
        self.order_counter = 1
        self.trade_counter = 1
    
    def generate_users(self, count: int = 20) -> List[Dict[str, Any]]:
        """Generate mock users/traders."""
        users = []
        for i in range(count):
            username = f"{random.choice(self.TRADER_NAMES)}{random.randint(100, 999)}"
            users.append({
                'username': username,
                'password_hash': 'mock_hash_' + username,  # Not secure, just for dev
                'email': f'{username.lower()}@traders.dev',
                'full_name': f'{username} Trader'
            })
            self.user_counter += 1
        
        logger.info(f"Generated {count} mock users")
        return users
    
    def generate_instruments(self) -> List[Dict[str, Any]]:
        """Generate instrument definitions."""
        instruments = []
        for symbol in self.DEV_SYMBOLS:
            min_price, max_price, tick_size = self.SYMBOL_PRICES[symbol]
            instruments.append({
                'symbol': symbol,
                'name': f'{symbol} Stock',
                'asset_class': 'equity',
                'tick_size': tick_size,
                'lot_size': 1.0,
                'is_active': True
            })
        
        logger.info(f"Generated {len(instruments)} instrument definitions")
        return instruments
    
    def generate_orders(
        self,
        user_ids: List[int],
        symbols: List[str] = None,
        count: int = 100,
        time_spread_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Generate mock orders.
        
        Args:
            user_ids: List of user IDs to assign orders to
            symbols: List of symbols (defaults to DEV_SYMBOLS)
            count: Number of orders to generate
            time_spread_hours: Spread orders over this many hours
        """
        if symbols is None:
            symbols = self.DEV_SYMBOLS
        
        orders = []
        now = datetime.now()
        
        for _ in range(count):
            symbol = random.choice(symbols)
            user_id = random.choice(user_ids)
            side = random.choice(['buy', 'sell'])
            
            # Get price range for symbol
            min_price, max_price, tick_size = self.SYMBOL_PRICES[symbol]
            
            # Generate price (round to tick size)
            price = round(random.uniform(min_price, max_price) / tick_size) * tick_size
            
            # Generate quantity (multiples of 10)
            quantity = random.choice([10, 25, 50, 100, 150, 200, 500]) * 1.0
            
            # Random status
            status = random.choices(
                ['open', 'filled', 'partially_filled', 'cancelled'],
                weights=[0.4, 0.3, 0.2, 0.1],
                k=1
            )[0]
            
            # Random timestamp within time spread
            time_offset = random.uniform(0, time_spread_hours * 3600)
            created_at = now - timedelta(seconds=time_offset)
            
            orders.append({
                'user_id': user_id,
                'symbol': symbol,
                'side': side,
                'quantity': quantity,
                'price': price,
                'status': status,
                'created_at': created_at.isoformat()
            })
            self.order_counter += 1
        
        logger.info(f"Generated {count} mock orders")
        return orders
    
    def generate_trades(
        self,
        user_ids: List[int],
        symbols: List[str] = None,
        count: int = 50,
        time_spread_hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Generate mock executed trades.
        
        Args:
            user_ids: List of user IDs to assign trades to
            symbols: List of symbols (defaults to DEV_SYMBOLS)
            count: Number of trades to generate
            time_spread_hours: Spread trades over this many hours
        """
        if symbols is None:
            symbols = self.DEV_SYMBOLS
        
        trades = []
        now = datetime.now()
        
        for _ in range(count):
            symbol = random.choice(symbols)
            
            # Get two different users (buyer and seller)
            if len(user_ids) < 2:
                logger.warning("Need at least 2 users to generate trades")
                break
            
            buyer_id, seller_id = random.sample(user_ids, 2)
            
            # Get price range for symbol
            min_price, max_price, tick_size = self.SYMBOL_PRICES[symbol]
            
            # Generate price (round to tick size)
            price = round(random.uniform(min_price, max_price) / tick_size) * tick_size
            
            # Generate quantity (multiples of 10)
            quantity = random.choice([10, 25, 50, 100, 150, 200]) * 1.0
            
            # Random timestamp within time spread
            time_offset = random.uniform(0, time_spread_hours * 3600)
            timestamp = now - timedelta(seconds=time_offset)
            
            trades.append({
                'user_id': buyer_id,  # For now, record as buyer's trade
                'symbol': symbol,
                'side': 'buy',
                'quantity': quantity,
                'price': price,
                'timestamp': timestamp.isoformat()
            })
            self.trade_counter += 1
        
        logger.info(f"Generated {count} mock trades")
        return trades
    
    def generate_orderbook_snapshot(
        self,
        symbol: str,
        depth: int = 5
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Generate a mock order book snapshot for a symbol.
        
        Args:
            symbol: Trading symbol
            depth: Number of price levels on each side
        
        Returns:
            Dict with 'bids' and 'asks' lists
        """
        min_price, max_price, tick_size = self.SYMBOL_PRICES.get(
            symbol,
            (100.0, 200.0, 0.01)
        )
        
        # Mid price
        mid_price = (min_price + max_price) / 2
        
        bids = []
        asks = []
        
        # Generate bids (decreasing prices)
        for i in range(depth):
            price = mid_price - (i * tick_size * random.randint(1, 5))
            quantity = random.uniform(100, 1000)
            bids.append({
                'price': round(price, 2),
                'quantity': round(quantity, 2),
                'orders': random.randint(1, 5)
            })
        
        # Generate asks (increasing prices)
        for i in range(depth):
            price = mid_price + (i * tick_size * random.randint(1, 5))
            quantity = random.uniform(100, 1000)
            asks.append({
                'price': round(price, 2),
                'quantity': round(quantity, 2),
                'orders': random.randint(1, 5)
            })
        
        return {
            'symbol': symbol,
            'bids': bids,
            'asks': asks,
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_positions(
        self,
        user_ids: List[int],
        symbols: List[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate mock positions for users."""
        if symbols is None:
            symbols = self.DEV_SYMBOLS
        
        positions = []
        
        for user_id in user_ids:
            # Each user gets positions in 2-5 random symbols
            user_symbols = random.sample(symbols, k=random.randint(2, min(5, len(symbols))))
            
            for symbol in user_symbols:
                min_price, max_price, _ = self.SYMBOL_PRICES[symbol]
                avg_price = random.uniform(min_price, max_price)
                
                # Random quantity (positive or negative for long/short)
                quantity = random.choice([-500, -200, -100, 100, 200, 500, 1000]) * 1.0
                
                positions.append({
                    'user_id': user_id,
                    'symbol': symbol,
                    'quantity': quantity,
                    'avg_price': round(avg_price, 2)
                })
        
        logger.info(f"Generated {len(positions)} mock positions")
        return positions


def initialize_mock_data(db_manager, analytics_db=None, utilities_db=None):
    """
    Initialize databases with mock data.
    
    Args:
        db_manager: TransactionalDB instance
        analytics_db: AnalyticsDB instance (optional)
        utilities_db: ModelParamsDB instance (optional)
    """
    generator = MockDataGenerator()
    
    logger.info("Starting mock data initialization...")
    
    # 1. Generate and insert users
    logger.info("Creating mock users...")
    users = generator.generate_users(count=20)
    user_ids = []
    for user in users:
        try:
            user_id = db_manager.add_user(user['username'], user['password_hash'])
            user_ids.append(user_id)
        except Exception as e:
            logger.warning(f"User {user['username']} might already exist: {e}")
    
    if not user_ids:
        logger.error("No users created. Cannot generate orders/trades.")
        return
    
    logger.info(f"Created {len(user_ids)} users")
    
    # 2. Generate and insert instruments (if utilities_db provided)
    if utilities_db:
        logger.info("Creating instrument definitions...")
        instruments = generator.generate_instruments()
        for instrument in instruments:
            try:
                utilities_db.add_instrument(
                    symbol=instrument['symbol'],
                    name=instrument['name'],
                    asset_class=instrument['asset_class'],
                    tick_size=instrument['tick_size'],
                    lot_size=instrument['lot_size']
                )
            except Exception as e:
                logger.warning(f"Instrument {instrument['symbol']} might already exist: {e}")
    
    # 3. Generate and insert orders
    logger.info("Creating mock orders...")
    orders = generator.generate_orders(
        user_ids=user_ids,
        count=100,
        time_spread_hours=24
    )
    for order in orders:
        try:
            db_manager.place_order(
                user_id=order['user_id'],
                symbol=order['symbol'],
                side=order['side'],
                quantity=order['quantity'],
                price=order['price']
            )
        except Exception as e:
            logger.error(f"Failed to insert order: {e}")
    
    # 4. Generate and insert trades
    logger.info("Creating mock trades...")
    trades = generator.generate_trades(
        user_ids=user_ids,
        count=50,
        time_spread_hours=24
    )
    for trade in trades:
        try:
            db_manager.record_trade(
                user_id=trade['user_id'],
                symbol=trade['symbol'],
                side=trade['side'],
                quantity=trade['quantity'],
                price=trade['price']
            )
        except Exception as e:
            logger.error(f"Failed to insert trade: {e}")
    
    # 5. Generate analytics data (if analytics_db provided)
    if analytics_db:
        logger.info("Creating mock analytics data...")
        for user_id in user_ids[:10]:  # Just for first 10 users
            try:
                # Daily PnL
                analytics_db.insert_daily_pnl(
                    user_id=user_id,
                    date=datetime.now().date().isoformat(),
                    realized_pnl=random.uniform(-1000, 2000),
                    unrealized_pnl=random.uniform(-500, 1000),
                    total_pnl=random.uniform(-1500, 3000)
                )
                
                # Trader metrics
                total_trades = random.randint(10, 100)
                winning_trades = random.randint(0, total_trades)
                analytics_db.insert_trader_metrics(
                    user_id=user_id,
                    total_trades=total_trades,
                    winning_trades=winning_trades,
                    losing_trades=total_trades - winning_trades,
                    avg_win=random.uniform(50, 200),
                    avg_loss=random.uniform(-200, -50),
                    period_start=(datetime.now() - timedelta(days=30)).date().isoformat(),
                    period_end=datetime.now().date().isoformat(),
                    sharpe_ratio=random.uniform(0.5, 2.5),
                    max_drawdown=random.uniform(-0.3, -0.05)
                )
            except Exception as e:
                logger.error(f"Failed to insert analytics: {e}")
    
    logger.info("✅ Mock data initialization complete!")
    logger.info(f"   - {len(user_ids)} users")
    logger.info(f"   - {len(orders)} orders")
    logger.info(f"   - {len(trades)} trades")
    logger.info(f"   - {len(MockDataGenerator.DEV_SYMBOLS)} instruments")
