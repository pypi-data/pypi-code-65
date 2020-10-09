"""rsensor test data generator"""

# === modules ==================================================================
from __future__ import print_function

import json
import logging
from optparse import OptionParser
import os
import paho.mqtt.client as mqtt
from pprint import pprint as pp
import random
import sys
import time
import yaml

# === local modules ============================================================
import rsensor

# === globals ==================================================================
EPILOG = """
Example YMLCONFIG File::
    
    ----------------------------------------------------
    - node:
            id: s_1111_0001
            name: s_1111_0001
            geolocation: [1, 3]
            loctag: Werkstatt
      actors:
            - description: power switch room light
              id: lamp1
      sensors:
            - id: temp1
              description: temperatur desk
              limits: [-10, 45]
              type: float
              unit: degC
            - id: hum1
              limits: [0, 100]
              type: float
              unit: '%%RH'
    # 2nd node
    - node: 
        ...
      sensors:
        ...
    ----------------------------------------------------
"""


# === classes ==================================================================

class MqttRandomGenerator:

    Sensors = {}

    def __init__(self, host, port=1883, prefix=None):
        self.L = logging.getLogger(self.__class__.__name__)
        self.host = host
        self.port = port
        self.prefix = prefix
        self.L.info("create generator class")
        self.client = mqtt.Client(userdata=self)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(host, port, 60)
        self.client.loop_start()

    @staticmethod
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            userdata.client.subscribe("%s/nodes/+/info" % userdata.prefix)
            userdata.L.info("connected to %s:%s, prefix=%s", userdata.host, userdata.port, userdata.prefix)
        else:
            raise Exception("FailedToConnect")

    @staticmethod
    def on_message(client, userdata, msg):
        #print(msg.topic+" "+str(msg.payload))
        topic_parts = msg.topic.split("/")
        if topic_parts[1] == "node" and topic_parts[-1] == "info":
            pp(json.loads(msg.payload))

    def create_sensor_info(self, node_id, cfg):
        self.Sensors[node_id] = cfg
        topic = self.prefix + "/" + "%s/info" % node_id
        self.client.publish(topic,
                            json.dumps(cfg, sort_keys=True),
                            retain=True)
        self.L.info("info message on: %s" % topic)
        self.L.debug("topic: %s, data: %s", topic, cfg)

    def generate_sensor_message(self, node):
        rv = {}
        s = self.Sensors.get(node)
        if s:
            topic = self.prefix + "/" + "%s/data" % node
            # todo: implement randomization of values
            data = {k['id']: 42 for k in s['sensors']}
            self.client.publish(topic, json.dumps(data, sort_keys=True))
            self.L.info("data message on: %s", topic)
            self.L.debug("topic: %s, data: %s", topic, data)


# === functions ================================================================

def process_options():
    
    class MyOptionParser(OptionParser):
        def format_epilog(self, formatter):
            return self.epilog
    # setup parser
    parser = MyOptionParser(description=__doc__, epilog=EPILOG)
    parser.add_option("-H", "--host", dest="host", default="localhost",
                      help="MQTT hostname (default: localhost)")
    parser.add_option("-P", "--port", dest="port", default=1883,
                      help="port number of MQTT server (default: 1883)")
    parser.add_option("--prefix", default="rsensor-test",
                      help="prefix where data are published (default: rsensor-test)")
    parser.add_option("-C", "--config",dest="ymlconfig", default="rsensor-test",
                      help="Yaml Config file that describes the sensors generated")
    _ll = ["DEBUG", "INFO", "WARNING", "ERROR"]
    _dfl_ll = "INFO"
    parser.add_option("-L", "--loglevel", type="choice", dest="loglevel", 
                      choices=_ll, default=_dfl_ll,
                      help="set loglevel to one off %s (default: %s)" % (_ll, _dfl_ll))

    (opts, _) = parser.parse_args()
    
    # verify if yml-config file exists
    if opts.ymlconfig == None:
        opts.ymlconfig = os.path.join(os.path.dirname(rsensor.__file__), "data", "test_node.yml")
        print("using default sensor config: %s" % opts.ymlconfig)

    assert os.path.isfile(opts.ymlconfig), "can not read sensor config: %s" % opts.ymlconfig

    return opts

def main():    
    opts = process_options()
    # setup logging
    logging.basicConfig()
    logging.root.setLevel(logging.getLevelName(opts.loglevel))

    
    mg = MqttRandomGenerator(opts.host, opts.port, opts.prefix)

    with open(opts.ymlconfig) as fh:
        
        ycfg = yaml.safe_load(fh.read())
    for n in ycfg:
        mg.create_sensor_info(n['node']['id'], n)

    try:
        while 1:
            time.sleep(1)
            sn = random.choice(mg.Sensors.keys())
            mg.generate_sensor_message(sn)
            sys.stdout.flush()
    except KeyboardInterrupt:
        print("Ctrl-C hit")


if __name__ == "__main__":
    main()
