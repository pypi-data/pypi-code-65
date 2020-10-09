"""
Functions for creating a partial dependence plot of an Abzu graph.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import feyn
from typing import Iterable, Optional
from collections.abc import Iterable 

def _cartesian_product(arrays) -> np.ndarray:
    #Find the unique combination of all values
    la = len(arrays)
    dtype = np.result_type(*arrays)
    arr = np.empty([len(a) for a in arrays] + [la], dtype=dtype)
    for i, a in enumerate(np.ix_(*arrays)):
        arr[...,i] = a
    return arr.reshape(-1, la).T

def _update_with_cartesian_product( samples ):
    #Apply cartesian to samples
    value_arr = []
    column_arr = []
    for key, value in samples.items():
        column_arr.append(key)
        value_arr.append(value)

    total_df = _cartesian_product(value_arr)

    for idx, col in enumerate(column_arr):
        samples[ col ] = total_df[ idx ]

def _create_by_samples( data: np.ndarray, n_samples: int = 100 ) -> np.ndarray:
    #Let the "by" variable vary from min to max of the variables values
    if data.dtype == 'object':
        return np.unique(data)

    return np.linspace(np.min(data), np.max(data), n_samples)


def _create_samples( data: np.ndarray ) -> np.ndarray:
    #Find fixed values for remaining features in graph.

    #For catgorical features apply the 3 most frequent categories
    if data.dtype == 'object':

        return np.unique(data)[:3]
      
    else:
        #For numerical features find the the 10, 50 and 90 percentiles
        rounded_quantiles = [np.round(np.quantile(data, x), 2) for x in [0.1, 0.5, 0.9]]
        return np.unique(rounded_quantiles)


def _to_numpy_array( something ):
    #Fix formatting
    if isinstance(something, str):
        return np.array([something])
    if isinstance(something, Iterable):
        return np.array(something)

    return np.array([something])

def plot_partial_dependence(graph:feyn.Graph, data:Iterable, by:str, fixed:Optional[dict] = None) -> None:
   
    """
    Plot a partial dependence plot. 

    This plot is useful to interpret the effect of a specific feature on the model output.

    Example:
    > qg = qlattice.get_regressor(["age","smoker","heartrate"], output="heartrate")
    > qg.fit(data)
    > best = qg[0]
    > feyn.__future__.contrib.inspection._partial_dependence.plot_partial_dependence(best, data, by="age")

    You can use any column in the dataset as the `by` parameter.
    If you use a numerical column, the feature will vary from min to max of that varialbe in the training set.
    If you use a categorical column, the feature will display all categories, sorted by the average prediction of that category.

    Arguments:
        graph -- The graph to plot.
        data -- The dataset to measure the loss on.
        by -- The column in the dataset to interpret by.
        fixed -- A dictionary of features and associated values to hold fixed
    """

    # Accept pandas dataframes
    if type(data).__name__ == "DataFrame":
        data = { col: data[col].values for col in data.columns }

    # Ensure fixed is a dict with numpy arrays
    fixed = {
        key: _to_numpy_array(val) \
            for key, val in fixed.items()
    } if fixed is not None else {}
    
    #Point to the target
    target = graph[-1].name

    #Point to features in the chosen graph that for our plots needs to be fixed
    cols = [ col for col in graph.features if col not in [by] ]

    samples = {
        col : fixed[col] if col in fixed else _create_samples(data[col]) \
            for col in cols
    }
    samples[by] = _create_by_samples(data[by])

    _update_with_cartesian_product(samples)

    # Make unique ids for each combination of fixed values for plotting
    samples['id'] = ''
    first=True
    for col in cols:
        print(samples[col].dtype)
        print(col)
        if first:
            first = False
        else:
            samples['id'] = np.char.add(samples['id'], ', ')
        
        if samples[col].dtype == 'object':
            samples['id'] = np.char.add(samples['id'], samples[col])

        else:
            samples['id'] = np.char.add(samples['id'], np.round(samples[col],2).astype('U'))
            
    # Perform predictions on the new values
    samples['preds'] = graph.predict(samples)

    #palette = plt.get_cmap('tab20')
    palette = ListedColormap(feyn.plots._themes.AbzuColors._abzu_colors.values())

    
    import pandas as pd

    total_df = pd.DataFrame(samples).sort_values( by='id' )

    #Distinguish between numerical and categorical plots
    if data[by].dtype == 'object':
        sort_df = total_df.groupby(by).agg(preds_sort = ('preds', 'mean')).reset_index()

        total_df = pd.merge(total_df, sort_df, on = by, suffixes = (False, False)).sort_values('preds_sort')

        for i, group in enumerate(total_df.id.sort_values().unique()):
            scatter_df = total_df[total_df.id == group]
            plt.scatter(scatter_df['preds'], scatter_df[by], color = palette(i), label = group)
        plt.xlabel(f"Predicted {target}")
        plt.title(f"'{by}' on '{target}'")
        #plt.grid(axis = 'x')
        plt.legend(title = cols, loc='center left', bbox_to_anchor=(1, 0.5))

    else:
        for i, group in enumerate(total_df.id.unique()):
            line_df = total_df[total_df.id == group].sort_values(by)
            plt.plot(line_df[by], line_df['preds'], color = palette(i), label = group, linewidth = 1.5)
        plt.xlabel(by)
        plt.ylabel(f"Predicted {target}")
        plt.title(f"'{by}' on '{target}'")
        plt.legend(title = cols, loc='center left', bbox_to_anchor=(1, 0.5))