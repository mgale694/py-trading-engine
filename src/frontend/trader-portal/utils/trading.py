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
        "action": side,
        "trader_id": trader_id,
        "trader_name": trader_name,
        "symbol": symbol,
        "quantity": quantity,
        "price": price,
        "order_type": order_type,
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
        query = """
            SELECT * FROM orders
            WHERE trader_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        cursor.execute(query, (trader_id, limit))
    else:
        query = """
            SELECT * FROM orders
            ORDER BY timestamp DESC
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
        query = """
            SELECT * FROM trades
            WHERE buy_trader_id = ? OR sell_trader_id = ?
            ORDER BY timestamp DESC
            LIMIT ?
        """
        cursor.execute(query, (trader_id, trader_id, limit))
    else:
        query = """
            SELECT * FROM trades
            ORDER BY timestamp DESC
            LIMIT ?
        """
        cursor.execute(query, (limit,))

    trades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return trades


def get_positions(trader_id: str):
    """Get positions for a trader."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM positions
        WHERE trader_id = ?
    """
    cursor.execute(query, (trader_id,))

    positions = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return positions


def get_portfolio(trader_id: str):
    """Get portfolio information for a trader."""
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
        SELECT * FROM portfolios
        WHERE trader_id = ?
    """
    cursor.execute(query, (trader_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return dict(result)
    return None
