import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict
import math
from scipy import stats


def get_deviation(item, df):
    data = df[(df['item_code'] == item) & (df['unit_price'] > 0)]
    return np.std(data['unit_price'].apply(math.log) / max(data['unit_price'].apply(math.log))) if len(data) else 0


def get_qty(item, df):
    unique_prices = list(set(df[df['item_code'] == item]['unit_price']))
    mydict = {}

    for i in range(len(unique_prices)):
        mydict[unique_prices[i]] = sum(df[(df['item_code'] == item) & (df['unit_price'] == unique_prices[i])]['qty'])

    return mydict


def get_entropy(mydict):
    total = sum(mydict.values())
    entropy_list = [(val / total) for key, val in mydict.items()] if total else []
    return stats.entropy(entropy_list, base=2)


def get_variability(item, df):
    return get_deviation(item, df) * get_entropy(get_qty(item, df))
