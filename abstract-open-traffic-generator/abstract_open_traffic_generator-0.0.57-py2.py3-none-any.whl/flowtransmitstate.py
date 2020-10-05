

class FlowTransmitState(object):
    """Generated from OpenAPI schema object #/components/schemas/FlowTransmitState

    Control flow transmit state  

    Args
    ----
    - flow_names (list[str]): The names of flow objects to control
     An empty or null list will control all flow objects
    - state (Union[start, stop, pause]): The transmit state
    """
    def __init__(self, flow_names=[], state=None):
        if isinstance(flow_names, (list, type(None))) is True:
            self.flow_names = [] if flow_names is None else list(flow_names)
        else:
            raise TypeError('flow_names must be an instance of (list, type(None))')
        if isinstance(state, (str)) is True:
            self.state = state
        else:
            raise TypeError('state must be an instance of (str)')
