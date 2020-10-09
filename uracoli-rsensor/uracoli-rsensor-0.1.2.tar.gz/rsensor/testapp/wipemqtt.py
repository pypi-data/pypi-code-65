from __future__ import print_function

import paho.mqtt.client as mqtt
from optparse import OptionParser
import time, sys

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.subscribe("rsensor/#")

def on_message(client, userdata, msg):
    print("rx:", msg.topic)
    if msg.retain: 
        print("delete ", msg.topic)
        client.publish(msg.topic,"", retain = 1)

if __name__ == "__main__":

    parser = OptionParser(__doc__)
    parser.add_option("-H", "--host", dest="host", default="localhost",
                      help="mqtt hostname")
    parser.add_option("-P", "--port", dest="port", default=1883,
                      help="don't print status messages to stdout")

    (opts, args) = parser.parse_args()

    
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(opts.host, opts.port, 60)
    client.loop_start()
    while 1:
        time.sleep(1)
        print(".", end="")
        sys.stdout.flush()  
    
    
