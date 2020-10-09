import time

from qary.etl.scrape_wikipedia import md5


def test_hash_speed():
    runtime = 0
    for i in range(10):
        t0 = time.time()
        for j in range(1000):
            md5('barackobama' + str(j), 16)
        t1 = time.time()
        runtime += (t1 - t0) / 1000 / 10
    assert runtime < 1e-4
    return runtime


def test_hash_consistency():
    assert md5("hello world") != md5("hello worlD")
    assert md5("hello world") != md5("Hello world")
    assert md5("hello world") == md5(b'hello world')
    assert md5("Barack Obama") == 4560975168341313090
    assert md5("barack obama") == 4205506257154982495


if __name__ == '__main__':
    test_hash_consistency()
    test_hash_speed()
