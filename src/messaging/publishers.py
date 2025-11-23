"""Message publishers for RabbitMQ."""
import json
import pika
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class MessagePublisher:
    """Publishes messages to RabbitMQ."""
    
    def __init__(self, broker):
        """Initialize publisher with a broker instance."""
        self.broker = broker
    
    def publish(self, 
                queue_name: str, 
                message: Dict[str, Any],
                exchange: str = '',
                routing_key: Optional[str] = None,
                properties: Optional[pika.BasicProperties] = None):
        """Publish a message to a queue."""
        if not self.broker.channel:
            raise RuntimeError("Broker channel not initialized.")
        
        if routing_key is None:
            routing_key = queue_name
        
        body = json.dumps(message)
        
        self.broker.channel.basic_publish(
            exchange=exchange,
            routing_key=routing_key,
            body=body,
            properties=properties or pika.BasicProperties(
                delivery_mode=2,  # Make message persistent
                content_type='application/json'
            )
        )
        logger.debug(f"Published message to {routing_key}: {message}")
    
    def publish_with_reply(self,
                          queue_name: str,
                          message: Dict[str, Any],
                          correlation_id: str,
                          reply_to: str):
        """Publish a message expecting a reply."""
        properties = pika.BasicProperties(
            correlation_id=correlation_id,
            reply_to=reply_to,
            content_type='application/json'
        )
        
        self.publish(
            queue_name=queue_name,
            message=message,
            properties=properties
        )
        logger.debug(f"Published RPC message with correlation_id={correlation_id}")


class OrderPublisher(MessagePublisher):
    """Specialized publisher for order messages."""
    
    def publish_order(self, order_data: Dict[str, Any]):
        """Publish an order message."""
        self.publish(
            queue_name='obs_requests',
            message={
                'action': 'place_order',
                'data': order_data
            }
        )
    
    def publish_cancel_order(self, order_id: str):
        """Publish a cancel order message."""
        self.publish(
            queue_name='obs_requests',
            message={
                'action': 'cancel_order',
                'order_id': order_id
            }
        )


class TradePublisher(MessagePublisher):
    """Specialized publisher for trade messages."""
    
    def publish_trade(self, trade_data: Dict[str, Any]):
        """Publish a trade execution message."""
        self.publish(
            queue_name='trade_events',
            message={
                'event': 'trade_executed',
                'data': trade_data
            }
        )
