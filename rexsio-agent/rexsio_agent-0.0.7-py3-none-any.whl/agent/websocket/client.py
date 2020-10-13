from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet import reactor
from twisted.internet.protocol import ReconnectingClientFactory

from agent.rabbitmq import rabbitmq_consumer, rabbitmq_publisher
from agent.rabbitmq.consumer import notify_control_center_queue
from agent.websocket import logger
from agent.websocket.utils import resolve_ws_endpoint


class AgentWebSocketClient(WebSocketClientProtocol):
    _instance = None

    @staticmethod
    def init(*args):  # AgentWebSocketFactory requires method with arguments
        AgentWebSocketClient._instance = AgentWebSocketClient()
        return AgentWebSocketClient._instance

    @staticmethod
    def get_instance():
        if not AgentWebSocketClient._instance:
            return AgentWebSocketClient.init()
        return AgentWebSocketClient._instance

    def __init__(self):
        super().__init__()
        self.on_message_handler = None
        self.is_notifying_control_center = False

    def set_on_message_handler(self, on_message_handler):
        self.on_message_handler = on_message_handler

    def onConnect(self, response):
        from agent.communication.message_processor import process_message
        from agent.scheduler.scheduled_tasks_manager import ScheduledTaskManager

        logger.info(f"Connected to Server: {response.peer}")
        self.set_on_message_handler(process_message)
        scheduled_task_manager = ScheduledTaskManager.get_instance()
        scheduled_task_manager.start_executing()
        self.start_notifying_control_center()
        rabbitmq_consumer.start_consuming_messages()
        rabbitmq_publisher.start_publishing_messages()

    def connectionLost(self, reason):
        from agent.scheduler.scheduled_tasks_manager import ScheduledTaskManager

        ScheduledTaskManager.get_instance().stop_executing()
        rabbitmq_consumer.stop_consuming_messages()
        rabbitmq_publisher.stop_publishing_messages()
        self.stop_notifying_control_center()
        super().connectionLost(reason)

    def onMessage(self, payload, isBinary):
        logger.info(f"Received a message: {payload}")
        if self.on_message_handler:
            reactor.callInThread(self.on_message_handler, payload)

    def start_notifying_control_center(self):
        self.is_notifying_control_center = True
        reactor.callInThread(self._notify_control_center)

    def stop_notifying_control_center(self):
        if self.is_notifying_control_center and notify_control_center_queue.empty():
            logger.info("Notify Control Center Queue processing stopped")
            notify_control_center_queue.put(None)

    def _notify_control_center(self):
        logger.info("Notify Control Center Queue processing started")
        while True:
            message = notify_control_center_queue.get()
            if message is None:
                logger.info("None in notify_control_center_queue")
                break
            self.safe_message_send(message)
        self.is_notifying_control_center = False

    def safe_message_send(self, message):
        try:
            self.sendMessage(message)
            logger.info(f"Message sent: {message}")
        except Exception as e:
            logger.error(f"Client connection lost because of: {e}.. retrying ..")
            AgentWebSocketFactory.get_instance().retry()


class AgentWebSocketFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = AgentWebSocketClient.init
    _instance = None
    maxDelay = 10.0

    @staticmethod
    def get_instance():
        if not AgentWebSocketFactory._instance:
            AgentWebSocketFactory._instance = AgentWebSocketFactory(
                resolve_ws_endpoint()
            )
        return AgentWebSocketFactory._instance

    def clientConnectionFailed(self, connector, reason):
        logger.error(f"Client connection failed because of: {reason}.. retrying ..")
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logger.error(f"Client connection lost because of: {reason}.. retrying ..")
        self.retry(connector)
