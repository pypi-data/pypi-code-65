import random 
from collections import Counter
from itertools import accumulate

import matplotlib.pyplot as plt

def sample_from_dataset(dataset, n=None, ratio=None):
    if not n and not ratio:
        print('Please enter #samples or ratio.')
        return 

    if n:
        return random.sample(dataset, n)
    elif ratio:
        return random.sample(dataset, int(ratio*len(dataset)))

def get_batches(dataset, bs):
    n = len(dataset) // bs
    rmd = len(dataset) % bs
    n += int(rmd != 0)
    for i in range(n):
        lo = i*bs
        hi = min((i+1)*bs, len(dataset))
        yield dataset[lo:hi]

def view_dict_info(d):
    print('-'*40)
    for key, value in d.items():
        print(f'{key}: {type(value)}')
    print('-'*40)

def view_counter_info(data):
    cnter = Counter(data)
    values, cnts = zip(*cnter.most_common())
    cnts_per = [c/sum(cnts) for c in cnts]
    cnts_per_cum = list(accumulate(cnts_per))

    print('-'*60)
    print(f'#total items: {len(values)}')
    for v, c, per, per_cum in zip(values, cnts, cnts_per, cnts_per_cum):
        print(f'{v:<6} {c:<6} {per:.4f} {per_cum:.4f}')
    print('-'*60)

    plt.plot(cnts_per)
    plt.show()
    return cnter