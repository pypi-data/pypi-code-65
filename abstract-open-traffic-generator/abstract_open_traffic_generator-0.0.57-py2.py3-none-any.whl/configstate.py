

class ConfigState(object):
    """Generated from OpenAPI schema object #/components/schemas/ConfigState

    Control the configuration state on the traffic generator  

    Args
    ----
    - config (Config): A container for all models that are part of the configuration
    - state (Union[set, update]): Set the configuration state on the traffic generator
     - set is used to submit a complete running configuration on the traffic generator
     - update is used to submit a partial configuration which will be merged with the current running configuration on the traffic generator
    """
    def __init__(self, config=None, state=None):
        from abstract_open_traffic_generator. import Config
        if isinstance(config, (Config)) is True:
            self.config = config
        else:
            raise TypeError('config must be an instance of (Config)')
        if isinstance(state, (str)) is True:
            self.state = state
        else:
            raise TypeError('state must be an instance of (str)')
