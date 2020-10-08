import requests
from urllib.parse import quote
from django.conf import settings
from appchance.client.api import CommonAPIClient


class ClientGraphQL(CommonAPIClient):
    """ GraphQL Client. Using GET for queries, POST for mutations
    """

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)

    @staticmethod
    def _prepare_query(root, params, extra, mutation=False):
        _str = f"{root}"
        if params:
            _str += f"({params})"
        if extra:
            _str += extra
        _str = "{"+_str+"}"
        if mutation:
            _str = "mutation" + _str
        if settings.DEBUG:
            print(_str)
        return _str

    def query(self, root, params, extra):
        kwargs = {"basic": self.basic} if self.basic else {}  # pylint: disable=no-member
        return self.do_request(
            "GET",
            self.endpoint,  # pylint: disable=no-member
            payload={"query": self._prepare_query(root, params, extra)},
            **kwargs)
    
    def mutation(self, root, params, extra):
        kwargs = {"basic": self.basic} if self.basic else {}  # pylint: disable=no-member
        return self.do_request(
            "POST",
            self.endpoint,  # pylint: disable=no-member
            payload={"query": self._prepare_query(root, params, extra, mutation=True)},
            **kwargs)
