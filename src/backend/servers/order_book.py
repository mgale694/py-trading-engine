import pika
import json
import uuid
import time

KDB_HOST = 'localhost'
KDB_PORT = 8080
RABBITMQ_HOST = 'localhost'
ORDERBOOK_QUEUE = 'orderbook_requests'
ORDERBOOK_RESPONSE_QUEUE = 'orderbook_responses'

class OrderBookServer:
    def __init__(self, strategy):
        self.strategy = strategy
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=ORDERBOOK_QUEUE)
        self.channel.queue_declare(queue=ORDERBOOK_RESPONSE_QUEUE)

    def on_request(self, ch, method, props, body):
        request = json.loads(body)
        # Run the strategy with the order context
        response = self.strategy.run(request)
        print(f"Trade request received for {request['symbol']}: {request}")
        print(f"Orderbook response: {response}")
        # Ensure the response is a JSON string
        ch.basic_publish(
            exchange='',
            routing_key=ORDERBOOK_RESPONSE_QUEUE,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        print('OrderBookServer started. Waiting for orderbook requests via RabbitMQ...')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=ORDERBOOK_QUEUE, on_message_callback=self.on_request)
        try:
            while True:
                self.connection.process_data_events(time_limit=1)
        except KeyboardInterrupt:
            print('OrderBookServer stopped by user.')
            self.connection.close()

# if __name__ == '__main__':
#     server = OrderBookServer(strategy=None)  # Replace None with an instance of your strategy class
#     server.run()
