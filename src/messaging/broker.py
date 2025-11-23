"""RabbitMQ connection broker."""
import pika
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class MessageBroker:
    """Manages RabbitMQ connections and channels."""
    
    def __init__(self, host='localhost', port=5672, username=None, password=None):
        """Initialize broker connection parameters."""
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.connection: Optional[pika.BlockingConnection] = None
        self.channel: Optional[pika.channel.Channel] = None
    
    def connect(self):
        """Establish connection to RabbitMQ."""
        try:
            if self.username and self.password:
                credentials = pika.PlainCredentials(self.username, self.password)
                parameters = pika.ConnectionParameters(
                    host=self.host,
                    port=self.port,
                    credentials=credentials
                )
            else:
                parameters = pika.ConnectionParameters(host=self.host, port=self.port)
            
            self.connection = pika.BlockingConnection(parameters)
            self.channel = self.connection.channel()
            logger.info(f"Connected to RabbitMQ at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            return False
    
    def declare_queue(self, queue_name: str, durable: bool = False):
        """Declare a queue."""
        if not self.channel:
            raise RuntimeError("Channel not initialized. Call connect() first.")
        
        self.channel.queue_declare(queue=queue_name, durable=durable)
        logger.debug(f"Queue declared: {queue_name}")
    
    def declare_exchange(self, exchange_name: str, exchange_type: str = 'direct', durable: bool = False):
        """Declare an exchange."""
        if not self.channel:
            raise RuntimeError("Channel not initialized. Call connect() first.")
        
        self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=durable
        )
        logger.debug(f"Exchange declared: {exchange_name} (type: {exchange_type})")
    
    def bind_queue(self, queue_name: str, exchange_name: str, routing_key: str = ''):
        """Bind queue to exchange."""
        if not self.channel:
            raise RuntimeError("Channel not initialized. Call connect() first.")
        
        self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        logger.debug(f"Queue {queue_name} bound to exchange {exchange_name} with key {routing_key}")
    
    def close(self):
        """Close the connection."""
        if self.connection and self.connection.is_open:
            self.connection.close()
            logger.info("RabbitMQ connection closed")
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
