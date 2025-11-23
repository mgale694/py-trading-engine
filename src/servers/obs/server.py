"""
Order Book Server (OBS)
Manages the order book, processes order requests, and interacts with trading strategies.
"""
import time
import pika
import json
import logging

logger = logging.getLogger(__name__)

RABBITMQ_HOST = "localhost"
OBS_QUEUE = "obs_requests"
OBS_RESPONSE_QUEUE = "obs_responses"


class OrderBookServer:
    def __init__(self):
        # Initialize RabbitMQ connection and channel
        logger.info("(OBS): Connecting to RabbitMQ")
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=OBS_QUEUE)
        self.channel.queue_declare(queue=OBS_RESPONSE_QUEUE)

    def on_request(self, ch, method, props, body):
        logger.info(f"Received request: {body}")
        request = json.loads(body)
        action = request.get("action")
        response = {}

        if action == "connect":
            logger.info(
                f"Engine {request.get('engine_id')} connected at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.get('timestamp')))}"
            )
            response = {
                "status": "ok",
                "message": f"Engine {request.get('engine_id')} connected to OBS at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(request.get('timestamp')))}",
            }

        ch.basic_publish(
            exchange="",
            routing_key=props.reply_to if props.reply_to else OBS_RESPONSE_QUEUE,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        logger.info(
            "OrderBookServer started. Waiting for client requests via RabbitMQ..."
        )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=OBS_QUEUE, on_message_callback=self.on_request)
        try:
            while True:
                self.connection.process_data_events(time_limit=1)
        except KeyboardInterrupt:
            logger.info("OrderBookServer stopped by user.")
            self.connection.close()
