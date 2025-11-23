"""Trader client for testing and development."""
import pika
import uuid
import json
import logging
import random
import time

logger = logging.getLogger(__name__)

RABBITMQ_HOST = "localhost"


class TraderClient:
    """Test client that simulates a trader connecting to the TES."""
    
    def __init__(self):
        self._id = str(uuid.uuid4())
        # Initialize RabbitMQ connection and channel
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.callback_queue = self.channel.queue_declare(
            queue="", exclusive=True
        ).method.queue
        self.channel.basic_consume(
            queue=self.callback_queue,
            on_message_callback=self.on_response,
            auto_ack=True,
        )
        self.response = None
        self.corr_id = None

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = json.loads(body)

    def send_request(self, request, timeout=10, retry=3):
        logger.info(f"Sending request: {request}")
        attempt = 0
        while attempt < retry:
            self.response = None
            self.corr_id = str(uuid.uuid4())
            self.channel.basic_publish(
                exchange="",
                routing_key="tes_requests",
                properties=pika.BasicProperties(
                    reply_to=self.callback_queue,
                    correlation_id=self.corr_id,
                ),
                body=json.dumps(request),
            )
            start_time = time.time()
            while self.response is None:
                self.connection.process_data_events()
                if time.time() - start_time > timeout:
                    logger.error(
                        f"Timeout waiting for response from TES (attempt {attempt + 1}/{retry})."
                    )
                    break
            if self.response is not None:
                return self.response
            attempt += 1
            logger.info(f"Retrying send_request (attempt {attempt + 1}/{retry})...")
        return self.response

    def check_tes_connection(self, timeout=10, retry=3):
        """Check TES connectivity by sending a simple request."""
        try:
            response = self.send_request(
                {
                    "action": "connect",
                    "trader_id": self._id,
                    "timestamp": time.time(),
                    "description": "Connecting to Trading Engine Server (TES)",
                },
                timeout=timeout,
                retry=retry,
            )
            if response and response.get("status") == "ok":
                logger.info(response.get("message", "No message in response"))
                return True
            else:
                logger.error("Trading Engine Server (TES) did not respond as expected.")
                return False
        except Exception as e:
            logger.error(f"Failed to connect to Trading Engine Server (TES): {e}")
            return False

    def run(self):
        """Run the trader client."""
        # Check TES connectivity using check_tes_connection
        if not self.check_tes_connection():
            logger.error("Failed to connect to Trading Engine Server (TES). Exiting.")
            return

        # Add more client logic here as needed
        symbols = ["AAPL", "GOOG", "MSFT", "TSLA"]
        while True:
            try:
                symbol = random.choice(symbols)
                price = round(random.uniform(100, 200), 2)
                quantity = random.randint(1, 100)
                action = random.choice(["buy", "sell"])
                response = self.send_request(
                    {
                        "action": action,
                        "trader_id": self._id,
                        "symbol": symbol,
                        "quantity": quantity,
                        "price": price,
                    }
                )
                logger.info(f"Response: {response}")
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info("Trader client stopped by user.")
                self.connection.close()
                break
