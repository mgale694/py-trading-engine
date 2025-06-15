import pika
import json
import uuid
import time
import os
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from database.sqlite_db import ClientDB

RABBITMQ_HOST = 'localhost'
TES_QUEUE = 'tes_requests'
TES_RESPONSE_QUEUE = 'tes_responses'

class TradingEngineServer:
    def __init__(self, db_path=None):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=TES_QUEUE)
        self.channel.queue_declare(queue=TES_RESPONSE_QUEUE)
        self.client_db = ClientDB(db_path) if db_path else ClientDB()
        self.portfolios = self._load_portfolios()

    def _load_portfolios(self):
        # For demo: portfolios are just unique types from the clients table
        clients = self.client_db.get_clients()
        portfolios = set()
        for c in clients:
            # Assume 'type' is used as portfolio for now
            portfolios.add(c[2])
        return list(portfolios) if portfolios else ['default']

    def on_request(self, ch, method, props, body):
        request = json.loads(body)
        action = request.get('action')
        response = {}
        if action == 'list_portfolios':
            response = {'portfolios': self.portfolios}
        elif action == 'select_portfolio':
            portfolio = request.get('portfolio')
            if portfolio in self.portfolios:
                response = {'status': 'ok', 'portfolio': portfolio}
            else:
                response = {'status': 'error', 'message': 'Portfolio not found'}
        elif action == 'register_client':
            name = request.get('name')
            ctype = request.get('type')
            desc = request.get('description')
            cid = self.client_db.add_client(name, ctype, desc)
            response = {'status': 'ok', 'client_id': cid}
        else:
            response = {'status': 'error', 'message': 'Unknown action'}
        ch.basic_publish(
            exchange='',
            routing_key=props.reply_to if props.reply_to else TES_RESPONSE_QUEUE,
            properties=pika.BasicProperties(correlation_id=props.correlation_id),
            body=json.dumps(response)
        )
        ch.basic_ack(delivery_tag=method.delivery_tag)

    def run(self):
        print('TradingEngineServer started. Waiting for client requests via RabbitMQ...')
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(queue=TES_QUEUE, on_message_callback=self.on_request)
        try:
            while True:
                self.connection.process_data_events(time_limit=1)
        except KeyboardInterrupt:
            print('TradingEngineServer stopped by user.')
            self.connection.close()
            self.client_db.close()

if __name__ == '__main__':
    server = TradingEngineServer()
    server.run()
