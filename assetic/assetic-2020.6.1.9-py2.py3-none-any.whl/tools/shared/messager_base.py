import logging
from abc import ABC, abstractmethod


class MessagerBase(ABC):

    def __init__(self):
        self.logger = logging.getLogger(__name__)

    @abstractmethod
    def new_message(self, msg):
        pass
