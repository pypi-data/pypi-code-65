from pyowm.owm import OWM
from pyowm.utils.config import get_default_config
class Corr:
    def __init__(self):
        pass
    def inputs(a):
        a_b = a.split()
        return a_b[0]
class Help:
    def __init__(self):
        pass
    def temo_po_name(place):
        config_dict = get_default_config()
        config_dict['language'] = 'ru'
        owm = OWM('c2a0e326bbada5bf04d2e515be62ca3c', config_dict)
        mgr = owm.weather_manager()
        observation = mgr.weather_at_place(place)
        weather = observation.weather

        temp = weather.temperature('celsius')['temp']
        status = weather.detailed_status
        mark = 'ну это '
        ob = {'st': status, 'temp': temp, 'mar': mark}
        return ob


