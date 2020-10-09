"""A graph is a path from some input registers to an output register.

The graph is a result of running a simulation. It is one of the many possible paths from the inputs to the output. It can be compared to a model in various other machine learning frameworks.
"""
import json
from pathlib import Path
from typing import AnyStr, TextIO, Union, Iterable, Optional

import numpy as np

import _feyn
import feyn

from ._graphmixin import GraphMetricsMixin

# Update this number whenever there are breaking changes to save/load
# (or to_dict/from_dict). Then use it intelligently in Graph.load.
SCHEMA_VERSION = "2020-02-07"

PathLike = Union[AnyStr, Path]


class Graph(_feyn.Graph, GraphMetricsMixin):
    """
    A Graph represents a single mathematical model which can be used used for predicting.

    The constructor is for internal use. You will typically use `QGraph[ix]` to pick graphs from QGraphs, or load them from a file with Graph.load().

    Arguments:
        size -- The number of nodes this graph contains. The actual nodes must be added to the graph after construction.
    """

    def __init__(self, size: int):
        """Construct a new 'Graph' object."""
        super().__init__(size)

        self.loss_value = np.nan
        self.age = 0

    def predict(self, X) -> np.ndarray:
        """
        Calculate predictions based on input values.

        >>> graph.predict({ "age": [34, 78], "sex": ["male", "female"] })
        [True, False]

        Arguments:
            X -- The input values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.

        Returns:
            np.ndarray -- The calculated predictions.
        """
        if type(X).__name__ == 'dict':
            for k in X:
                if type(X[k]).__name__ == 'list':
                    X[k] = np.array(X[k])

        # Magic support for pandas DataFrame
        if type(X).__name__ == "DataFrame":
            X = {col: X[col].values for col in X.columns}

        return super()._query(X, None)

    @property
    def edges(self) -> int:
        """Get the total number of edges in this graph."""
        return super().edge_count

    @property
    def depth(self) -> int:
        """Get the depth of the graph"""
        return self[-1].depth

    @property
    def target(self) -> str:
        """Get the name of the output node"""
        return self[-1].name

    @property
    def features(self):
        return [i.name for i in self if i.spec.startswith("in:")]

    def save(self, file: Union[PathLike, TextIO]) -> None:
        """
        Save the `Graph` to a file-like object.

        The file can later be used to recreate the `Graph` with `Graph.load`.

        Arguments:
            file -- A file-like object or path to save the graph to.
        """
        as_dict = self._to_dict()
        as_dict["version"] = SCHEMA_VERSION

        if isinstance(file, (str, bytes, Path)):
            with open(file, mode="w") as f:
                json.dump(as_dict, f)
        else:
            json.dump(as_dict, file)

    @staticmethod
    def load(file: Union[PathLike, TextIO]) -> "Graph":
        """
        Load a `Graph` from a file.

        Usually used together with `Graph.save`.

        Arguments:
            file -- A file-like object or a path to load the `Graph` from.

        Returns:
            Graph -- The loaded `Graph`-object.
        """
        if isinstance(file, (str, bytes, Path)):
            with open(file, mode="r") as f:
                as_dict = json.load(f)
        else:
            as_dict = json.load(file)

        return Graph._from_dict(as_dict)

    def __hash__(self):
        return super().__hash__()

    def __eq__(self, other):
        return other.__hash__() == self.__hash__()

    def __contains__(self, item:str):
        return item in [interaction.name for interaction in self]

    def fit(self, data, loss_function=_feyn.DEFAULT_LOSS, sample_weights=None):
        """
        Fit the `Graph` with the given data set. Unlike fitting a QGraph, this does not involve searching an infinite list or using the QLattice in any other way.

        The purpose of this function is to allow re-fitting the model to a different dataset, for example with different baserates, or for cross-validation of a chosen Graph.

        Arguments:
            data -- Training data including both input and expected values. Can be either a dict mapping register names to value arrays, or a pandas.DataFrame.
            loss_function -- Name of the loss function or the function itself. This is the loss function to use for fitting. Can either be a string or one of the functions provided in `feyn.losses`.
            sample_weights -- An optional numpy array of weights for each sample. If present, the array must have the same size as the data set, i.e. one weight for each sample

        """

        # Magic support for pandas DataFrame
        if type(data).__name__ == "DataFrame":
            data = {col: data[col].values for col in data.columns}

        loss_function = feyn.losses._get_loss_function(loss_function)
        if not hasattr(loss_function, "c_derivative"):
            raise ValueError("Loss function cannot be used for fitting, since it doesn't have a corresponding c derivative")

        self._fit(data, loss_function, sample_weights)


    def _fit(self, data, loss_function, sample_weights=None):
        out_reg = self[-1]
        Y = data[out_reg.name]

        out_reg._loss = loss_function.c_derivative

        predictions = super()._query(data, Y, sample_weights)
        losses = loss_function(Y.astype(float), predictions)
        if sample_weights is not None:
            losses *= sample_weights
        self.loss_value = np.mean(losses)

        return self.loss_value

    def _to_dict(self):
        nodes = []
        links = []
        for ix in range(len(self)):
            interaction = self[ix]
            nodes.append({
                "id": interaction._index,
                "spec": interaction.spec,
                "location": interaction._latticeloc,
                "peerlocation": interaction._peerlocation,
                "legs": len(interaction.sources),
                "strength": interaction._strength,
                "name": interaction.name,
                "state": interaction.state._to_dict()
            })
            for ordinal, src in enumerate(interaction.sources):
                if src != -1:
                    links.append({
                        'source': src,
                        'target': interaction._index,
                        'ord': ordinal
                    })

        return {
            'directed': True,
            'multigraph': True,
            'nodes': nodes,
            'links': links
        }

    def _repr_svg_(self):
        return feyn._current_renderer.rendergraph(self)

    def _repr_html_(self):
        return feyn._current_renderer.rendergraph(self)

    @staticmethod
    def _get_interaction(data: dict) -> _feyn.Interaction:
        interaction = feyn.Interaction(data["spec"], tuple(data["location"]), peerlocation=data["peerlocation"], strength=data["strength"], name=data["name"])
        interaction.state._from_dict(data["state"])

        return interaction

    @staticmethod
    def _from_dict(gdict):
        sz = len(gdict["nodes"])
        graph = Graph(sz)
        for ix, node in enumerate(gdict["nodes"]):
            interaction = Graph._get_interaction(node)
            graph[ix] = interaction

        for edge in gdict["links"]:
            interaction = graph[edge["target"]]
            ord = edge["ord"]
            interaction._set_source(ord, edge["source"])
        return graph


    def plot_summary(self, data:Iterable, test:Optional[Iterable]=None, corr_func:Optional[str]=None) -> "SVG":
        """
        Plot the graph's summary metrics and show the signal path.

        This is a shorthand for calling feyn.plots.plot_graph_summary.

        Arguments:
            data {Iterable} -- Data set including both input and expected values. Must be a pandas.DataFrame.

        Keyword Arguments:
            test {Optional[Iterable]} -- Additional data set including both input and expected values. Must be a pandas.DataFrame. (default: {None})
            corr_func {Optional[str]} -- Correlation function to use in showing the importance of individual nodes. Must be either "mi" or "pearson". (default: {None})

        Returns:
            SVG -- SVG of the graph summary.
        """
        return feyn.plots._graph_summary.plot_graph_summary(self, data, corr_func=corr_func, test=test)
