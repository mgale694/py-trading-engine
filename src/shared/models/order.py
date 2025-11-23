"""Order model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, Optional
from enum import Enum


class OrderSide(Enum):
    """Order side enumeration."""
    BUY = "buy"
    SELL = "sell"


class OrderType(Enum):
    """Order type enumeration."""
    MARKET = "market"
    LIMIT = "limit"


class OrderStatus(Enum):
    """Order status enumeration."""
    PENDING = "pending"
    OPEN = "open"
    FILLED = "filled"
    PARTIALLY_FILLED = "partially_filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


@dataclass
class Order:
    """Order domain model."""
    
    id: str
    user_id: int
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: float
    status: OrderStatus = OrderStatus.PENDING
    filled_quantity: float = 0.0
    remaining_quantity: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def __post_init__(self):
        """Post-initialization processing."""
        if self.remaining_quantity is None:
            self.remaining_quantity = self.quantity
        
        # Convert string enums to proper Enum types
        if isinstance(self.side, str):
            self.side = OrderSide(self.side)
        if isinstance(self.order_type, str):
            self.order_type = OrderType(self.order_type)
        if isinstance(self.status, str):
            self.status = OrderStatus(self.status)
    
    def fill(self, quantity: float):
        """Fill part or all of the order."""
        if quantity > self.remaining_quantity:
            raise ValueError(f"Cannot fill {quantity}, only {self.remaining_quantity} remaining")
        
        self.filled_quantity += quantity
        self.remaining_quantity -= quantity
        self.updated_at = datetime.now()
        
        if self.remaining_quantity == 0:
            self.status = OrderStatus.FILLED
        elif self.filled_quantity > 0:
            self.status = OrderStatus.PARTIALLY_FILLED
    
    def cancel(self):
        """Cancel the order."""
        self.status = OrderStatus.CANCELLED
        self.updated_at = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert order to dictionary."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'symbol': self.symbol,
            'side': self.side.value,
            'order_type': self.order_type.value,
            'quantity': self.quantity,
            'price': self.price,
            'status': self.status.value,
            'filled_quantity': self.filled_quantity,
            'remaining_quantity': self.remaining_quantity,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }
