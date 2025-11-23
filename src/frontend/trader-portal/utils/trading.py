"""
Utility functions for trader portal.
Handles connections to TES and database.
"""

import json
import sqlite3
import uuid
from pathlib import Path
from typing import Any, Optional

import pika
import streamlit as st


def get_trader_id() -> str:
    """
    Get or create a unique trader ID for this session.
    Stored in Streamlit session state.
    """
    if "trader_id" not in st.session_state:
        st.session_state.trader_id = str(uuid.uuid4())
    return st.session_state.trader_id


def get_trader_name() -> str:
    """Get or create trader name."""
    if "trader_name" not in st.session_state:
        trader_id = get_trader_id()
        st.session_state.trader_name = f"WebTrader_{trader_id[:8]}"
    return st.session_state.trader_name


def get_db_connection():
    """Get database connection to transactional DB."""
    db_path = (
        Path(__file__).parent.parent.parent.parent
        / "database"
        / "transactional"
        / "trading_engine.db"
    )
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row
    return conn


def send_order_to_tes(
    symbol: str,
    side: str,
    quantity: float,
    price: float,
    order_type: str = "limit",
) -> dict[str, Any]:
    """
    Send order to Trading Engine Server via RabbitMQ.

    Args:
        symbol: Trading symbol (e.g., 'AAPL')
        side: 'buy' or 'sell'
        quantity: Number of shares
        price: Price per share
        order_type: 'limit' or 'market'

    Returns:
        Response from TES
    """
    trader_id = get_trader_id()
    trader_name = get_trader_name()

    order = {
        "action": "place_order",
        "trader_id": trader_id,
        "trader_name": trader_name,
        "symbol": symbol,
        "side": side,  # 'buy' or 'sell'
        "quantity": quantity,
        "price": price,
        "type": order_type,  # 'limit' or 'market'
    }

    try:
        # Connect to RabbitMQ
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = connection.channel()

        # Create callback queue for response
        result = channel.queue_declare(queue="", exclusive=True)
        callback_queue = result.method.queue

        # Correlation ID for matching request/response
        corr_id = str(uuid.uuid4())

        # Send order
        channel.basic_publish(
            exchange="",
            routing_key="tes_requests",
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
            ),
            body=json.dumps(order),
        )

        # Wait for response (with timeout)
        response = None
        for method_frame, properties, body in channel.consume(
            callback_queue, inactivity_timeout=5.0
        ):
            if method_frame is None:
                # Timeout
                break
            if properties.correlation_id == corr_id:
                response = json.loads(body)
                channel.basic_ack(method_frame.delivery_tag)
                break

        connection.close()

        if response:
            return {"success": True, "data": response}
        else:
            return {"success": False, "error": "Timeout waiting for response"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def connect_trader_to_tes() -> dict[str, Any]:
    """
    Send initial connect message to TES.
    Should be called when trader first logs in.
    """
    trader_id = get_trader_id()
    trader_name = get_trader_name()

    connect_msg = {
        "action": "connect",
        "trader_id": trader_id,
        "trader_name": trader_name,
        "description": f"Web trader {trader_name} connecting",
    }

    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
        channel = connection.channel()

        result = channel.queue_declare(queue="", exclusive=True)
        callback_queue = result.method.queue
        corr_id = str(uuid.uuid4())

        channel.basic_publish(
            exchange="",
            routing_key="tes_requests",
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=corr_id,
            ),
            body=json.dumps(connect_msg),
        )

        # Wait for response
        response = None
        for method_frame, properties, body in channel.consume(
            callback_queue, inactivity_timeout=5.0
        ):
            if method_frame is None:
                break
            if properties.correlation_id == corr_id:
                response = json.loads(body)
                channel.basic_ack(method_frame.delivery_tag)
                break

        connection.close()

        if response:
            return {"success": True, "data": response}
        else:
            return {"success": False, "error": "Connection timeout"}

    except Exception as e:
        return {"success": False, "error": str(e)}


def get_orders(trader_id: Optional[str] = None, limit: int = 100):
    """Get orders from database, optionally filtered by trader."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if trader_id:
        # Join with users table to filter by trader UUID (stored as username)
        query = """
            SELECT o.id as order_id, o.user_id, o.symbol, o.side, o.quantity, o.price, o.status,
                   o.created_at as timestamp
            FROM orders o
            JOIN users u ON o.user_id = u.id
            WHERE u.username = ?
            ORDER BY o.created_at DESC
            LIMIT ?
        """
        cursor.execute(query, (trader_id, limit))
    else:
        query = """
            SELECT id as order_id, user_id, symbol, side, quantity, price, status,
                   created_at as timestamp
            FROM orders
            ORDER BY created_at DESC
            LIMIT ?
        """
        cursor.execute(query, (limit,))

    orders = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return orders


def get_trades(trader_id: Optional[str] = None, limit: int = 100):
    """Get trades from database, optionally filtered by trader."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if trader_id:
        # Join with users table to filter by trader UUID (stored as username)
        query = """
            SELECT t.id as trade_id, t.user_id, t.symbol, t.side, t.quantity, t.price, t.timestamp
            FROM trades t
            JOIN users u ON t.user_id = u.id
            WHERE u.username = ?
            ORDER BY t.timestamp DESC
            LIMIT ?
        """
        cursor.execute(query, (trader_id, limit))
    else:
        query = """
            SELECT id as trade_id, user_id, symbol, side, quantity, price, timestamp
            FROM trades
            ORDER BY timestamp DESC
            LIMIT ?
        """
        cursor.execute(query, (limit,))

    trades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return trades


def get_positions(trader_id: str):
    """Get positions for a trader.

    Note: This queries the positions table which is linked to portfolios.
    Since the schema doesn't have trader_id directly in positions,
    we need to join through portfolios->users.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Join through portfolios and users to match trader UUID
    query = """
        SELECT p.id, p.symbol, p.quantity, p.avg_price, p.updated_at
        FROM positions p
        JOIN portfolios pf ON p.portfolio_id = pf.id
        JOIN users u ON pf.user_id = u.id
        WHERE u.username = ?
    """
    cursor.execute(query, (trader_id,))

    positions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return positions


def get_portfolio(trader_id: str):
    """Get portfolio information for a trader."""
    conn = get_db_connection()
    cursor = conn.cursor()

    # Join with users table to match trader UUID
    query = """
        SELECT p.id, p.user_id, p.name, p.created_at
        FROM portfolios p
        JOIN users u ON p.user_id = u.id
        WHERE u.username = ?
    """
    cursor.execute(query, (trader_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return dict(result)

    # Return a default portfolio structure if none exists
    return {
        "user_id": trader_id,
        "cash": 100000.0,  # Starting cash
        "equity": 0.0,
        "total_value": 100000.0,
    }
