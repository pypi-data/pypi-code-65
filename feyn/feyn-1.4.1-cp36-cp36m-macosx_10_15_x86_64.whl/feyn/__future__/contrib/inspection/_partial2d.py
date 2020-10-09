"""
Functions for creating a 2D partial plot of an Abzu graph.
"""
import numpy as np
import matplotlib.pyplot as plt
import feyn

from typing import Dict, Union, Optional


def plot_partial2d(graph:feyn.Graph, data:"DataFrame", fixed:Dict[str, Union[int, float]], ax:Optional[plt.Axes]=None, resolution:int=1000) -> None:
    """
    Visualize the response of a graph to numerical inputs using a partial plot. Works for both classification and regression problems. The partial plot comes in two parts:

    1. A colored background indicating the response of the graph in a 2D space given the fixed values. A lighter color corresponds to a bigger output from the graph.
    2. Scatter-plotted data on top of the background. In a classification scenario, red corresponds to true positives, and blue corresponds to true negatives. For regression, the color gradient shows the true distribution of the output value. Two sizes are used in the scatterplot, the larger dots correspond to the data that matches the values in fixed and the smaller ones have data different from the values in fixed.

    Arguments:
        graph {feyn.Graph} -- The Abzu graph we want a partial plot of.
        data {DataFrame} -- The data that will be scattered in the graph.
        fixed {Dict[str, Union[int, float]]} -- Dictionary with values we fix in the graph. The key is a feature name in the graph and the value is a number that the feature is fixed to.

    Keyword Arguments:
        ax {Optional[plt.Axes.axes]} -- Optional matplotlib axes in which to make the partial plot. (default: {None})
        resolution {int} -- The resolution at which we sample the 2D feature space for the background. (default: {1000})

    Raises:
        ValueError: Raised if the graph features names minus the fixed value names are more than two, meaning that you need to fix more values to reduce the dimensionality and make a 2D plot possible.
        ValueError: Raised if one of the features you are trying to plot in a 2D space is a categorical.
    """
    plot = set(graph.features).difference(fixed.keys())
    if len(plot) > 2:
        raise ValueError("Not enough features fixed.")

    for gint in graph:
        if not gint.name in plot:
            continue
        if "in:" in gint.spec and "c" in gint.spec:
            raise ValueError("Cannot plot a categorical register.")

    true_output = data[graph.target]
    class_problem = False
    if "b" in graph[-1].spec:
        true_output = true_output.astype(bool)
        class_problem = True

    if ax is None:
        ax = plt.subplot()

    # Construct boolean index for the data that we actually scatter
    available_data = np.ones(len(data), dtype=bool)
    for key, value in fixed.items():
        available_data = available_data & (data[key] == value)

    x, y = plot
    scaledX, scaledY, gridX, gridY = _scale_xy(x, y, data, resolution)

    XX, YY = np.meshgrid(gridX, gridY)

    # Predict on synthetic for background
    pred_synth = graph.predict(_build_fixed(
        {x: XX.flatten(), y: YY.flatten()}, fixed
    ))
    ax.imshow(pred_synth.reshape((resolution, resolution)), alpha=0.4, origin="lower")

    present_kwargs = {"s": 25, "alpha": .9}
    missing_kwargs = {"s": 2, "alpha": .2}

    if np.any(available_data):
        if class_problem:
            ax.scatter(scaledX[available_data & true_output],  scaledY[available_data & true_output], c="red", **present_kwargs)
            ax.scatter(scaledX[available_data & ~true_output], scaledY[available_data & ~true_output], c="blue", **present_kwargs)
        else:
            ax.scatter(scaledX[available_data],  scaledY[available_data], c=true_output[available_data], cmap="bwr", **present_kwargs)

    if class_problem:
        ax.scatter(scaledX[~available_data & true_output],  scaledY[~available_data & true_output], c="red", **missing_kwargs)
        ax.scatter(scaledX[~available_data & ~true_output], scaledY[~available_data & ~true_output], c="blue", **missing_kwargs)
    else:
        ax.scatter(scaledX[~available_data],  scaledY[~available_data], c=true_output[~available_data], cmap="bwr", **missing_kwargs)

    # Label the graph and adjust axes
    n_labels = 7
    ax.set_xticks(np.linspace(scaledX.min(), scaledX.max(), n_labels))
    ax.set_xticklabels(np.round(np.linspace(data[x].min(), data[x].max(), n_labels), 1))

    ax.set_yticks(np.linspace(scaledY.min(), scaledY.max(), n_labels))
    ax.set_yticklabels(np.round(np.linspace(data[y].min(), data[y].max(), n_labels), 1))

    ax.set_xlabel(x)
    ax.set_ylabel(y)

def _scale_xy(xname, yname, data, resolution):
    """
    Return scaled data for plotting a scatter on top of an imshow.
    Also return the X, Y grid for the background image itself.
    """
    minX, maxX = data[xname].min(), data[xname].max()
    minY, maxY = data[yname].min(), data[yname].max()

    # Scaling for each column
    adjustX = (maxX - minX) * 0.05
    adjustY = (maxY - minY) * 0.05

    scaledX = data[xname] - minX + adjustX
    scaledX = (scaledX / (scaledX.max() + adjustX)) * resolution
    scaledY = data[yname] - minY + adjustY
    scaledY = (scaledY / (scaledY.max() + adjustY)) * resolution

    # Meshgrid for background
    gridX = np.linspace(minX-adjustX, maxX+adjustX, resolution)
    gridY = np.linspace(minY-adjustY, maxY+adjustY, resolution)

    return scaledX, scaledY, gridX, gridY

def _build_fixed(data:Dict[str, np.ndarray], fixed:Dict[str, Union[int, float]]) -> Dict[str, np.ndarray]:
    """
    Take a DataFrame and a Dictionary, and return a DataFrame that has been updated with with constant values from fixed.
    """
    ret = data.copy()
    target_shape = next(iter(ret.values())).shape
#    for datarrs in ret.values():
#        target_shape = datarrs.shape
#        break

    for key, value in fixed.items():
        ret[key] = np.full(target_shape, value)

    return ret
