
from kpn_senml import *
import paho.mqtt.client as mqtt
import time
import resource_monitoring as rm


class IfraSDK():
  def __init__(self, channel, device_id,device_secret ,server="mqtt.ifra.io"):
    self.server = server
    self.channel = channel
    self.device_id = device_id
    self.device_secret = device_secret
    self.pack = SenmlPack("")
    self.client = mqtt.Client("makerio_mqtt") 
    self.client.username_pw_set(username=self.device_id,password=self.device_secret)
    self.client.connect(self.server, 1883) 

    self.client.on_message = self.on_message 
    self.client.loop_start() 
 
  def on_log(self,mqttc, obj, level, string):
        print(string)
    # The callback for when the client receives a CONNACK response from the server.
  def on_connect(self,client, userdata, flags, rc):
        print("Connected with result code "+str(rc))
        self.client.subscribe("organization/"+self.channel+"/messages") 

  def on_message(self,client, userdata, msg):
        print(msg.topic+" "+str(msg.payload))


  def on_disconnect(self,client, userdata, rc):
        if rc != 0:
            print("Unexpected disconnection.")
  def addActuator(self,sensor_name,unit,value):
     pass

  def addSensor(self,sensor_name,unit,value):
     self.pack.add(SenmlRecord(sensor_name, unit=unit, value=value))

  def send(self):
     topic = "organization/"+self.channel+"/messages"
     self.client.publish(topic, self.pack.to_json(), qos=0, retain=False) 
     self.pack.clear()
  def toJson(self):
     return self.pack.to_json()






counter=0
while True:
    if counter == 1:
        break
    # Create new client
    client = IfraSDK("ebd53c0e-3e3a-49ab-8b5f-3ee37bce93fb","bea3e088-5cb8-445c-8f72-39372705231c","473f747e-805b-4fd8-9892-d4949e24172e","127.0.0.1")
    #Append counter sensor
    client.addSensor("counter",'times', counter)
    print(counter)
    print(client.toJson())
    #Send data
    client.send()

    #Sleep 1 sec
    #time.sleep(1)  

    #Increase counter +1
    counter=counter+1