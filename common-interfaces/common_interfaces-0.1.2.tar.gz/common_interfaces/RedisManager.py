from abc import ABC


class RedisManager(ABC):
    print("RedisManager")

    def insert(self, key, value):
        pass

    def queue_length(self):
        pass

    def pop(self):
        pass

    def set_value(self, key, value):
        pass

    def get_value(self, key):
        pass
