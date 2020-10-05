from dataclasses import dataclass
import pandas as pd
import time


@dataclass
class Measure:
    name: str = ''
    min: int = int(1e12)
    mean: int = 0
    total: int = 0
    max: int = 0
    last: int = 0
    count: int = 1

    data : pd.DataFrame = None

    def __str__(self):
        return f'{self.name}: {self.last} <{self.min},{self.mean},{self.max}> ns'

    def update(self, measure):
        self.count += 1
        if measure < self.min:
            self.min = measure
        elif measure > self.max:
            self.max = measure
        self.total += measure
        self.mean = int(self.total / self.count)
        self.last = measure

    def reset(self):
        self.count = 0
        self.total = 0


class Performance:
    stats = dict()
    _ms: int = int(1e-6)

    def __getitem__(self, key):
        return self.stats[key]

    def new(self, name, time):
        if name not in self.stats:
            self.stats[name] = Measure(name=name, min=time, mean=time, max=time, last=time)
        else:
            self.stats[name].update(time)

    def collect(method):
        def measure(*args, **kw):
            self = args[0]
            ts = time.time_ns()
            result = method(*args, **kw)
            self.performance.new(method.__name__, time.time_ns() - ts)
            return result
        return measure

