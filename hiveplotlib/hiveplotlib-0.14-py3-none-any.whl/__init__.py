# Gary Koplik
# gary<dot>koplik<at>geomdata<dot>com
# August, 2020
# __init__.py

"""
Generates the necessary structure for constructing visualizations.
"""

import pandas as pd
from typing import Hashable
from .utils import *
import warnings


class Node:
    """
    Node object
    """

    def __init__(self, unique_id: Hashable, data: dict or None = None):
        """
        Initialize `Node` object with a unique Hashable label for identification and data if prepared
        (but can always be added later with the `add_data()` method

        :param unique_id: identifier for the instance (intended to be unique)
        :param data: dictionary of data

        Example
        -------
        >>> my_node = Node(unique_id="my_unique_node_id", data=data)
        """

        self.unique_id = unique_id
        self.data = None
        self.add_data(data)
        # Hashable value that points to which `Axis` instance the node is assigned to
        #  (this will point to an `Axis` instance via `HivePlot.axes[label]`)
        self.axis_label = None

    def add_data(self, data: dict):
        """
        Add dictionary of data to `self.data`

        :param data:
        :return: None
        """

        if data is None:
            self.data = None
        else:
            assert type(data) == dict, \
                "`data` must be dictionary."

            self.data = data

        return None


class Axis:
    """
    Axis object
    """

    def __init__(self, axis_id: Hashable, start: float = 0, end: float = 1, angle: float = 0,
                 long_name: str or None = None):
        """
        Initialize `Axis` object with start and end positions and angle. Default to axis normalized on [0, 1]

        :param axis_id: unique name for `Axis` instance
        :param start: point closest to the center of the plot (using the same positive number for multiple axes in a
            Hive Plot is a nice way to space out the figure)
        :param end: point farthest from the center of the plot
        :param angle: angle to set the axis, in degrees (moving counterclockwise, e.g.
            0 degrees points East, 90 degrees points North).
        :param long_name: longer name for use when labeling on graph (but not for referencing the axis).
            Default `None` sets it to `axis_id`

        Example
        -------
        >>> # 3 axes, spaced out 120 degrees apart, all size 4, starting 1 unit off of origin
        >>> axis0 = Axis(axis_id="axis0", start=1, end=5, angle=0)
        >>> axis1 = Axis(axis_id="axis1", start=1, end=5, angle=120)
        >>> axis2 = Axis(axis_id="axis2", start=1, end=5, angle=240)
        """

        self.axis_id = axis_id

        if long_name is None:
            self.long_name = str(axis_id)
        else:
            self.long_name = str(long_name)

        # keep internal angle in [0, 360)
        self.angle = angle % 360

        self.polar_start = start
        self.start = polar2cartesian(self.polar_start, self.angle)

        self.polar_end = end
        self.end = polar2cartesian(self.polar_end, self.angle)

        # key from each node's data dictionary that we will use to position the node along the `Axis`
        self.node_placement_label = None

        # hold all the cartesian coordinates, polar rho, and corresponding labels in a pandas dataframe
        self.node_placements = pd.DataFrame(columns=['x', 'y', 'unique_id', 'rho'])

    def set_node_placements(self, x: List, y: List, node_ids: List, rho: List):
        """
        set `self.node_placements` to an array of:
            - x cartesian coordinates
            - y cartesian coordinates, and
            - unique node IDs
            - polar rho component (distance from the origin)

        :param x: array of x cartesian coordinates
        :param y: array of y cartesian coordinates corresponding to x coordinates
        :param node_ids: array of unique node IDs corresponding to x and y coordinates
        :param rho: array of polar coordinate distance values corresponding to x, y, and unique ID values
        :return:
        """

        assert np.array(x).shape[0] == np.array(y).shape[0] == np.array(node_ids).shape[0] == np.array(rho).shape[0], \
            "Must provide the same number of x values, y values, and node IDs"

        self.node_placements = pd.DataFrame.from_dict({'x': x, 'y': y, 'unique_id': node_ids, 'rho': rho})

        return None

    def set_node_placement_label(self, label: Hashable):
        """
        Set the key for which the value in `self.data` will decide the placement of the node on the axis

        :param label: which key in `self.data` to reference
        :return:
        """
        self.node_placement_label = label

        return None


class HivePlot:
    """
    Hive Plots built from combination of `Axis` and `Node` instances
    """

    def __init__(self):
        """
        Initialize HivePlot object
        """

        # keep dictionary of axes so we can find axes by label
        self.axes = dict()

        # keep dictionary of nodes with keys as unique IDs
        self.nodes = dict()

        # maintain dictionary of node assignments to axes
        #  (note, this may not always be a partition, e.g. repeat axis)
        self.node_assignments = dict()

        # maintain dictionary of dictionaries of edges with three keys
        #   "ids" : (n, 2) numpy arrays where each row represents a single edge, represented by unique node ids:
        #   >>> HivePlot.edges[<source_axis_id>][<sink_axis_id>]["ids"]
        #   "curves" : discretized edges for plotting numpy arrays of edges in Cartesian space will be stored by:
        #   >>> HivePlot.edges[<source_axis_id>][<sink_axis_id>]["curves"]
        #   "edge_kwargs" : matplotlib line kwargs for plotting the edges later stored by:
        #   >>> HivePlot.edges[<source_axis_id>][<sink_axis_id>]["edge_kwargs"]
        # with nested keys "ids" or "curves" past
        self.edges = dict()

    def add_axes(self, axes: List):
        """
        Add list of `Axis` instances to `self.axes`.
        Note: all resulting Axis IDs must be unique.

        :param axes: `Axis` objects to add to `HivePlot` instance.
        :return: None
        """

        current_ids = list(self.axes.keys())
        new_ids = [axis.axis_id for axis in axes]
        combined_ids = current_ids + new_ids
        assert len(combined_ids) == len(set(combined_ids)), \
            "New specified axis IDs combined with existing IDs led to non-unique IDs. Not adding specified axes."

        for axis in axes:
            self.axes[axis.axis_id] = axis
            self.node_assignments[axis.axis_id] = None
        return None

    def add_nodes(self, nodes: List, check_uniqueness: bool = True):
        """
        Add `Node` instances to `self.nodes`

        :param nodes: collection of `Node` instances, will be added to `self.nodes` dict with unique IDs as keys
        :param check_uniqueness: whether to formally check for uniqueness.
            WARNING: the only reason to turn this off is if the dataset becomes big enough that this operation becomes
            expensive, and you have already established uniqueness another way (for example, you are pulling data from
            a database and using the db key as the unique ID). If you add non-unique IDs with `check_uniqueness=False`,
            we make no promises about output.
        :return: None
        """

        # make sure id's are unique or things could break later
        if check_uniqueness:
            current_ids = list(self.nodes.keys())
            new_ids = [node.unique_id for node in nodes]
            combined_ids = current_ids + new_ids
            assert len(combined_ids) == len(set(combined_ids)), \
                "New specified IDs combined with existing IDs led to non-unique IDs. Not adding specified nodes."

        for node in nodes:
            self.nodes[node.unique_id] = node

        return None

    def allocate_nodes_to_axis(self, unique_ids: List, axis_id: Hashable):
        """
        Allocate a set of nodes (pointers by unique node id's) to a single axis (specified by a unique axis_id).
        Note, this is NOT sufficient for plotting nodes. Once allocated, you must then sort the nodes on the axis
        to then place them on the axis (via `HivePlot.sort_nodes_on_axis()`).

        :param unique_ids: list of node IDs to place on specified axis
        :param axis_id: unique ID of axis in HivePlot instance on which we want to place nodes
        :return:
        """

        self.node_assignments[axis_id] = unique_ids

        return None

    def place_nodes_on_axis(self, axis_id: Hashable, unique_ids: List or None = None,
                            sorting_feature_to_use: Hashable or None = None,
                            vmin: float or None = None, vmax: float or None = None):
        """
        Set node positions on specific axis. Cartesian coordinates will be normalized to specified `vmin` and `vmax`,
        then those `vmin` and `vmax` values will be normalized to span the length of the axis when plotted.

        :param axis_id: which axis (as specified by key from `self.axes`) for which to plot nodes
        :param unique_ids: list of node IDs to assign to this axis. If previously set with
            `HivePlot.allocate_nodes_to_axis()`, this will overwrite those node assignments. If `None`, method will
            check and confirm there are existing node ID assignments.
        :param sorting_feature_to_use: which feature in the node data to use to align nodes on an axis.
            Default `None` uses the feature previously assigned via `HivePlot.axes[axis_id].set_node_placement_label()`.
        :param vmin: all values less than `vmin` will be set to `vmin`. Default `None` sets as global minimum
        :param vmax: all values greater than `vmax` will be set to `vmin`. Default `None` sets as global maximum
        :return: None
        """

        # ToDo: allow rescaling option before thresholding on min and max values (e.g. put in log scale)

        if unique_ids is None:
            assert self.node_assignments[axis_id] is not None, \
                f"No existing node IDs assigned to axis {axis_id}. Please provide `unique_ids` to place on this axis."
        else:
            self.allocate_nodes_to_axis(unique_ids=unique_ids, axis_id=axis_id)

        # assign which data label to use
        if sorting_feature_to_use is not None:
            self.axes[axis_id].set_node_placement_label(label=sorting_feature_to_use)

        else:
            assert self.axes[axis_id].node_placement_label is not None, \
                "Must either specify which feature to use in " + \
                "`HivePlot.place_nodes_on_axis(feature_to_use=<Hashable>)` " + \
                "or set the feature directly on the `Axis.set_node_placement_label(label=<Hashable>)`."

        axis = self.axes[axis_id]

        assert axis.node_placement_label is not None, \
            "Must choose a node feature on which to order points with `Axis.set_node_placement_label()`"

        all_node_ids = self.node_assignments[axis_id]
        all_vals = np.array([self.nodes[node_id].data[axis.node_placement_label]
                             for node_id in all_node_ids]).astype(float)

        if vmin is None:
            vmin = np.min(all_vals)
        if vmax is None:
            vmax = np.max(all_vals)

        # handle case of one point on an axis but no vmin or vmax specified (put it at the midpoint)
        if all_vals.size == 1 and vmin == vmax:
            vmin -= 1
            vmax += 1

        # handle case of one unique value on an axis but no vmin or vmax specified (put it at the midpoint)
        if np.unique(all_vals).size == 1 and vmin == vmax:
            vmin -= 1
            vmax += 1

        # scale values to [vmin, vmax]
        all_vals[all_vals < vmin] = vmin
        all_vals[all_vals > vmax] = vmax

        # normalize to vmin = 0, vmax = 1
        all_vals -= vmin
        all_vals /= (vmax - vmin)
        # scale to length of axis
        all_vals *= np.abs(axis.polar_end - axis.polar_start)
        # shift to correct starting point which could be off the origin
        all_vals += axis.polar_start

        # translate into cartesian coords
        x_coords, y_coords = polar2cartesian(all_vals, axis.angle)

        # update pandas dataframe of cartesian coordinate information and polar rho coordinates
        axis.set_node_placements(x=x_coords, y=y_coords, node_ids=all_node_ids, rho=all_vals)

        # remove any curves that were previously pointing to this axis
        #  (since they were based on a different alignment of nodes)
        for a0 in list(self.edges.keys()):
            for a1 in list(self.edges[a0].keys()):
                if a0 == axis_id and "curves" in self.edges[a0][a1]:
                    del self.edges[a0][a1]["curves"]
                elif a1 == axis_id and "curves" in self.edges[a0][a1]:
                    del self.edges[a0][a1]["curves"]

        return None

    def reset_edges(self):
        """
        Reset `self.edges` i.e. delete any stored connections between axes previously computed.

        :return: None
        """

        self.edges = dict()

        return None

    def __store_edge_ids(self, edge_ids: np.ndarray, from_axis_id: Hashable, to_axis_id: Hashable):
        """
        Store edge ids to self.edges (e.g. the unique identifiers of nodes "from" and "to" for each edge).

        :param edge_ids: node IDs of "from" and "to" nodes
        :param from_axis_id: ID of axis that nodes are coming "from"
        :param to_axis_id: ID of axis that nodes are going "to"
        :return: None
        """

        # initialize nested dicts if not there
        from_keys = list(self.edges.keys())
        if from_axis_id not in from_keys:
            self.edges[from_axis_id] = dict()
            self.edges[from_axis_id][to_axis_id] = dict()

        to_keys = list(self.edges[from_axis_id].keys())
        if to_axis_id not in to_keys:
            self.edges[from_axis_id][to_axis_id] = dict()

        self.edges[from_axis_id][to_axis_id]["ids"] = edge_ids

        return None

    def add_edge_ids(self, edges: np.ndarray, axis_id_1: Hashable, axis_id_2: Hashable,
                     a1_to_a2: bool = True, a2_to_a1: bool = True):
        """
        Find the subset of network connections (edges) that involve nodes currently on `axis_id_1` and `axis_id_2`.

        Generates (j, 2) and (k, 2) numpy arrays of axis_1 to axis_2 connections and axis_2 to axis 1 connections (or
        only 1 of those arrays depending on parameter choices for `a1_to_a2` and `a2_to_a1`.

        These resulting numpy arrays of edge IDs (e.g. each row is a [<FROM ID>, <TO ID>] edge) will be stored
        automatically in `self.edges`, a dictionary of dictionaries of discretized edges, which can later be
        converted for plotting numpy arrays of edges in Cartesian space. They are stored as
        `self.edges[<source_axis_id>][<sink_axis_id>]["ids"]`.

        :param edges: (n, 2) array of Hashables representing pointers to specific `Node` instances.
            The first column is the "from" and the second column is the "to" for each connection.
        :param axis_id_1: Hashables pointer to first `Axis` instance in `self.axes` we want to find connections between.
        :param axis_id_2: Hashables pointer to second `Axis` instance in `self.axes` we want to find connections
            between.
        :param a1_to_a2: whether to find the connections going FROM axis_id_1 TO axis_id_2
        :param a2_to_a1: whether to find the connections going FROM axis_id_2 TO axis_id_1
        :return: None
        """

        # axis 1 to axis 2
        if a1_to_a2:
            a1_input = np.isin(edges[:, 0], self.axes[axis_id_1].node_placements.values[:, 2])
            a2_output = np.isin(edges[:, 1], self.axes[axis_id_2].node_placements.values[:, 2])
            a1_to_a2 = np.logical_and(a1_input, a2_output)
            self.__store_edge_ids(edge_ids=edges[a1_to_a2], from_axis_id=axis_id_1, to_axis_id=axis_id_2)

        # axis 2 to axis 1
        if a2_to_a1:
            a1_output = np.isin(edges[:, 1], self.axes[axis_id_1].node_placements.values[:, 2])
            a2_input = np.isin(edges[:, 0], self.axes[axis_id_2].node_placements.values[:, 2])
            a2_to_a1 = np.logical_and(a2_input, a1_output)
            self.__store_edge_ids(edge_ids=edges[a2_to_a1], from_axis_id=axis_id_2, to_axis_id=axis_id_1)

        return None

    def add_edge_curves_between_axes(self, axis_id_1: Hashable, axis_id_2: Hashable,
                                     a1_to_a2: bool = True, a2_to_a1: bool = True,
                                     num_steps: int = 100, short_arc: bool = True):
        """
        Add edge curves to self.edges (e.g. the Cartesian coordinates of discretized bezier curves of
        edges to be plotted) between two axes of a HivePlot.

        Note: expected to have run `self.find_edge_ids()` first for the two axes of interest.

        Resulting discretized bezier curves will be stored as an (n, 2) numpy ndarray of multiple sampled curves where
        the first column is x position and the second column is y position. NOTE: curves are separated by rows of
        `[None, None]`, which allow matplotlib to accept the entire array when plotting lines via `plt.plot()`.

        This output will be stored in `self.edges[axis_id_1][axis_id_2]["curves"]`.

        :param axis_id_1: Hashable pointer to the first `Axis` instance in `self.axes` we want to find connections
            between.
        :param axis_id_2: Hashable pointer to the second `Axis` instance in `self.axes` we want to find connections
            between.
        :param a1_to_a2: whether to find the connections going FROM axis_id_1 TO axis_id_2
        :param a2_to_a1: whether to find the connections going FROM axis_id_2 TO axis_id_1
        :param num_steps: number of points sampled along a given Bezier curve. Larger numbers will result in
            smoother curves when plotting later, but slower rendering.
        :param short_arc: whether to take the shorter angle arc (True) or longer angle arc (False).
            There are always two ways to traverse between axes: with one angle being x, the other option being 360 - x.
            For most visualizations, the user should expect to traverse the "short arc," hence the default True.
            For full user flexibility, however, we offer the ability to force the arc the other direction, the
            "long arc" (`short_arc = False`). Note: in the case of 2 axes 180 degrees apart, there is no "wrong" angle,
            so in this case an initial decision will be made, but switching this boolean will switch the arc to the
            other hemisphere.
        :return: None
        """

        all_connections = []
        direction = []
        if a1_to_a2:
            try:
                temp_connections = self.edges[axis_id_1][axis_id_2]["ids"].copy().astype("O")
                all_connections.append(temp_connections)
                direction.append("a1_to_a2")
            except KeyError:
                raise KeyError("`self.edges[axis_id_1][axis_id_2]['ids']` does not appear to exist. " +
                               "It is expected you have run `self.add_edge_ids()` first for the two axes of interest."
                               )
        if a2_to_a1:
            try:
                temp_connections = self.edges[axis_id_2][axis_id_1]["ids"].copy().astype("O")
                all_connections.append(temp_connections)
                direction.append("a2_to_a1")
            except KeyError:
                raise KeyError("`self.edges[axis_id_2][axis_id_1]['ids']` does not appear to exist. " +
                               "It is expected you have run `self.add_edge_ids()` first for the two axes of interest."
                               )

        if len(all_connections) == 0:
            raise ValueError("One of `a1_to_a2` or `a2_to_a1` must be true.")

        for connections, edge_direction in zip(all_connections, direction):

            # left join the flattened start and stop values array with the cartesian and polar node locations
            #  Note: sorting behavior is not cooperating, so needed a trivial np.arange to re-sort at end
            #   (dropped before using `out`)
            if edge_direction == "a1_to_a2":
                start_axis = axis_id_1
                stop_axis = axis_id_2
            elif edge_direction == "a2_to_a1":
                start_axis = axis_id_2
                stop_axis = axis_id_1

            start = pd.DataFrame(np.c_[connections[:, 0], np.arange(connections.shape[0])]) \
                .set_index(0) \
                .merge(self.axes[start_axis].node_placements.set_index("unique_id"),
                       left_index=True, right_index=True, how="left") \
                .sort_values(1) \
                .drop(columns=1) \
                .values

            stop = pd.DataFrame(np.c_[connections[:, 1], np.arange(connections.shape[0])]) \
                .set_index(0) \
                .merge(self.axes[stop_axis].node_placements.set_index("unique_id"),
                       left_index=True, right_index=True, how="left") \
                .sort_values(1) \
                .drop(columns=1) \
                .values

            start_arr = start[:, :2]
            end_arr = stop[:, :2]

            # we only want one rho for the start, stop pair (using the mean rho)
            control_rho = (start[:, 2] + stop[:, 2]) / 2

            # all interactions between same two axes, so only one angle
            angles = [self.axes[axis_id_1].angle, self.axes[axis_id_2].angle]
            angle_diff = angles[1] - angles[0]

            # make sure we take the short arc if requested
            if short_arc:
                if np.abs(angle_diff) > 180:
                    # flip the direction in this case and angle between is now "360 minus"
                    control_angle = angles[0] + -1 * np.sign(angle_diff) * (360 - np.abs(angle_diff)) / 2
                else:
                    control_angle = angles[0] + angle_diff / 2
            # long arc
            else:
                if np.abs(angle_diff) <= 180:
                    # flip the direction in this case and angle between is now "360 minus"
                    control_angle = angles[0] + -1 * np.sign(angle_diff) * (360 - np.abs(angle_diff)) / 2
                else:
                    control_angle = angles[0] + angle_diff / 2

            control_cartesian = polar2cartesian(control_rho, control_angle)
            bezier_output = np.column_stack(
                [bezier_all(start_arr=start_arr[:, i], end_arr=end_arr[:, i],
                            control_arr=control_cartesian[i], num_steps=num_steps)
                 for i in range(2)]
            )

            # put `None` spacers in
            bezier_output = np.insert(arr=bezier_output.astype("O"),
                                      obj=np.arange(bezier_output.shape[0], step=num_steps) + num_steps,
                                      values=None, axis=0)

            # store the output in the right place(s)
            if edge_direction == "a1_to_a2":
                self.edges[axis_id_1][axis_id_2]["curves"] = bezier_output

            elif edge_direction == "a2_to_a1":
                self.edges[axis_id_2][axis_id_1]["curves"] = bezier_output

        return None

    def construct_curves(self, num_steps: int = 100, short_arc: bool = True):
        """
        Constructs bezier curves for any connections for which we've specified the edges to draw (i.e.
        self.edges[axis_0][axis_1]["ids"] is non-empty but self.edges[axis_0][axis_1]["curves"] does not yet exist

        :param num_steps: number of points sampled along a given Bezier curve. Larger numbers will result in
            smoother curves when plotting later, but slower rendering.
        :param short_arc: whether to take the shorter angle arc (True) or longer angle arc (False).
            There are always two ways to traverse between axes: with one angle being x, the other option being 360 - x.
            For most visualizations, the user should expect to traverse the "short arc," hence the default True.
            For full user flexibility, however, we offer the ability to force the arc the other direction, the
            "long arc" (`short_arc = False`). Note: in the case of 2 axes 180 degrees apart, there is no "wrong" angle,
            so in this case an initial decision will be made, but switching this boolean will switch the arc to the
            other hemisphere.
        :return: None
        """

        for a0 in list(self.edges.keys()):
            for a1 in list(self.edges[a0].keys()):
                if "ids" in self.edges[a0][a1] and "curves" not in self.edges[a0][a1]:
                    self.add_edge_curves_between_axes(axis_id_1=a0, axis_id_2=a1, a2_to_a1=False,
                                                      num_steps=num_steps, short_arc=short_arc)
        return None

    def add_edge_kwargs(self, axis_id_1: Hashable, axis_id_2: Hashable,
                        a1_to_a2: bool = True, a2_to_a1: bool = True, **edge_kwargs):
        """
        Add edge kwargs to self.edges (e.g. the Cartesian coordinates of discretized bezier curves of
        edges to be plotted) between two axes of a HivePlot.

        Note: expected to have run `self.find_edge_ids()` first for the two axes of interest.

        Resulting kwargs will be stored as a dict. This output will be stored in
        `self.edges[axis_id_1][axis_id_2]["edge_kwargs"]`.

        :param axis_id_1: Hashable pointer to the first `Axis` instance in `self.axes` we want to find connections
            between.
        :param axis_id_2: Hashable pointer to the second `Axis` instance in `self.axes` we want to find connections
            between.
        :param a1_to_a2: whether to find the connections going FROM axis_id_1 TO axis_id_2
        :param a2_to_a1: whether to find the connections going FROM axis_id_2 TO axis_id_1
        :param edge_kwargs: additional matplotlib params that will be applied to the related edges.
        :return: None
        """

        axes = []
        if a1_to_a2:
            try:
                if "ids" in self.edges[axis_id_1][axis_id_2]:
                    axes.append([axis_id_1, axis_id_2])
            except KeyError:
                raise KeyError("`self.edges[axis_id_1][axis_id_2]['ids']` does not appear to exist. " +
                               "It is expected you have run `self.add_edge_ids()` first for the two axes of interest."
                               )
        if a2_to_a1:
            try:
                if "ids" in self.edges[axis_id_2][axis_id_1]:
                    axes.append([axis_id_2, axis_id_1])
            except KeyError:
                raise KeyError("`self.edges[axis_id_2][axis_id_1]['ids']` does not appear to exist. " +
                               "It is expected you have run `self.add_edge_ids()` first for the two axes of interest."
                               )
        # store the kwargs
        for [a1, a2] in axes:
            self.edges[a1][a2]["edge_kwargs"] = edge_kwargs

        return None

    def connect_axes(self, edges: np.ndarray, axis_id_1: Hashable, axis_id_2: Hashable,
                     a1_to_a2: bool = True, a2_to_a1: bool = True,
                     num_steps: int = 100, short_arc: bool = True, **edge_kwargs):
        """
        Find all the edges to construct between `axis_id_1` to `axis_id_2`, build out the resulting bezier curves,
        and set any kwargs for the edges for later visualization.

        Note: you can choose to construct edges in only one of either directions by specifying `a1_to_a2` or `a2_to_a1`
        as False (both are True by default).

        :param edges: (n, 2) array of Hashables representing pointers to specific `Node` instances.
            The first column is the "from" and the second column is the "to" for each connection.
        :param axis_id_1: Hashable pointer to the first `Axis` instance in `self.axes` we want to find connections
            between.
        :param axis_id_2: Hashable pointer to the second `Axis` instance in `self.axes` we want to find connections
            between.
        :param a1_to_a2: whether to find the connections going FROM axis_id_1 TO axis_id_2
        :param a2_to_a1: whether to find the connections going FROM axis_id_2 TO axis_id_1
        :param num_steps: number of points sampled along a given Bezier curve. Larger numbers will result in
            smoother curves when plotting later, but slower rendering.
        :param short_arc: whether to take the shorter angle arc (True) or longer angle arc (False).
            There are always two ways to traverse between axes: with one angle being x, the other option being 360 - x.
            For most visualizations, the user should expect to traverse the "short arc," hence the default True.
            For full user flexibility, however, we offer the ability to force the arc the other direction, the
            "long arc" (`short_arc = False`). Note: in the case of 2 axes 180 degrees apart, there is no "wrong" angle,
            so in this case an initial decision will be made, but switching this boolean will switch the arc to the
            other hemisphere.
        :param edge_kwargs: additional matplotlib params that will be applied to the related edges.
        :return: None
        """

        self.add_edge_ids(edges=edges, axis_id_1=axis_id_1, axis_id_2=axis_id_2,
                          a1_to_a2=a1_to_a2, a2_to_a1=a2_to_a1)

        self.add_edge_curves_between_axes(axis_id_1=axis_id_1, axis_id_2=axis_id_2,
                                          a1_to_a2=a1_to_a2, a2_to_a1=a2_to_a1,
                                          num_steps=num_steps, short_arc=short_arc)

        self.add_edge_kwargs(axis_id_1=axis_id_1, axis_id_2=axis_id_2,
                             a1_to_a2=a1_to_a2, a2_to_a1=a2_to_a1, **edge_kwargs)

        return None


def hive_plot_n_axes(node_list: List, edges: np.ndarray, axes_assignments: List,
                     sorting_variables: List, axes_names: List or None = None,
                     repeat_axes: List or None = None,
                     vmins: List or None = None, vmaxes: List or None = None,
                     angle_between_repeat_axes: float = 40, orient_angle: float = 0,
                     edge_alpha: float = 0.7):
    """
    Generate a HivePlot Instance with an arbitrary number of axes, as specified by passing a partition of node IDs.
    Repeat axes can be generated for any desired subset of axes, but repeat axes will be sorted by the same variable
    as the original axis.

    Edges directed counterclockwise will be drawn as solid black lines. Clockwise edges will be drawn as dashed black
    lines. These kwargs can be changed by running the `add_edge_kwargs()` method on the resulting `HivePlot` instance.

    Axes will all be the same length and position from the origin.

    :param node_list: List of `Node` instances to go into output `HivePlot` instance
    :param edges: (n, 2) array of Hashables representing pointers to specific `Node` instances.
        The first column is the "from" and the second column is the "to" for each connection.
    :param axes_assignments: list of lists of node unique IDs. Each list will become an axis in the resulting `HivePlot`
       instance.
    :param sorting_variables: list of Hashable variables on which to sort each axis, where the ith index Hashable
        corresponds to the ith index list of nodes in `axes_assignments` (e.g. the ith axis of the resulting
        `HivePlot`).
    :param axes_names: list of Hashable names for each axis, where the ith index Hashable corresponds to the ith index
        list of nodes in `axes_assignments` (e.g. the ith axis of the resulting `HivePlot`). Default `None` names the
        groups as "Group 1," "Group 2," etc.
    :param repeat_axes: list of bools of whether to generate a repeat axis, where the ith index bool corresponds to the
        ith index list of nodes in `axes_assignments` (e.g. the ith axis of the resulting `HivePlot`). A `True` value
        generates a repeat axis. Default `None` assumes no repeat axes (e.g. all `False`).
    :param vmins: list of floats (or `None` values) specifying the vmin for each axis, where the ith index value
        corresponds to the ith index list of nodes in `axes_assignments` (e.g. the ith axis of the resulting
        `HivePlot`). A None value infers the global min for that axis. Default `None` uses the global min for all axes.
    :param vmaxes: list of floats (or `None` values) specifying the vmax for each axis, where the ith index value
        corresponds to the ith index list of nodes in `axes_assignments` (e.g. the ith axis of the resulting
        `HivePlot`). A None value infers the global max for that axis. Default `None` uses the global max for all axes.
    :param angle_between_repeat_axes: angle between repeat axes. Default 40 degrees.
    :param orient_angle: rotates the axes counterclockwise from their initial angles (default 0 degrees).
    :param edge_alpha: alpha value used for all edges in the plot
    :return: `HivePlot` instance
    """

    # make sure specified instructions match the number of specified axes
    assert len(axes_assignments) == len(sorting_variables), \
        "Must specify a sorting variable (`sorting_variables`) for every axis (`axes_assignments`). " + \
        f"Currently have {len(sorting_variables)} sorting variables and {len(axes_assignments)} axes assignments."

    if axes_names is not None:
        assert len(axes_assignments) == len(axes_names), \
            "Must specify a axis name (`axes_names`) for every axis (`axes_assignments`). " + \
            f"Currently have {len(axes_names)} axes names and {len(axes_assignments)} axes assignments."

    else:
        axes_names = [f"Group {i + 1}" for i in range(len(axes_assignments))]

    if repeat_axes is not None:
        assert len(axes_assignments) == len(repeat_axes), \
            "Must specify a repeat axis (`repeat_axes`) for every axis (`axes_assignments`). " + \
            f"Currently have {len(repeat_axes)} repeat axes specified and {len(axes_assignments)} axes assignments."
    else:
        repeat_axes = [False] * len(axes_assignments)

    if vmins is not None:
        assert len(axes_assignments) == len(vmins), \
            "Must specify a vmin (`vmins`) for every axis (`axes_assignments`). " + \
            f"Currently have {len(vmins)} vmins specified and {len(axes_assignments)} axes assignments."
    else:
        vmins = [None] * len(axes_assignments)

    if vmaxes is not None:
        assert len(axes_assignments) == len(vmaxes), \
            "Must specify a vmax (`vmaxes`) for every axis (`axes_assignments`). " + \
            f"Currently have {len(vmaxes)} vmaxes specified and {len(axes_assignments)} axes assignments."
    else:
        vmaxes = [None] * len(axes_assignments)
    
    hp = HivePlot()
    hp.add_nodes(nodes=node_list)

    # space out axes evenly
    spacing = 360/len(axes_assignments)

    if spacing <= angle_between_repeat_axes:
        warnings.warn(
            f"Your angle between repeat axes ({angle_between_repeat_axes}) is going to cause repeat axes to cross " +
            f"past other axes, which will lead to overlapping edges in the final Hive Plot visualization. " +
            f"To space out axes equally, they are {spacing} degrees apart. " +
            f"We recommend setting a lower value for `angle_between_repeat_axes`.",
            stacklevel=2
        )

    for i, assignment in enumerate(axes_assignments):
        angle = spacing * i
        sorting_variable = sorting_variables[i]
        axis_name = axes_names[i]
        repeat_axis = repeat_axes[i]
        vmin = vmins[i]
        vmax = vmaxes[i]

        # add axis / axes
        if not repeat_axis:
            temp_axis = Axis(axis_id=axis_name, start=1, end=5, angle=angle + orient_angle)
            hp.add_axes([temp_axis])
        else:
            # space out on either side of the well-spaced angle
            temp_axis = Axis(axis_id=axis_name, start=1, end=5,
                             angle=angle - angle_between_repeat_axes/2 + orient_angle)
            temp_axis_repeat = Axis(axis_id=f"{axis_name}_repeat", start=1, end=5,
                                    angle=angle + angle_between_repeat_axes/2 + orient_angle,
                                    long_name=axis_name)
            hp.add_axes([temp_axis, temp_axis_repeat])

        # place nodes on the axis / axes
        hp.place_nodes_on_axis(axis_id=axis_name, unique_ids=assignment,
                               sorting_feature_to_use=sorting_variable, vmin=vmin, vmax=vmax)
        # also place values on the repeat axis if we have one
        if repeat_axis:
            hp.place_nodes_on_axis(axis_id=f"{axis_name}_repeat", unique_ids=assignment,
                                   sorting_feature_to_use=sorting_variable, vmin=vmin, vmax=vmax)

    # add in edges
    for i, axis_name in enumerate(axes_names):

        first_axis_name = axis_name

        # figure out next axis to connect to
        if i != len(axes_names) - 1:
            next_axis_name = axes_names[i + 1]
        # circle back to first axis
        else:
            next_axis_name = axes_names[0]

        if repeat_axes[i]:
            # add repeat axis edges (only in ccw direction) if we have a repeat axis
            hp.connect_axes(edges=edges, axis_id_1=first_axis_name, axis_id_2=f"{first_axis_name}_repeat",
                            a2_to_a1=False, c="black", alpha=edge_alpha)
            # the following inter-group edges will instead come off of the repeat edge
            first_axis_name += "_repeat"

        hp.connect_axes(edges=edges, axis_id_1=first_axis_name, axis_id_2=next_axis_name,
                        a2_to_a1=False, c="black", alpha=edge_alpha)
        hp.connect_axes(edges=edges, axis_id_1=first_axis_name, axis_id_2=next_axis_name,
                        a1_to_a2=False, c="black", alpha=edge_alpha, ls="--")

    return hp
