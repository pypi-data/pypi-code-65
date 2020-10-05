

class PortCaptureState(object):
    """Generated from OpenAPI schema object #/components/schemas/PortCaptureState

    Control port capture state  

    Args
    ----
    - port_names (list[str]): The name of ports to start capturing packets on
     An empty or null list will control all port objects
    - state (Union[start, stop]): The capture state
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
