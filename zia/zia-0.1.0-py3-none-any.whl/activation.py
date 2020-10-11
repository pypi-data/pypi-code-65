import logging

class Activation(object):
    def __init__(self, session):
        self.session = session
    def get_status(self):
        path = 'status'
        return self.session.get(path)
    def activate(self):
        path = 'status/activate'
        body = {}
        return self.session.post(path, body)


LOGGER = logging.getLogger(__name__)
