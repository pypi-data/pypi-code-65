# Version of the include-beer-DHT11 package
__version__ = "1.0.2"

import board
import adafruit_dht
import sys

def read(data_pin, temperature_scale='f'):
    """read ambient sensor

    Required:
        data_pin (int): pin data is on
        temperature_scale (str, default=f): c or f 
    """
    if isinstance(data_pin, str) and data_pin == 'Empty':
        # sfrom board import 'Empty'
        _eval_str = 'board.Empty'
    elif isinstance(data_pin, int):
        #from board import data_pin
        _eval_str = 'board.D' + str(data_pin)
    elif isinstance(data_pin, str):
        # sfrom board import int(data_pin)
        _eval_str = 'board.D' + data_pin
    else:
        return "Data pin supplied is not a valid value", str(data_pin)
    try:
        data_pin = eval(_eval_str)
    except AttributeError as error:
        return "Data pin not found", str(data_pin)
    dht_device = adafruit_dht.DHT11(data_pin)
    try:
        # by default the device returns c
        temperature = dht_device.temperature
        if temperature_scale == 'f':
            temperature = temperature * (9 / 5) + 32
        humidity = dht_device.humidity
        dht_device.exit()
        return temperature, humidity
    except RuntimeError as error:
        # TODO: figure out better error handling and message return
        # print('Errors happen fairly often, DHT''s are hard to read, just keep going after you read the following error msg:')
        # print(error.args[0])
        dht_device.exit()
        return "DHT read error", error.args[0]
