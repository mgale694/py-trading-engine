"""Trade model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class Trade:
    """Trade domain model."""
    
    id: str
    buyer_id: int
    seller_id: int
    symbol: str
    quantity: float
    price: float
    buy_order_id: str
    sell_order_id: str
    timestamp: datetime = field(default_factory=datetime.now)
    execution_time_ms: Optional[float] = None
    
    @property
    def total_value(self) -> float:
        """Calculate total trade value."""
        return self.quantity * self.price
    
    def to_dict(self) -> dict:
        """Convert trade to dictionary."""
        return {
            'id': self.id,
            'buyer_id': self.buyer_id,
            'seller_id': self.seller_id,
            'symbol': self.symbol,
            'quantity': self.quantity,
            'price': self.price,
            'buy_order_id': self.buy_order_id,
            'sell_order_id': self.sell_order_id,
            'timestamp': self.timestamp.isoformat(),
            'execution_time_ms': self.execution_time_ms,
            'total_value': self.total_value,
        }
