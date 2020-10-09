class Event:
    EVENT_HANDLERS = {}

    @classmethod
    def add_handler(cls, event_type, function):
        if event_type not in cls.EVENT_HANDLERS:
            cls.EVENT_HANDLERS[event_type] = []
        cls.EVENT_HANDLERS[event_type].append(function)

    @classmethod
    def trigger_event(cls, event_type, *args, **kwargs):
        for function in cls.EVENT_HANDLERS.get(event_type, []):
            function(*args, **kwargs)

    def __call__(self, function):
        self.function = function
        self.__class__.add_handler(self.event_type, self.function)

    def __init__(self, event_type):
        self.event_type = event_type

