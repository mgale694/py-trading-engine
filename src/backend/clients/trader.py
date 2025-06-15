import pika
import uuid
import json
import logging
import random
import time

logger = logging.getLogger(__name__)


class TraderClient:
    def __init__(self, host="localhost"):
        self._id = str(uuid.uuid4())
        # Initialize RabbitMQ connection and channel
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=host))
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

    def send_request(self, request):
        logger.info(f"Sending request: {request}")
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
        while self.response is None:
            self.connection.process_data_events()
        return self.response

    def run(self):
        response = self.send_request(
            {
                "action": "connect",
                "trader_id": self._id,
                "timestamp": time.time(),
                "description": "Connecting to Trading Engine Server (TES)",
            }
        )
        logger.info(response.get("message", "No message in response"))
        # Add more client logic here as needed
        symbols = ["AAPL", "GOOG", "MSFT", "TSLA"]
        while True:
            try:
                symbol = random.choice(symbols)
                price = round(random.uniform(100, 200), 2)
                quantity = random.randint(1, 100)

                trade = {
                    "trader_id": self._id,
                    "symbol": symbol,
                    "price": price,
                    "quantity": quantity,
                    "action": "buy" if random.choice([True, False]) else "sell",
                }
                self.send_request(trade)
                time.sleep(random.uniform(1, 3))
            except KeyboardInterrupt:
                logger.info("TraderClient interrupted by user.")
                break
