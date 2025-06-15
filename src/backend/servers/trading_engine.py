import pika
import json
import time
import logging

logger = logging.getLogger(__name__)

RABBITMQ_HOST = "localhost"
TES_QUEUE = "tes_requests"
TES_RESPONSE_QUEUE = "tes_responses"

OBS_QUEUE = "obs_requests"


class TradingEngineServer:
    def __init__(self):
        # Initialize RabbitMQ connection and channel
        logger.info("Connecting to RabbitMQ")
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST)
        )
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=TES_QUEUE)
        self.channel.queue_declare(queue=TES_RESPONSE_QUEUE)

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
        elif action == "buy":
            # Simulate a buy action
            logger.info(f"Processing buy request: {request}")
            response = {"status": "ok", "message": "Buy action processed"}
        elif action == "sell":
            # Simulate a sell action
            logger.info(f"Processing sell request: {request}")
            response = {"status": "ok", "message": "Sell action processed"}
        # ----------------------------------
        ch.basic_publish(
            exchange="",
            routing_key=props.reply_to if props.reply_to else TES_RESPONSE_QUEUE,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response),
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        logger.info(
            "TradingEngineServer started. Waiting for client requests via RabbitMQ..."
        )
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=TES_QUEUE, on_message_callback=self.on_request)
        try:
            while True:
                self.connection.process_data_events(time_limit=1)
        except KeyboardInterrupt:
            logger.info("TradingEngineServer stopped by user.")
            self.connection.close()
