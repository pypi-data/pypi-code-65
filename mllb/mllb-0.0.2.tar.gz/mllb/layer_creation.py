"""
Layer creation functions.
Used when the creating neural network layers.

"""


def sigmoid(nodes):

    """
    Sigmoid activated layer.

    Args:
        nodes: (int) number of nodes

    """

    if isinstance(nodes, int) == False or nodes < 1:
        raise ValueError("'nodes' value must be a positive integer")

    return [nodes, "sigmoid"]

def relu(nodes):
    
    """
    ReLU activated layer.

    Args:
        nodes: (int) number of nodes

    """

    if isinstance(nodes, int) == False or nodes < 1:
        raise ValueError("'nodes' value must be a positive integer")

    return [nodes, "relu"]

def tanh(nodes):

    """
    tanh activated layer.

    Args:
        nodes: (int) number of nodes

    """

    if isinstance(nodes, int) == False or nodes < 1:
        raise ValueError("'nodes' value must be a positive integer")

    return [nodes, "tanh"]

def softplus(nodes):

    """
    softplus activated layer.

    Args:
        nodes: (int) number of nodes

    """

    if isinstance(nodes, int) == False or nodes < 1:
        raise ValueError("'nodes' value must be a positive integer")

    return [nodes, "softplus"]

def softmax(nodes):

    """
    softmax activated layer.

    Args:
        nodes: (int) number of nodes

    """

    if isinstance(nodes, int) == False or nodes < 1:
        raise ValueError("'nodes' value must be a positive integer")

    return [nodes, "softmax"]

def leakyrelu(nodes):

    """
    leakyReLU activated layer.

    Args:
        nodes: (int) number of nodes

    """

    if isinstance(nodes, int) == False or nodes < 1:
        raise ValueError("'nodes' value must be a positive integer")

    return [nodes, "leakyrelu"]

def none(nodes):

    """
    un-activated layer.

    Args:
        nodes: (int) number of nodes

    """

    if isinstance(nodes, int) == False or nodes < 1:
        raise ValueError("'nodes' value must be a positive integer")

    return [nodes, "none"]