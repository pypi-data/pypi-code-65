from threading import Lock


class Singleton:
    _instance = None

    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                cls._instance = super().__new__(cls, *args, **kwargs)
        return cls._instance

