import pika
import json
import uuid
import random
import time

RABBITMQ_HOST = 'localhost'
ORDERBOOK_QUEUE = 'orderbook_requests'
ORDERBOOK_RESPONSE_QUEUE = 'orderbook_responses'

def send_orderbook_request(symbol):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    channel = connection.channel()

    # Declare queues in case they don't exist
    channel.queue_declare(queue=ORDERBOOK_QUEUE)
    channel.queue_declare(queue=ORDERBOOK_RESPONSE_QUEUE)

    corr_id = str(uuid.uuid4())
    response = None

    def on_response(ch, method, props, body):
        nonlocal response
        if props.correlation_id == corr_id:
            response = json.loads(body)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            ch.stop_consuming()

    channel.basic_consume(queue=ORDERBOOK_RESPONSE_QUEUE, on_message_callback=on_response)

    request = {'symbol': symbol}
    channel.basic_publish(
        exchange='',
        routing_key=ORDERBOOK_QUEUE,
        properties=pika.BasicProperties(
            reply_to=ORDERBOOK_RESPONSE_QUEUE,
            correlation_id=corr_id
        ),
        body=json.dumps(request)
    )

    print(f'Sent orderbook request for {symbol}, waiting for response...')
    channel.start_consuming()
    print('Received orderbook:', response)
    connection.close()

if __name__ == '__main__':
    symbols = ['AAPL', 'GOOG', 'MSFT', 'TSLA']
    try:
        while True:
            symbol = random.choice(symbols)
            send_orderbook_request(symbol)
            time.sleep(random.uniform(1, 3))  # Random delay between requests
    except KeyboardInterrupt:
        print('Stopped by user.')
