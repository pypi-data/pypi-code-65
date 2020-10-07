from typing import List

from hyperfoil.defaults import DefaultClient, DefaultResource
from hyperfoil.resources import RunResource, BenchmarkResource


class BenchmarkClient(DefaultClient):
    def __init__(self, parent=None, instance_klass=None):
        super().__init__(parent, instance_klass=instance_klass)

    @property
    def url(self):
        return self.hyperfoil_client.url + '/benchmark'

    def list(self, **kwargs) -> List[DefaultResource]:
        response = self.rest.get(url=self.url, **kwargs)
        return [self._instance_klass(self, entity_id=name) for name in response.json()]

    def create(self, params: dict = None, **kwargs):
        response = self.rest.post(url=self.url, json=params, **kwargs)
        return response.ok

    def read(self, name: str) -> BenchmarkResource:
        return self._instance_klass(client=self, entity_id=name)

    def start(self, name: str, **kwargs):
        url = self.url + f"/{name}/start"
        response = self.rest.get(url=url, **kwargs)
        return self._create_instance(response, klass=RunResource, client=self.parent.run)


class RunClient(DefaultClient):
    def __init__(self, parent=None, instance_klass=None) -> None:
        super().__init__(parent, instance_klass)

    @property
    def url(self):
        return self.hyperfoil_client.url + '/run'

    def list(self, **kwargs) -> List[DefaultResource]:
        response = self.rest.get(url=self.url, **kwargs)
        return [self._instance_klass(self, entity_id=name) for name in response.json()]

    def read(self, run_id: str) -> RunResource:
        return self._instance_klass(client=self, entity_id=run_id)

    def kill(self, run_id: str, **kwargs) -> bool:
        url = self._entity_url(run_id) + '/kill'
        response = self.rest.get(url=url, **kwargs)
        return response.ok

    def is_finished(self, run_id: str) -> bool:
        run = self.read(run_id)
        return run.is_finished()

    def sessions(self, run_id: str, **kwargs) -> str:
        url = self._entity_url(run_id) + '/sessions'
        response = self.rest.get(url=url, **kwargs)
        # TODO: add test with run that takes longer time
        return response.content

    def recent_sessions(self, run_id: str, **kwargs):
        url = self._entity_url(run_id) + "/sessions/recent"
        response = self.rest.get(url=url, **kwargs)
        return response.json()

    def total_sessions(self, run_id: str, **kwargs) -> dict:
        url = self._entity_url(run_id) + '/sessions/total'
        response = self.rest.get(url=url, **kwargs)
        return response.json()

    def connections(self, run_id: str, **kwargs) -> str:
        url = self._entity_url(run_id) + '/connections'
        response = self.rest.get(url=url, **kwargs)
        return response.content.decode('utf-8')

    def all_stats(self, run_id: str, **kwargs) -> dict:
        headers = {'Accept': 'application/json'}
        url = self._entity_url(run_id) + '/stats/all'
        response = self.rest.get(url=url, headers=headers, **kwargs)
        return response.json()

    def recent_stats(self, run_id: str, **kwargs) -> dict:
        url = self._entity_url(run_id) + '/stats/recent'
        response = self.rest.get(url=url, **kwargs)
        return response.json()

    def total_stats(self, run_id: str, **kwargs) -> dict:
        url = self._entity_url(run_id) + '/stats/total'
        response = self.rest.get(url=url, **kwargs)
        return response.json()

    def custom_stats(self, run_id: str, **kwargs) -> dict:
        url = self._entity_url(run_id) + '/stats/custom'
        response = self.rest.get(url=url, **kwargs)
        return response.json()

    def histogram_stats(self, run_id: str, phase: str, step_id: int, metric: str, **kwargs) -> dict:
        # TODO: add tests
        params = {
            'phase': phase,
            'stepId': step_id,
            'metric': metric
        }
        url = self._entity_url(run_id) + '/stats/histogram'
        response = self.rest.get(url=url, params=params, **kwargs)
        return response.json()

    def benchmark(self, run_id: str, **kwargs) -> BenchmarkResource:
        url = self._entity_url(run_id) + '/benchmark'
        response = self.rest.get(url=url, **kwargs)
        return self._create_instance(response, klass=BenchmarkResource, client=self.parent.benchmark)


class UtilsClient(DefaultClient):
    def __init__(self, parent=None, instance_klass=None) -> None:
        super().__init__(parent, instance_klass)

    def agents(self, **kwargs) -> List[str]:
        url = self.url + '/agents'
        response = self.rest.get(url=url, **kwargs)
        return response.json()

    def log(self, **kwargs) -> str:
        url = self.url + '/log'
        response = self.rest.get(url=url, **kwargs)
        return response.content.decode('utf-8')

    def agent_logs(self, agent_name: str, **kwargs) -> str:
        url = self.url + '/log/' + agent_name
        response = self.rest.get(url=url, **kwargs)
        return response.content.decode('utf-8')

    def shutdown(self, **kwargs) -> bool:
        url = self.url + '/shutdown'
        response = self.rest.get(url=url, **kwargs)
        return response.ok

    def version(self, **kwargs) -> dict:
        url = self.url + '/version'
        response = self.rest.get(url=url, **kwargs)
        return response.json()
