from autobahn.twisted.websocket import connectWS
from twisted.internet import reactor

from agent.logger import setup_logger
from agent.rabbitmq.setup import setup_rabbitmq
from agent.websocket.client import AgentWebSocketFactory

logger = setup_logger()


def main():
    logger.info("Launching Agent...")
    setup_rabbitmq()
    connectWS(AgentWebSocketFactory.get_instance())
    reactor.run()


if __name__ == "__main__":
    main()
