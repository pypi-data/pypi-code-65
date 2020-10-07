from hyperfoil.defaults import DefaultResource, DefaultClient


class BenchmarkResource(DefaultResource):

    def __init__(self, client: DefaultClient = None, entity: dict = None, content_type: str = '',
                 entity_id: str = "") -> None:
        super().__init__(client, entity, content_type,
                         entity_id=entity_id or entity.get('name', '')
                         )

    def start(self):
        return self.client.start(self._entity_id)


class RunResource(DefaultResource):
    def __init__(self, client: DefaultClient = None, entity: dict = None, content_type: str = '',
                 entity_id: str = "") -> None:
        super().__init__(client, entity, content_type,
                         entity_id=entity_id or entity.get('id', '')
                         )

    def kill(self):
        return self.client.kill(self._entity_id)

    def is_finished(self) -> bool:
        return self.entity['cancelled'] or self.entity['completed']

    def sessions(self):
        return self.client.sessions(self._entity_id)

    def recent_sessions(self):
        return self.client.recent_sessions(self._entity_id)

    def total_sessions(self):
        return self.client.total_sessions(self._entity_id)

    def connections(self):
        return self.client.connections(self._entity_id)

    def all_stats(self):
        return self.client.all_stats(self._entity_id)

    def recent_stats(self):
        return self.client.recent_stats(self._entity_id)

    def total_stats(self):
        return self.client.total_stats(self._entity_id)

    def custom_stats(self):
        return self.client.custom_stats(self._entity_id)

    def histogram_stats(self, phase: str, step_id: int, metric: str):
        return self.client.histogram_stats(self._entity_id, phase=phase, step_id=step_id, metric=metric)

    def benchmark(self):
        return self.client.benchmark(self._entity_id)
