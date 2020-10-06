import json
from collections import namedtuple

from agent.commands import dispatcher
from agent.communication import logger
from agent.exceptions.agent_error import AgentError
from agent.rabbitmq.publisher import publish_message

command = namedtuple("command", ["type", "body"])


def process_message(payload: bytes) -> None:
    data = convert_message_to_json(payload.decode("utf8"))
    if data.get("nodeServiceId"):
        publish_message(data)
    else:
        process_json_message(data)


def process_json_message(json_message):
    try:
        resolved_command = process_message_to_command(json_message)
        dispatcher.dispatch_command(resolved_command.type, resolved_command.body)
    except AgentError as error:
        logger.error(f"Dispatching command failed due to the: {error.message}")


def process_message_to_command(json_message):
    message_type = json_message["messageType"]
    body = json_message["body"]
    return command(type=message_type, body=body)


def convert_message_to_json(message):
    try:
        json_message = json.loads(message)
    except json.decoder.JSONDecodeError as e:
        logger.error(f"{message} is not json!")
        raise AgentError(message, e)
    return json_message
