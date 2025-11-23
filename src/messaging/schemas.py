"""Message schemas for RabbitMQ messages."""
from typing import TypedDict, Literal, Optional
from datetime import datetime


class OrderMessage(TypedDict):
    """Order message schema."""
    action: Literal['place_order', 'cancel_order', 'modify_order']
    user_id: int
    symbol: str
    side: Literal['buy', 'sell']
    quantity: float
    price: float
    order_type: Literal['market', 'limit']
    timestamp: float


class TradeMessage(TypedDict):
    """Trade message schema."""
    event: Literal['trade_executed', 'trade_cancelled']
    trade_id: str
    buyer_id: int
    seller_id: int
    symbol: str
    quantity: float
    price: float
    timestamp: float


class ConnectionMessage(TypedDict):
    """Connection message schema."""
    action: Literal['connect', 'disconnect']
    client_id: str
    client_type: Literal['trader', 'engine', 'system']
    timestamp: float
    description: Optional[str]


class ResponseMessage(TypedDict):
    """Generic response message schema."""
    status: Literal['ok', 'error']
    message: str
    data: Optional[dict]
