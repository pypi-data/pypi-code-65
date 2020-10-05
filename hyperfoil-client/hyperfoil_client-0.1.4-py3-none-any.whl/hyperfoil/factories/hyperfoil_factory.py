import csv
from io import StringIO

import yaml

from hyperfoil import HyperfoilClient
from hyperfoil.resources import BenchmarkResource


class HyperfoilFactory:
    def __init__(self, client: 'HyperfoilClient'):
        self._client = client
        self._benchmark = {}
        self._files = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        for _, stream in self._files.values():
            stream.close()

    def create(self) -> 'BenchmarkResource':
        self._client.benchmark.create(files=self._files)
        return self._client.benchmark.read(self._benchmark['name'])

    def benchmark(self, benchmark: dict) -> 'HyperfoilFactory':
        self._benchmark = benchmark
        file = StringIO()
        yaml.dump(benchmark, file)
        file.seek(0)
        self.file('benchmark', file)
        return self

    def file(self, file_name: str, stream) -> 'HyperfoilFactory':
        if file_name in self._files:
            stream.close()
            raise Exception('File already loaded')
        self._files[file_name] = (file_name, stream)
        return self

    def csv_data(self, file_name: str, rows: [[str]], **kwargs) -> 'HyperfoilFactory':
        file = StringIO()
        csv_writer = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL, **kwargs)
        csv_writer.writerows(rows)
        file.seek(0)
        self.file(file_name, file)
        return self
