import pika
import json

KDB_HOST = 'localhost'
KDB_PORT = 8080
RABBITMQ_HOST = 'localhost'
ORDERBOOK_QUEUE = 'orderbook_requests'
ORDERBOOK_RESPONSE_QUEUE = 'orderbook_responses'

class OrderBookServer:
    def __init__(self):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=ORDERBOOK_QUEUE)
        self.channel.queue_declare(queue=ORDERBOOK_RESPONSE_QUEUE)
        # --- KDB+ INTEGRATION INSTRUCTIONS ---
        # To connect to kdb+ from Python, install the qpython package:
        #   pip install qpython
        # Then, import and create a connection in __init__:
        #   from qpython import qconnection
        #   self.kdb = qconnection.QConnection(host=KDB_HOST, port=KDB_PORT)
        #   self.kdb.open()
        # In on_request, replace the mock orderbook with a real query:
        #   q = f"select from orderbook where sym=`{symbol}"
        #   result = self.kdb.sendSync(q)
        #   # Convert result to a serializable dict for response
        #   orderbook = ...
        # Don't forget to close the connection on shutdown:
        #   self.kdb.close()
        # --------------------------------------

    def on_request(self, ch, method, props, body):
        request = json.loads(body)
        symbol = request.get('symbol', 'AAPL')
        # Here you would query kdb+ for the orderbook. We'll mock a response for now.
        # To use kdb+, see the instructions in __init__ above.
        orderbook = {'symbol': symbol, 'bids': [[100, 10]], 'asks': [[101, 5]]}
        response = json.dumps(orderbook)
        print(f"Trade request received for {symbol}: {request}")
        print(f"Orderbook response: {orderbook}")
        ch.basic_publish(
            exchange='',
            routing_key=ORDERBOOK_RESPONSE_QUEUE,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=response
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

if __name__ == '__main__':
    server = OrderBookServer()
    server.run()
