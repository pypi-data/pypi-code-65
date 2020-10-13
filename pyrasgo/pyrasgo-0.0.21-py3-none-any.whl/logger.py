class Logger():
    '''
    This is a shell logger to replace amplitude
    This gets instantiated in the connection script as _event_logger
    At the time we upgrade to Heap, we should kill this and switch _self_logger to the right Heap object
    '''
    def __init__(self):
        pass

    def turn_off_logging(self, *args, **kwargs):
        pass

    def create_event(self, *args, **kwargs):
        pass

    def log_event(self, *args, **kwargs):
        pass