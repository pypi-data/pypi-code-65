from basic_http.session import HttpSession
from basic_http.util.networking import get_details


class Http:
    def __init__(self):
        self.sessions = dict()

    def __getitem__(self, item: str):
        try:
            return self.sessions[item]
        except KeyError:
            return None

    def __str__(self):
        str_repr = str()
        for identifier, session_object in self.sessions.items():
            str_repr += 'Session at ' + identifier + ':\n'
            str_repr += str(session_object.to_dict()) + '\n\n'
        else:
            str_repr = str_repr[: -2]
        return str_repr

    def get_session(self, identifier: str, create_new: bool = False):
        session = HttpSession()
        try:
            session = self.sessions[identifier]
        except KeyError:
            if create_new:
                self.sessions[identifier] = session
        finally:
            return session

    def request(self, method: str, url: str, header=None, raw_body: str = '', **kwargs):
        request_details = get_details(url)
        session_identifier = request_details['host'] + ':' + request_details['port']

        session = self.get_session(session_identifier, True)
        response = session.request(method, url, header, raw_body, **kwargs)

        return response
