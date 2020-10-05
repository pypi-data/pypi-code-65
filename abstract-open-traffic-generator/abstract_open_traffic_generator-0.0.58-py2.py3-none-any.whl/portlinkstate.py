

class PortLinkState(object):
    """Generated from OpenAPI schema object #/components/schemas/PortLinkState

    Control port link state  

    Args
    ----
    - port_names (list[str]): The names of port objects to
     An empty or null list will control all port objects
    - state (Union[up, down]): The link state
    """
    def __init__(self, port_names=[], state=None):
        if isinstance(port_names, (list, type(None))) is True:
            self.port_names = [] if port_names is None else list(port_names)
        else:
            raise TypeError('port_names must be an instance of (list, type(None))')
        if isinstance(state, (str)) is True:
            self.state = state
        else:
            raise TypeError('state must be an instance of (str)')
