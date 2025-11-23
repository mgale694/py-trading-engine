"""Message consumers for RabbitMQ."""
import json
import pika
import logging
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)


class MessageConsumer:
    """Consumes messages from RabbitMQ."""
    
    def __init__(self, broker):
        """Initialize consumer with a broker instance."""
        self.broker = broker
        self.handlers: Dict[str, Callable] = {}
    
    def register_handler(self, action: str, handler: Callable):
        """Register a message handler for a specific action."""
        self.handlers[action] = handler
        logger.debug(f"Registered handler for action: {action}")
    
    def on_message(self, ch, method, properties, body):
        """Default message callback."""
        try:
            message = json.loads(body)
            action = message.get('action')
            
            logger.debug(f"Received message: {message}")
            
            # Call registered handler
            if action in self.handlers:
                response = self.handlers[action](message, properties)
                
                # Send response if reply_to is set
                if properties.reply_to:
                    ch.basic_publish(
                        exchange='',
                        routing_key=properties.reply_to,
                        properties=pika.BasicProperties(
                            correlation_id=properties.correlation_id,
                            content_type='application/json'
                        ),
                        body=json.dumps(response)
                    )
            else:
                logger.warning(f"No handler registered for action: {action}")
            
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
    
    def start_consuming(self, queue_name: str, prefetch_count: int = 1):
        """Start consuming messages from a queue."""
        if not self.broker.channel:
            raise RuntimeError("Broker channel not initialized.")
        
        self.broker.channel.basic_qos(prefetch_count=prefetch_count)
        self.broker.channel.basic_consume(
            queue=queue_name,
            on_message_callback=self.on_message
        )
        
        logger.info(f"Starting to consume messages from {queue_name}")
        try:
            self.broker.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.broker.channel.stop_consuming()


class RPCConsumer(MessageConsumer):
    """RPC-style consumer that expects and sends replies."""
    
    def __init__(self, broker):
        super().__init__(broker)
        self.response = None
        self.correlation_id = None
    
    def on_rpc_response(self, ch, method, properties, body):
        """Handle RPC response."""
        if self.correlation_id == properties.correlation_id:
            self.response = json.loads(body)
        ch.basic_ack(delivery_tag=method.delivery_tag)
    
    def call(self, queue_name: str, message: Dict[str, Any], timeout: int = 10) -> Dict[str, Any]:
        """Make an RPC call and wait for response."""
        if not self.broker.channel:
            raise RuntimeError("Broker channel not initialized.")
        
        # Create callback queue
        result = self.broker.channel.queue_declare(queue='', exclusive=True)
        callback_queue = result.method.queue
        
        # Setup consumer for callback
        self.broker.channel.basic_consume(
            queue=callback_queue,
            on_message_callback=self.on_rpc_response,
            auto_ack=False
        )
        
        # Generate correlation ID
        import uuid
        self.correlation_id = str(uuid.uuid4())
        self.response = None
        
        # Publish request
        self.broker.channel.basic_publish(
            exchange='',
            routing_key=queue_name,
            properties=pika.BasicProperties(
                reply_to=callback_queue,
                correlation_id=self.correlation_id,
                content_type='application/json'
            ),
            body=json.dumps(message)
        )
        
        # Wait for response
        import time
        start_time = time.time()
        while self.response is None:
            self.broker.connection.process_data_events()
            if time.time() - start_time > timeout:
                raise TimeoutError(f"RPC call timed out after {timeout}s")
        
        return self.response
