

class State(object):
    """Generated from OpenAPI schema object #/components/schemas/Control.State

    A container for the different types of states  

    Args
    ----
    - choice (Union[ConfigState, PortLinkState, PortCaptureState, FlowTransmitState]): TBD
    """
    _CHOICE_MAP = {
        'ConfigState': 'config_state',
        'PortLinkState': 'port_link_state',
        'PortCaptureState': 'port_capture_state',
        'FlowTransmitState': 'flow_transmit_state',
    }
    def __init__(self, choice=None):
        from abstract_open_traffic_generator. import ConfigState
        from abstract_open_traffic_generator. import PortLinkState
        from abstract_open_traffic_generator. import PortCaptureState
        from abstract_open_traffic_generator. import FlowTransmitState
        if isinstance(choice, (ConfigState, PortLinkState, PortCaptureState, FlowTransmitState)) is False:
            raise TypeError('choice must be of type: ConfigState, PortLinkState, PortCaptureState, FlowTransmitState')
        self.__setattr__('choice', State._CHOICE_MAP[type(choice).__name__])
        self.__setattr__(State._CHOICE_MAP[type(choice).__name__], choice)
