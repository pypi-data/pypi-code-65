

class Port(object):
    """Generated from OpenAPI schema object #/components/schemas/Port

    An abstract test port  

    Args
    ----
    - name (str): Unique name of an object that is the primary key for objects found in arrays
    - location (str): The location of a test port
     It is the endpoint where packets will emit from
     Test port locations can be the following: - physical appliance with multiple ports - physical chassis with multiple cards and ports - local interface - virtual machine, docker container, kubernetes cluster The test port location format is implementation specific
     Use the /results/capabilities API to determine what formats an implementation supports for the location property
     Get the configured location state by using the /results/port API
    - devices (list[Device]): TBD
    - capture (Capture): Container for capture filter information
    """
    def __init__(self, name=None, location=None, devices=[], capture=None):
        from abstract_open_traffic_generator.port import Capture
        if isinstance(name, (str)) is True:
            import re
            assert(bool(re.match(r'^[\sa-zA-Z0-9-_()><\[\]]+$', name)) is True)
            self.name = name
        else:
            raise TypeError('name must be an instance of (str)')
        if isinstance(location, (str, type(None))) is True:
            self.location = location
        else:
            raise TypeError('location must be an instance of (str, type(None))')
        if isinstance(devices, (list, type(None))) is True:
            self.devices = [] if devices is None else list(devices)
        else:
            raise TypeError('devices must be an instance of (list, type(None))')
        if isinstance(capture, (Capture, type(None))) is True:
            self.capture = capture
        else:
            raise TypeError('capture must be an instance of (Capture, type(None))')


class Capture(object):
    """Generated from OpenAPI schema object #/components/schemas/Port.Capture

    Container for capture filter information  

    Args
    ----
    - choice (Union[list, str]): The type of filter
    - enable (Union[True, False]): Enable capture on the port
    - overwrite (Union[True, False]): Overwrite the capture buffer
    - format (Union[pcap, pcapng]): The format of the capture file
    """
    _CHOICE_MAP = {
        'list': 'basic',
        'str': 'pcap',
    }
    def __init__(self, choice=None, enable=True, overwrite=False, format='pcap'):
        if isinstance(choice, (list, str)) is False:
            raise TypeError('choice must be of type: list, str')
        self.__setattr__('choice', Capture._CHOICE_MAP[type(choice).__name__])
        self.__setattr__(Capture._CHOICE_MAP[type(choice).__name__], choice)
        if isinstance(enable, (bool, type(None))) is True:
            self.enable = enable
        else:
            raise TypeError('enable must be an instance of (bool, type(None))')
        if isinstance(overwrite, (bool, type(None))) is True:
            self.overwrite = overwrite
        else:
            raise TypeError('overwrite must be an instance of (bool, type(None))')
        if isinstance(format, (str, type(None))) is True:
            self.format = format
        else:
            raise TypeError('format must be an instance of (str, type(None))')


class BasicFilter(object):
    """Generated from OpenAPI schema object #/components/schemas/Port.BasicFilter

    A container for different types of basic capture filters  

    Args
    ----
    - choice (Union[MacAddressFilter, CustomFilter]): TBD
    - and_operator (Union[True, False]): TBD
    - not_operator (Union[True, False]): TBD
    """
    _CHOICE_MAP = {
        'MacAddressFilter': 'mac_address',
        'CustomFilter': 'custom',
    }
    def __init__(self, choice=None, and_operator=True, not_operator=False):
        from abstract_open_traffic_generator.port import MacAddressFilter
        from abstract_open_traffic_generator.port import CustomFilter
        if isinstance(choice, (MacAddressFilter, CustomFilter)) is False:
            raise TypeError('choice must be of type: MacAddressFilter, CustomFilter')
        self.__setattr__('choice', BasicFilter._CHOICE_MAP[type(choice).__name__])
        self.__setattr__(BasicFilter._CHOICE_MAP[type(choice).__name__], choice)
        if isinstance(and_operator, (bool, type(None))) is True:
            self.and_operator = and_operator
        else:
            raise TypeError('and_operator must be an instance of (bool, type(None))')
        if isinstance(not_operator, (bool, type(None))) is True:
            self.not_operator = not_operator
        else:
            raise TypeError('not_operator must be an instance of (bool, type(None))')


class MacAddressFilter(object):
    """Generated from OpenAPI schema object #/components/schemas/Port.MacAddressFilter

    A container for a mac address capture filter  

    Args
    ----
    - mac (Union[source, destination]): The type of mac address filters
     This can be either source or destination
    - filter (str): The value of the mac address
    - mask (str): The value of the mask to be applied to the mac address
    """
    def __init__(self, mac=None, filter=None, mask=None):
        if isinstance(mac, (str)) is True:
            self.mac = mac
        else:
            raise TypeError('mac must be an instance of (str)')
        if isinstance(filter, (str)) is True:
            self.filter = filter
        else:
            raise TypeError('filter must be an instance of (str)')
        if isinstance(mask, (str, type(None))) is True:
            self.mask = mask
        else:
            raise TypeError('mask must be an instance of (str, type(None))')


class CustomFilter(object):
    """Generated from OpenAPI schema object #/components/schemas/Port.CustomFilter

    A container for a custom capture filter  

    Args
    ----
    - filter (str): The value to filter on
    - mask (str): The mask to be applied to the filter
    - offset (int): The offset in the packet to filter at
    """
    def __init__(self, filter=None, mask=None, offset=None):
        if isinstance(filter, (str)) is True:
            self.filter = filter
        else:
            raise TypeError('filter must be an instance of (str)')
        if isinstance(mask, (str, type(None))) is True:
            self.mask = mask
        else:
            raise TypeError('mask must be an instance of (str, type(None))')
        if isinstance(offset, (float, int)) is True:
            self.offset = offset
        else:
            raise TypeError('offset must be an instance of (float, int)')


class Options(object):
    """Generated from OpenAPI schema object #/components/schemas/Port.Options

    Common port options that apply to all configured Port.Port objects  

    Args
    ----
    - location_preemption (Union[True, False]): Preempt all the test port locations as defined by the Port
     Port
     properties
     location
     If the test ports as defined by their location values are in use and this value is true, the test ports will be preempted
    """
    def __init__(self, location_preemption=False):
        if isinstance(location_preemption, (bool, type(None))) is True:
            self.location_preemption = location_preemption
        else:
            raise TypeError('location_preemption must be an instance of (bool, type(None))')
