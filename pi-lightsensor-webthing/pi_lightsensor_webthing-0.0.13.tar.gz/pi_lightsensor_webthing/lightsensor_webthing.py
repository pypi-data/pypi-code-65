from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
import logging
import RPi.GPIO as GPIO
import tornado.ioloop


class LightSensor(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, gpio_number, name, description):
        Thing.__init__(
            self,
            'urn:dev:ops:illuminanceSensor-1',
            'Illuminance ' + name,
            ['BinarySensor'],
            description
        )

        self.bright = Value(False)
        self.add_property(
            Property(self,
                     'bright',
                     self.bright,
                     metadata={
                         '@type': 'BooleanProperty',
                         'title': 'bright',
                         "type": "boolean",
                         'description': 'Whether is bright',
                         'readOnly': True,
                     }))

        self.ioloop = tornado.ioloop.IOLoop.current()
        logging.info('bind to gpio ' + str(gpio_number))
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(gpio_number, GPIO.IN)
        GPIO.add_event_detect(gpio_number, GPIO.BOTH, callback=self.__update, bouncetime=5)
        self.__update(gpio_number)

    def __update(self, gpio_number):
        if GPIO.input(gpio_number):
            self.ioloop.add_callback(self.__update_bright_prop, False)
        else:
            self.ioloop.add_callback(self.__update_bright_prop, True)

    def __update_bright_prop(self, is_bright):
        self.bright.notify_of_external_update(is_bright)
        logging.info("is_bright: " + str(is_bright))


def run_server(port, gpio_number, name, description):
    light_sensor = LightSensor(gpio_number, name, description)
    server = WebThingServer(SingleThing(light_sensor), port=port)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        server.stop()
        logging.info('done')
