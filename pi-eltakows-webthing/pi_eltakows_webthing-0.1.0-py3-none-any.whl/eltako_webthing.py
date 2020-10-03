from webthing import (SingleThing, Property, Thing, Value, WebThingServer)
import RPi.GPIO as GPIO
import logging
import time
import tornado.ioloop


class EltakoWsSensor(Thing):

    # regarding capabilities refer https://iot.mozilla.org/schemas
    # there is also another schema registry http://iotschema.org/docs/full.html not used by webthing

    def __init__(self, gpio_number, description):
        Thing.__init__(
            self,
            'urn:dev:ops:eltakowsSensor-1',
            'Windsensor',
            ['MultiLevelSensor'],
            description
        )

        self.gpio_number = gpio_number
        self.start_time = time.time()
        self.num_raise_events = 0
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.gpio_number, GPIO.IN)
        GPIO.add_event_detect(self.gpio_number, GPIO.RISING, callback=self.__spin, bouncetime=5)

        self.timer = tornado.ioloop.PeriodicCallback(self.__measure, 5000)

        self.windspeed = Value(0.0)
        self.add_property(
            Property(self,
                     'windspeed',
                     self.windspeed,
                     metadata={
                         '@type': 'LevelProperty',
                         'title': 'Windspeed',
                         'type': 'number',
                         'description': 'The current windspeed',
                         'unit': 'km/h',
                         'readOnly': True,
                     }))
        self.timer.start()

    def __spin(self, channel):
        self.num_raise_events = self.num_raise_events + 1

    def __measure(self):
        try:
            windspeed_kmh = 0
            elapsed_sec = time.time() - self.start_time
            if (self.num_raise_events > 0) and (elapsed_sec > 0):
                windspeed_kmh = self.__compute_speed_kmh(self.num_raise_events, elapsed_sec)
            self.num_raise_events = 0
            self.start_time = time.time()
            logging.info('windspeed ' + str(windspeed_kmh) + " (" + str(self.num_raise_events) + ' raise events/' + str(elapsed_sec) + ' sec)')
            self.windspeed.notify_of_external_update(windspeed_kmh)
        except Exception as e:
            logging.debug(str(e))

    def __compute_speed_kmh(self, num_raise_events, elapsed_sec):
        rotation_per_sec = num_raise_events / elapsed_sec
        lowspeed_factor = 1.761
        highspeed_factor = 3.013
        km_per_hour = lowspeed_factor / (1 + rotation_per_sec) + highspeed_factor * rotation_per_sec
        if km_per_hour < 2:
            km_per_hour = 0
        return round(km_per_hour, 1)

    def cancel_measure_task(self):
        self.timer.stop()


def run_server(port, gpio_number, description):
    eltakows_sensor = EltakoWsSensor(gpio_number, description)
    server = WebThingServer(SingleThing(eltakows_sensor), port=port)
    try:
        logging.info('starting the server')
        server.start()
    except KeyboardInterrupt:
        logging.info('stopping the server')
        eltakows_sensor.cancel_measure_task()
        server.stop()
        logging.info('done')

