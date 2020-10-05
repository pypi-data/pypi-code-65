from typing import Dict

import yaml


class BenchmarkFactory:
    def __init__(self, benchmark: Dict = None):
        if benchmark is None:
            benchmark = {}
        self._benchmark = {'http': [], **benchmark}

    def create(self):
        return self._benchmark

    def load_benchmark(self, stream) -> 'BenchmarkFactory':
        benchmark = yaml.load(stream, Loader=yaml.Loader)
        self._benchmark.update(benchmark)
        return self

    def add_host(self, host: str, shared_connections: int, **kwargs) -> 'BenchmarkFactory':
        self._benchmark['http'].append({
            'host': host,
            'sharedConnections': shared_connections,
            **kwargs
        })
        return self
