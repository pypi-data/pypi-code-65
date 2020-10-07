from hyperfoil.clients import RunClient, BenchmarkClient
from hyperfoil.resources import RunResource, BenchmarkResource


def test_create(benchmark, benchmark_yaml):
    assert benchmark.create(params=benchmark_yaml)
    mark = benchmark.reload(benchmark_yaml['name'])
    assert mark.entity == benchmark_yaml
    assert isinstance(mark, BenchmarkResource)
    assert isinstance(mark.client, BenchmarkClient)


def test_all(benchmark, benchmark_yaml):
    assert benchmark.create(params=benchmark_yaml)
    all_benchmarks = benchmark.list()
    filtered = list(filter(lambda x: x.get('name') == benchmark_yaml['name'], all_benchmarks))
    assert len(filtered) == 1
    assert filtered[0].entity == benchmark_yaml


def test_start(benchmark, benchmark_yaml):
    assert benchmark.create(params=benchmark_yaml)
    run = benchmark.start(benchmark_yaml['name'])
    assert run
    assert run['id']
    assert isinstance(run, RunResource)
    assert isinstance(run.client, RunClient)


def test_benchmark_with_file(benchmark, benchmark_file):
    files = {
        'benchmark': ('file-benchmark.hf.yaml', open('benchmarks/file-benchmark.hf.yaml')),
        'file': ('usernames.txt', open('benchmarks/usernames.txt')),
        'test': ('test.txt', open('benchmarks/test.txt'))
    }
    assert benchmark.create(files=files)
    run = benchmark.start(benchmark_file['name'])
    assert run
    assert run['id']
    assert isinstance(run, RunResource)
    assert isinstance(run.client, RunClient)
