from typing import List
from urllib.parse import urljoin

import requests

from hyperfoil import resources
from hyperfoil.clients import BenchmarkClient, RunClient, UtilsClient
from hyperfoil.errors import ApiClientError


class HyperfoilClient:
    def __init__(self, url: str) -> None:
        self._rest = RestApiClient(url=url)
        self._benchmark = BenchmarkClient(self, instance_klass=resources.Benchmark)
        self._run = RunClient(self, instance_klass=resources.Run)
        self._utils = UtilsClient(self)

    @property
    def hyperfoil_client(self) -> 'HyperfoilClient':
        return self

    @property
    def rest(self) -> 'RestApiClient':
        return self._rest

    @property
    def benchmark(self) -> 'BenchmarkClient':
        return self._benchmark

    @property
    def run(self) -> 'RunClient':
        return self._run

    @property
    def url(self) -> str:
        return self._rest.url

    def agents(self, **kwargs) -> List[str]:
        return self._utils.agents(**kwargs)

    def log(self, **kwargs) -> str:
        return self._utils.log(**kwargs)

    def agent_logs(self, agent_name: str, **kwargs) -> str:
        return self._utils.agent_logs(agent_name, **kwargs)

    def shutdown(self, **kwargs) -> bool:
        return self._utils.shutdown(**kwargs)

    def version(self, **kwargs):
        return self._utils.version(**kwargs)


class RestApiClient:
    def __init__(self, url: str, verify_ssl=False):
        self._url = url
        self._verify_ssl = verify_ssl

    @property
    def url(self) -> str:
        return self._url

    def request(self, method='GET', url=None, path='', params: dict = None,
                headers: dict = None, **kwargs):
        full_url = url if url else urljoin(self._url, path)
        headers = headers or {}
        params = params or {}
        response = requests.request(method=method, url=full_url, headers=headers,
                                    params=params, verify=self._verify_ssl, **kwargs)
        return self._process_response(response)

    def get(self, *args, **kwargs):
        return self.request('GET', *args, **kwargs)

    def post(self, *args, **kwargs):
        return self.request('POST', *args, **kwargs)

    @classmethod
    def _process_response(cls, response: requests.Response) -> requests.Response:
        # TODO: log
        if not response.ok:
            raise ApiClientError(response.status_code, response.content)
        return response
