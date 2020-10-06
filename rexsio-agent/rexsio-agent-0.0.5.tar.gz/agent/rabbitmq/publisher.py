import json
from typing import Dict, Any

from agent.rabbitmq import logger
from agent.rabbitmq.client import RabbitMqClient


def publish_message(message: Dict[str, Any]) -> None:
    rabbitmq_message = json.dumps(message).encode("utf-8")
    RabbitMqClient.get_instance().publish_message(
        message=rabbitmq_message,
        message_type=message["messageType"],
        topic=message["nodeServiceId"],
    )
    logger.info(f"Message sent to RabbitMQ: {rabbitmq_message}")
