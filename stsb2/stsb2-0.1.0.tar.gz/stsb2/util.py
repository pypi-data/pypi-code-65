
import collections

import numpy as np


def roll_op(
    arr,
    op, 
    window_size, 
    *op_args, 
    output_size='same',
    pad='continue',
    **op_kwargs,
):
    """Rolls an operation along an array.

    Args:
        arr (numpy.ndarray): original array
        op (callable): reduction function
        window_size (int >= 2): size of the subarrays to pass to `op`
        op_args (list): non-keyword arguments to pass to op
        output_size (string): one of 'same', 'valid'
        pad (string): currently only 'continue' is supported
        op_kwargs (dict): keyword arguments to pass to op

    Returns:
        out (numpy.ndarray): the filtered array
    """
    len_arr = arr.shape[-1]
    if output_size == 'same':
        output_size = len_arr
    elif output_size == 'valid':
        output_size = len_arr - window_size
    
    if output_size != 'valid':
        out = np.empty(output_size)
    _opped = np.empty(len_arr - window_size)
    
    
    for i in range(window_size, len_arr):
        _opped[i - window_size] = op(
            arr[..., i - window_size : i],
            *op_args,
            **op_kwargs
        )
    
    if output_size == 'valid':
        return _opped
    
    overhang = window_size + output_size - len_arr
    if overhang % 2 == 0:
        padleft = padright = int(overhang / 2)
    else:
        padleft = int(overhang / 2)
        padright = int(overhang / 2 + 1)
        
    if pad == 'continue':
        out[:padleft] = _opped[0]
        out[-padright:] = _opped[-1]
    out[padleft:-padright] = _opped
    return out


def _constant_std(x):
    dx = x[..., 1:] - x[..., :-1]
    return dx.std(axis=-1)


def _rolling_std(x, window_frac=0.1, power=0.5,):
    window_size = max([int(window_frac * len(x)), 4])
    std = roll_op(
        x[..., 1:] - x[..., :-1], 
        np.std, 
        window_size,
        output_size=len(x)
    )
    return std ** power


def get_free_parameters_from_root(root):
    """Gets all free parameter values from the root and its predecessors

    Defines a BFS order on the compute graph. This is one of two functions
    that explicitly walk through the compute graph.

    Args:
        root (Block): the root of the STS graph

    Returns:
        return (tuple[list]): (nodes, parameter names, parameter bounds)
    """
    deque = collections.deque()
    parameters = list()
    nodes = list()
    bounds = list()
    visited = set()

    prec = root.prec()
    nodes.append(root)
    visited.add(root)
    parameters.append(root.parameters)
    bounds.append(root.parameter_bounds)

    for element in prec:
        deque.append(element)

    while deque:
        this_node = deque.popleft()
        if this_node not in visited:
            nodes.append(this_node)
            visited.add(this_node)
            parameters.append(this_node.parameters)
            bounds.append(this_node.parameter_bounds)
            prec = this_node.prec()

            for element in prec:
                deque.append(element)
        else:
            continue

    return nodes, parameters, bounds


def get_nodes_from_root(root):
    """Returns the root and all its predecessors in the graph.

    Defines a BFS order on the compute graph. This is one of two functions
    that explicitly walk through the compute graph.

    Args:
        root (Block): the root of the STS graph

    Returns:
        nodes (tuple[list]): root and predecessor nodes in the graph
    """
    deque = collections.deque()
    nodes = list()
    visited = set()

    prec = root.prec()
    nodes.append(root)
    visited.add(root)

    for element in prec:
        deque.append(element)

    while deque:
        this_node = deque.popleft()
        if this_node not in visited:
            nodes.append(this_node)
            visited.add(this_node)
            prec = this_node.prec()

            for element in prec:
                deque.append(element)
        else:
            continue

    return nodes


def set_all_values(proposed, nodes, param_names):
    """Sets all values to proposed.

    Args:
        proposed (numpy.ndarray): array of proposed param values.
            Shape (p, batch_size) where p is the total number of params
            of the model
        nodes (list[Block]): list of all blocks in the model
        param_names (list[string]): list of all block param names in the model
    """
    i = 0
    for node, param in zip(nodes, param_names):
        for p in param:
            setattr(node, p, proposed[i])
            i += 1


def get_all_values(nodes, param_names):
    """Gets current value of all parameters in the model.

    Args:
        nodes (list[Block]): list of all blocks in the model
        param_names (list[string]): list of all block param names in the model

    Returns:
        values (list): list of all current param values
    """
    values = list()
    i = 0
    for node, param in zip(nodes, param_names):
        for p in param:
            values.append(getattr(node, p))
            i += 1
    return values


def set_cache_mode(root, cache):
    """
    Sets root and all predecessor nodes cache mode to `cache`.
    
    Args:
        root (Block): a block
        cache (bool): whether or not to cache block calls
    """
    nodes = get_nodes_from_root(root)
    for node in nodes:
        node.is_cached = cache


def clear_cache(root,):
    """
    Clears cache of all predecessor nodes of root.
    This does *not* reset the cache mode of any node;
    to turn off caching, call `set_cache_mode(root, False)`

    Args:
        root (Block): a block
    """
    nodes = get_nodes_from_root(root)
    for node in nodes:
        node.clear_cache()
