import collections
from typing import Dict, Iterator

import yaml


class Benchmark(collections.abc.MutableMapping):
    def __init__(self, benchmark: Dict = None):
        if benchmark is None:
            benchmark = {}
        self._benchmark = {'http': [], **benchmark}

    def __setitem__(self, key: str, value) -> None:
        self._benchmark[key] = value

    def __delitem__(self, key: str) -> None:
        del self._benchmark[key]

    def __getitem__(self, key: str):
        return self._benchmark.get(key)

    def __len__(self) -> int:
        return len(self._benchmark)

    def __iter__(self) -> Iterator:
        return iter(self._benchmark)

    def load_benchmark(self, stream):
        benchmark = yaml.load(stream, Loader=yaml.Loader)
        self._benchmark.update(benchmark)

    def load_benchmark_file(self, path: str):
        with open(path, 'r') as file:
            self.load_benchmark(file)

    def add_host(self, host: str, shared_connections: int, **kwargs):
        self._benchmark['http'].append({
            'host': host,
            'sharedConnections': shared_connections,
            **kwargs
        })

    def update(self, benchmark=None, **kwargs):
        self._benchmark.update(benchmark, **kwargs)

    def create(self):
        return self._benchmark
