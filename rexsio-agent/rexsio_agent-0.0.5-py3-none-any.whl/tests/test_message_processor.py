import json
from unittest import TestCase
from unittest.mock import patch

from agent.communication.message_processor import process_message


class TestMessageProcessor(TestCase):
    @patch("agent.communication.message_processor.process_json_message")
    @patch("agent.communication.message_processor.publish_message")
    def test_process_rabbitmq_message(
        self, rabbit_publisher_mock, commands_dispatcher_mock
    ):
        # given
        command_message = b'{"messageType": "COMMAND_MESSAGE", "nodeServiceId": "nodeServiceId", "body": {"key": "value"}}'
        expected_message = json.loads(command_message.decode("utf-8"))
        # when
        process_message(command_message)

        # then
        rabbit_publisher_mock.assert_called_once_with(expected_message)
        commands_dispatcher_mock.assert_not_called()

    @patch("agent.communication.message_processor.process_json_message")
    @patch("agent.communication.message_processor.publish_message")
    def test_process_command_message(
        self, rabbit_publisher_mock, commands_dispatcher_mock
    ):
        # given
        rabbit_message = b'{"messageType": "COMMAND_MESSAGE", "nodeServiceId": null, "body": {"key": "value"}}'
        expected_message = json.loads(rabbit_message.decode("utf-8"))
        # when
        process_message(rabbit_message)

        # then
        commands_dispatcher_mock.assert_called_once_with(expected_message)
        rabbit_publisher_mock.assert_not_called()
