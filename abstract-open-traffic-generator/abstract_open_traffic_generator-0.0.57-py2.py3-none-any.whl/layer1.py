

class Layer1(object):
    """Generated from OpenAPI schema object #/components/schemas/Layer1

    A container for layer1 settings  

    Args
    ----
    - name (str): Unique name of an object that is the primary key for objects found in arrays
    - port_names (list[str]): A list of unique names of a port objects that will share the choice settings
    - choice (Union[OneHundredGbe, Ethernet]): The type of layer1 characteristics
    """
    _CHOICE_MAP = {
        'OneHundredGbe': 'one_hundred_gbe',
        'Ethernet': 'ethernet',
    }
    def __init__(self, name=None, port_names=[], choice=None):
        from abstract_open_traffic_generator.layer1 import OneHundredGbe
        from abstract_open_traffic_generator.layer1 import Ethernet
        if isinstance(choice, (OneHundredGbe, Ethernet)) is False:
            raise TypeError('choice must be of type: OneHundredGbe, Ethernet')
        self.__setattr__('choice', Layer1._CHOICE_MAP[type(choice).__name__])
        self.__setattr__(Layer1._CHOICE_MAP[type(choice).__name__], choice)
        if isinstance(name, (str)) is True:
            import re
            assert(bool(re.match(r'^[\sa-zA-Z0-9-_()><\[\]]+$', name)) is True)
            self.name = name
        else:
            raise TypeError('name must be an instance of (str)')
        if isinstance(port_names, (list, type(None))) is True:
            self.port_names = [] if port_names is None else list(port_names)
        else:
            raise TypeError('port_names must be an instance of (list, type(None))')


class OneHundredGbe(object):
    """Generated from OpenAPI schema object #/components/schemas/Layer1.OneHundredGbe

    Container for 100 gigabit ethernet settings  

    Args
    ----
    - ieee_media_defaults (Union[True, False]): Enable/disable ieee media default settings
     True will override the speed, auto_negotiate, link_training, rs_fec settings
    - auto_negotiate (Union[True, False]): Enable/disable auto negotiation
    - link_training (Union[True, False]): Enable/disable link training
    - rs_fec (Union[True, False]): Enable/disable reed solomon forward error correction (RS FEC)
    - speed (Union[one_hundred_gbps, fifty_gbps, forty_gbps, twenty_five_gpbs, ten_gbps]): This is the speed that will be used if auto_negotiate is false
    - flow_control (FlowControl): A container for layer1 receive flow control settings
     To enable flow control settings on ports this object must be a valid object not a null value
    """
    def __init__(self, ieee_media_defaults=True, auto_negotiate=False, link_training=False, rs_fec=False, speed='one_hundred_gbps', flow_control=None):
        from abstract_open_traffic_generator.layer1 import FlowControl
        if isinstance(ieee_media_defaults, (bool, type(None))) is True:
            self.ieee_media_defaults = ieee_media_defaults
        else:
            raise TypeError('ieee_media_defaults must be an instance of (bool, type(None))')
        if isinstance(auto_negotiate, (bool, type(None))) is True:
            self.auto_negotiate = auto_negotiate
        else:
            raise TypeError('auto_negotiate must be an instance of (bool, type(None))')
        if isinstance(link_training, (bool, type(None))) is True:
            self.link_training = link_training
        else:
            raise TypeError('link_training must be an instance of (bool, type(None))')
        if isinstance(rs_fec, (bool, type(None))) is True:
            self.rs_fec = rs_fec
        else:
            raise TypeError('rs_fec must be an instance of (bool, type(None))')
        if isinstance(speed, (str, type(None))) is True:
            self.speed = speed
        else:
            raise TypeError('speed must be an instance of (str, type(None))')
        if isinstance(flow_control, (FlowControl, type(None))) is True:
            self.flow_control = flow_control
        else:
            raise TypeError('flow_control must be an instance of (FlowControl, type(None))')


class EthernetVirtual(object):
    """Generated from OpenAPI schema object #/components/schemas/Layer1.EthernetVirtual

    Container for virtual ethernet settings  

    Args
    ----
    - speed (Union[one_hundred_mbps, one_gbps, ten_gbps, twenty_five_gbps, fifty_gbps, one_hundred_gbps]): This is the speed that will be set on the virtual ethernet interface
    """
    def __init__(self, speed='ten_gbps'):
        if isinstance(speed, (str, type(None))) is True:
            self.speed = speed
        else:
            raise TypeError('speed must be an instance of (str, type(None))')


class Ethernet(object):
    """Generated from OpenAPI schema object #/components/schemas/Layer1.Ethernet

    Container for 10/100/1000 ethernet settings  

    Args
    ----
    - media (Union[copper, fiber]): TBD
    - speed (Union[one_thousand_mbps, one_hundred_fd_mbps, one_hundred_hd_mbps, ten_fd_mbps, ten_hd_mbps]): This is the speed that will be used if auto_negotiate is false
    - auto_negotiate (Union[True, False]): Enable/disable auto negotiation
    - advertise_one_thousand_mbps (Union[True, False]): If auto_negotiate is true then this speed will be advertised
    - advertise_one_hundred_fd_mbps (Union[True, False]): If auto_negotiate is true then this speed will be advertised
    - advertise_one_hundred_hd_mbps (Union[True, False]): If auto_negotiate is true then this speed will be advertised
    - advertise_ten_fd_mbps (Union[True, False]): If auto_negotiate is true then this speed will be advertised
    - advertise_ten_hd_mbps (Union[True, False]): If auto_negotiate is true then this speed will be advertised
    - flow_control (FlowControl): A container for layer1 receive flow control settings
     To enable flow control settings on ports this object must be a valid object not a null value
    """
    def __init__(self, media='copper', speed='one_thousand_mbps', auto_negotiate=True, advertise_one_thousand_mbps=True, advertise_one_hundred_fd_mbps=True, advertise_one_hundred_hd_mbps=True, advertise_ten_fd_mbps=True, advertise_ten_hd_mbps=True, flow_control=None):
        from abstract_open_traffic_generator.layer1 import FlowControl
        if isinstance(media, (str, type(None))) is True:
            self.media = media
        else:
            raise TypeError('media must be an instance of (str, type(None))')
        if isinstance(speed, (str, type(None))) is True:
            self.speed = speed
        else:
            raise TypeError('speed must be an instance of (str, type(None))')
        if isinstance(auto_negotiate, (bool, type(None))) is True:
            self.auto_negotiate = auto_negotiate
        else:
            raise TypeError('auto_negotiate must be an instance of (bool, type(None))')
        if isinstance(advertise_one_thousand_mbps, (bool, type(None))) is True:
            self.advertise_one_thousand_mbps = advertise_one_thousand_mbps
        else:
            raise TypeError('advertise_one_thousand_mbps must be an instance of (bool, type(None))')
        if isinstance(advertise_one_hundred_fd_mbps, (bool, type(None))) is True:
            self.advertise_one_hundred_fd_mbps = advertise_one_hundred_fd_mbps
        else:
            raise TypeError('advertise_one_hundred_fd_mbps must be an instance of (bool, type(None))')
        if isinstance(advertise_one_hundred_hd_mbps, (bool, type(None))) is True:
            self.advertise_one_hundred_hd_mbps = advertise_one_hundred_hd_mbps
        else:
            raise TypeError('advertise_one_hundred_hd_mbps must be an instance of (bool, type(None))')
        if isinstance(advertise_ten_fd_mbps, (bool, type(None))) is True:
            self.advertise_ten_fd_mbps = advertise_ten_fd_mbps
        else:
            raise TypeError('advertise_ten_fd_mbps must be an instance of (bool, type(None))')
        if isinstance(advertise_ten_hd_mbps, (bool, type(None))) is True:
            self.advertise_ten_hd_mbps = advertise_ten_hd_mbps
        else:
            raise TypeError('advertise_ten_hd_mbps must be an instance of (bool, type(None))')
        if isinstance(flow_control, (FlowControl, type(None))) is True:
            self.flow_control = flow_control
        else:
            raise TypeError('flow_control must be an instance of (FlowControl, type(None))')


class FlowControl(object):
    """Generated from OpenAPI schema object #/components/schemas/Layer1.FlowControl

    A container for layer1 receive flow control settings  
    To enable flow control settings on ports this object must be a valid object not a null value  

    Args
    ----
    - directed_address (str): The 48bit mac address that the layer1 port names will listen on for a directed pause
    - choice (Union[Ieee8021qbb, Ieee8023x]): The type of priority flow control
    """
    _CHOICE_MAP = {
        'Ieee8021qbb': 'ieee_802_1qbb',
        'Ieee8023x': 'ieee_802_3x',
    }
    def __init__(self, directed_address='0180C2000001', choice=None):
        from abstract_open_traffic_generator.layer1 import Ieee8021qbb
        from abstract_open_traffic_generator.layer1 import Ieee8023x
        if isinstance(choice, (Ieee8021qbb, Ieee8023x)) is False:
            raise TypeError('choice must be of type: Ieee8021qbb, Ieee8023x')
        self.__setattr__('choice', FlowControl._CHOICE_MAP[type(choice).__name__])
        self.__setattr__(FlowControl._CHOICE_MAP[type(choice).__name__], choice)
        if isinstance(directed_address, (str, type(None))) is True:
            self.directed_address = directed_address
        else:
            raise TypeError('directed_address must be an instance of (str, type(None))')


class Ieee8023x(object):
    """Generated from OpenAPI schema object #/components/schemas/Layer1.Ieee8023x

    A container for ieee 802.3x rx pause settings  
    """
    def __init__(self):
        pass


class Ieee8021qbb(object):
    """Generated from OpenAPI schema object #/components/schemas/Layer1.Ieee8021qbb

    These settings enhance the existing 802.3x pause priority capabilities to enable flow control based on 802.1p priorities (classes of service)  

    Args
    ----
    - pfc_delay (int): The upper limit on the transmit time of a queue after receiving a message to pause a specified priority
     A value of 0 or null indicates that pfc delay will not be enabled
    - pfc_class_0 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    - pfc_class_1 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    - pfc_class_2 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    - pfc_class_3 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    - pfc_class_4 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    - pfc_class_5 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    - pfc_class_6 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    - pfc_class_7 (int): The valid values are null, 0 - 7
     A null value indicates there is no setting for this pfc class
    """
    def __init__(self, pfc_delay=None, pfc_class_0=None, pfc_class_1=None, pfc_class_2=None, pfc_class_3=None, pfc_class_4=None, pfc_class_5=None, pfc_class_6=None, pfc_class_7=None):
        if isinstance(pfc_delay, (float, int, type(None))) is True:
            self.pfc_delay = pfc_delay
        else:
            raise TypeError('pfc_delay must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_0, (float, int, type(None))) is True:
            self.pfc_class_0 = pfc_class_0
        else:
            raise TypeError('pfc_class_0 must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_1, (float, int, type(None))) is True:
            self.pfc_class_1 = pfc_class_1
        else:
            raise TypeError('pfc_class_1 must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_2, (float, int, type(None))) is True:
            self.pfc_class_2 = pfc_class_2
        else:
            raise TypeError('pfc_class_2 must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_3, (float, int, type(None))) is True:
            self.pfc_class_3 = pfc_class_3
        else:
            raise TypeError('pfc_class_3 must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_4, (float, int, type(None))) is True:
            self.pfc_class_4 = pfc_class_4
        else:
            raise TypeError('pfc_class_4 must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_5, (float, int, type(None))) is True:
            self.pfc_class_5 = pfc_class_5
        else:
            raise TypeError('pfc_class_5 must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_6, (float, int, type(None))) is True:
            self.pfc_class_6 = pfc_class_6
        else:
            raise TypeError('pfc_class_6 must be an instance of (float, int, type(None))')
        if isinstance(pfc_class_7, (float, int, type(None))) is True:
            self.pfc_class_7 = pfc_class_7
        else:
            raise TypeError('pfc_class_7 must be an instance of (float, int, type(None))')
