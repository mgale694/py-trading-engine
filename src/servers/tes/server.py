"""
Trading Engine Server (TES)
Handles client registration, portfolio management, and routes trading actions to the order book server.
"""

import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path

import pika

logger = logging.getLogger(__name__)

RABBITMQ_HOST = "localhost"
TES_QUEUE = "tes_requests"
TES_RESPONSE_QUEUE = "tes_responses"

OBS_QUEUE = "obs_requests"
OBS_RESPONSE_QUEUE = "obs_responses"

# Database path
DB_PATH = Path(__file__).parent.parent.parent / "database" / "transactional" / "trading_engine.db"


class TradingEngineServer:
    def __init__(self):
        self._id = str(uuid.uuid4())

        # Initialize database connection
        self.db_conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.db_conn.row_factory = sqlite3.Row
        logger.info(f"(TES): Connected to database at {DB_PATH}")

        # Initialize RabbitMQ connection and channel
        logger.info("(TES): Connecting to RabbitMQ")
        self.tes_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.tes_channel = self.tes_connection.channel()
        self.tes_channel.queue_declare(queue=TES_QUEUE)
        self.tes_channel.queue_declare(queue=TES_RESPONSE_QUEUE)

        self.obs_connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.obs_channel = self.obs_connection.channel()
        self.obs_callback_queue = self.obs_channel.queue_declare(
            queue="", exclusive=True
        ).method.queue
        self.obs_channel.basic_consume(
            queue=self.obs_callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def on_request(self, ch, method, props, body):
        request = json.loads(body)
        action = request.get("action")
        response = {}
        # --- Add your custom logic here ---
        if action == "connect":
            logger.info(
                f"Trader {request.get('trader_id')} connected at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.get('timestamp')))}"
            )
            response = {
                "status": "ok",
                "message": f"Trader {request.get('trader_id')} connected to TES at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.get('timestamp')))}",
            }
        elif action == "place_order":
            # Handle order placement - persist to database
            try:
                trader_id = request.get("trader_id")
                symbol = request.get("symbol")
                side = request.get("side")
                quantity = request.get("quantity")
                price = request.get("price")
                # order_type = request.get("type", "limit")  # Future use for order types

                # Get or create user_id from trader_id (UUID)
                cursor = self.db_conn.cursor()

                # Check if user exists with this trader_id as username
                cursor.execute("SELECT id FROM users WHERE username = ?", (trader_id,))
                user = cursor.fetchone()

                if not user:
                    # Create new user for this trader
                    cursor.execute(
                        "INSERT INTO users (username, password_hash) VALUES (?, ?)",
                        (trader_id, "simulated"),  # Password hash not needed for simulated traders
                    )
                    user_id = cursor.lastrowid
                    logger.info(f"Created new user {user_id} for trader {trader_id[:8]}...")
                else:
                    user_id = user[0]

                # Insert order into database
                cursor.execute(
                    """INSERT INTO orders (user_id, symbol, side, quantity, price, status)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, symbol, side, quantity, price, "open"),
                )
                order_id = cursor.lastrowid
                self.db_conn.commit()

                logger.info(f"Order {order_id} placed: {side} {quantity} {symbol} @ {price}")
                response = {
                    "status": "ok",
                    "message": "Order placed successfully",
                    "order_id": order_id,
                }
            except Exception as e:
                logger.error(f"Error placing order: {e}")
                response = {"status": "error", "message": str(e)}
        elif action == "buy":
            # Legacy support - redirect to place_order
            request["action"] = "place_order"
            request["side"] = "buy"
            return self.on_request(ch, method, props, json.dumps(request).encode())
        elif action == "sell":
            # Legacy support - redirect to place_order
            request["action"] = "place_order"
            request["side"] = "sell"
            return self.on_request(ch, method, props, json.dumps(request).encode())
        # ----------------------------------
        ch.basic_publish(
            exchange="",
            routing_key=props.reply_to if props.reply_to else TES_RESPONSE_QUEUE,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def send_request(self, request, timeout=10, retry=3):
        logger.info(f"Sending request: {request}")
        attempt = 0
        while attempt < retry:
            self.response = None
            self.corr_id = str(uuid.uuid4())
            self.obs_channel.basic_publish(
                exchange="",
                routing_key="obs_requests",
                properties=pika.BasicProperties(
                    reply_to=self.obs_callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=json.dumps(request),
            )
            start_time = time.time()
            while self.response is None:
                self.obs_connection.process_data_events()
                if time.time() - start_time > timeout:
                    logger.error("Timeout waiting for response from OBS.")
                    break
            if self.response is not None:
                return self.response
            attempt += 1
            logger.info(f"Retrying send_request (attempt {attempt + 1}/{retry})...")
        return self.response

    def check_obs_connection(self, timeout=10, retry=3):
        # Check OBS connectivity using send_request with timeout
        try:
            response = self.send_request(
                {
                    "action": "connect",
                    "engine_id": self._id,
                    "timestamp": time.time(),
                    "description": "Connecting TES to Order Book Server (OBS)",
                },
                timeout=timeout,
                retry=retry,
            )
            if response and response.get("status") == "ok":
                logger.info(response.get("message", "No message in response"))
                return True
            else:
                logger.error("Order Book Server (OBS) did not respond as expected.")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Order Book Server (OBS): {e}")
            logger.info("Try running the Order Book Server (OBS) first: \npython main.py -s OBS")
            return False

    def run(self):
        # Check OBS connectivity using check_obs_connection
        if not self.check_obs_connection():
            logger.error("Failed to connect to Order Book Server (OBS). Exiting.")
            return

        logger.info("TradingEngineServer started. Waiting for client requests via RabbitMQ...")
        self.tes_channel.basic_qos(prefetch_count=1)
        self.tes_channel.basic_consume(queue=TES_QUEUE, on_message_callback=self.on_request)
        try:
            while True:
                self.tes_connection.process_data_events(time_limit=1)
        except KeyboardInterrupt:
            logger.info("TradingEngineServer stopped by user.")
            self.tes_connection.close()
            self.db_conn.close()
