import pandas as pd
import numpy as np


def create_demo_df():
    a = np.array([i for i in range(20)]).reshape(-1, 2)
    df = pd.DataFrame(a, columns=['x', 'y'])
    return df
