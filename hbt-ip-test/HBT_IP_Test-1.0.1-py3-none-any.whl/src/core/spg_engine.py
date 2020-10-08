
import sys
import os
sys.path.insert(0, "../../libs/")
sys.path.insert(0, "../../src/")
import random
import string

import time

import paho.mqtt.client as mqtt

import sparkplug_b as sparkplug
from sparkplug_b import *
from sparkplug_b_pb2 import Payload
from common.config import Config
import random
from random import randint
from common.aliasmap import AliasMap
from common.config import Config
from threading import Thread

class SPGEngine:
       
    def __init__(self, node):
        self.connectStatus          =       None
        self.disconnectStatus       =       None
        self.message_recieved       =       None
        self.messageFlag            =       None
        self.deathByteArray         =       None
        self.publishStatus          =       None

        self.node                   =        node
        
        self.client                 =       mqtt.Client(Config.brokerAddr, Config.brokerPort, 60)
        self.client.on_connect      =       self.on_connect                                    #connect callback
        self.client.on_disconnect   =       self.on_disconnect
        self.client.on_message      =       self.on_message
        self.client.on_publish      =       self.on_publish         

    def eventLoop(self):
        
        client, cStatus = self.client_run()

        while (self.node.eventQueue != None):

            print("Inside MSG API.. Is Queue Empty " + str(self.node.eventQueue.empty()))
             
            if not self.node.eventQueue.empty():

                data = self.node.eventQueue.get()
                deviceId = data['deviceId']
                dataKey = data['dataKey']
                dataValue = data['dataValue']
                dataType = data['dataType']

                #TODO: MetricDataType is hardcoded. Data in Queue to be passed as generic
                self.updateDeviceData(deviceId, dataKey, dataType, dataValue ) 

                #### MQTT loop for handling inbound and outbound messages
                for _ in range(2):
                    time.sleep(1)
                    client.loop()
            else:
                time.sleep(1)

    def start(self):
        self.node.subEvent()
        self.eventLoopThread =Thread(target=self.eventLoop)
        self.eventLoopThread.start()

    def stop(self):
        self.node.eventQueue = None

    # connect call back 
    def on_connect(self, client, userdata, flags, rc):

        self.connectStatus = rc
         
        if rc == 0:            
            print("Connected with result code "+str(self.connectStatus))          
        else:
            print("Failed to connect with result code "+str(rc))
            sys.exit()

        # Subscribing in on_connect() means that if we lose the connection and
        # reconnect then subscriptions will be renewed.
        self.subNodeCmd()
        self.subDeviceCmd()
    
    # disconnect callback
    def on_disconnect(self,client, userdata, rc):
        
        self.disconnectStatus = rc
        if rc == 0:        
            print("disconnected with result code "+str(disconnectStatus))
        else:
            print("Failed to connect with result code "+str(disconnectStatus))
    

    #TODO: This API needs to be worked on
    def on_message(self, client, userdata, msg):
        self.messageFlag = 1
        print("Message arrived: " + msg.topic)
        tokens = msg.topic.split("/")
        
        if tokens[0] == "spBv1.0" and tokens[1] == groupInfo.myGroupId and (tokens[2] == "NCMD" or tokens[2] == "DCMD") and tokens[3] == groupInfo.myNodeName:
            inboundPayload = sparkplug_b_pb2.Payload()
            inboundPayload.ParseFromString(msg.payload)
            for metric in inboundPayload.metrics:
                
                #TODO: Platform specific changes to be moved to the platform modules 
                if metric.name == "Eagle Command Controls/Next Server" or metric.alias == AliasMap.Next_Server:
                
                    # 'Node Control/Next Server' is an NCMD used to tell the device/client application to
                    # disconnect from the current MQTT server and connect to the next MQTT server in the
                    # list of available servers.  This is used for clients that have a pool of MQTT servers to connect to.
                    print ("'Node Control/Next Server' is not implemented in this example")

                #TODO: Platform specific changes to be moved to the platform modules 
                elif metric.name == "Eagle Command Controls/Rebirth" or metric.alias == AliasMap.Rebirth:
               
                    # 'Node Control/Rebirth' is an NCMD used to tell the device/client application to resend its full NBIRTH and DBIRTH again.                    
                    # SPGEngine.publish_node_cert(self)
                    # SPGEngine.publish_device_cert(self)
                    print("published re-birth command")

                #TODO: Platform specific changes to be moved to the platform modules 
                elif metric.name == "Eagle Command Controls/Reboot" or metric.alias == AliasMap.Reboot:
                
                    # 'Node Control/Reboot' is an NCMD used to tell a device/client application to reboot
                    # This can be used for devices that need a full application reset via a soft reboot.                    
                    # SPGEngine.publish_node_cert(self)
                    # SPGEngine.publish_device_cert(self)
                    print("Rebooting...........")
                    #os.system('sudo reboot')

                else:
                    print ("Unknown command: " + metric.name)
        else:
            print ("Unknown command...")  

        return self.messageFlag  
    
    def on_publish(self, client, userdata, mid):
        self.publishStatus = mid
        print("publish ack: "+str(self.publishStatus))

    def client_subscribe(self, topic):
        self.client.subscribe(topic)

    def client_publish(self, topic, data):
        byteArray = bytearray(data.SerializeToString())   
        self.client.publish(topic , byteArray , 0, False)
        time.sleep(0.1)      
        print("published data: " + str(topic)) 
        return self.publishStatus
       
    def publishNodeBirthCert(self):
        nodeBirthCert = self.node.getBirthCert()
        birthTopic = self.node.getBirthTopic()
        SPGEngine.client_publish(self, birthTopic, nodeBirthCert)
        return self.publishStatus

    def publishDeviceBirthCert(self):
        deviceMap = self.node.getDeviceMap()
        for deviceId in self.node.getDeviceMap():           
            device = deviceMap[deviceId]
            deviceBirthCert = device.getBirthCert()
            dBirthTopic = device.getBirthTopic()              
            SPGEngine.client_publish(self, dBirthTopic, deviceBirthCert)

        return self.publishStatus

    def subNodeCmd(self):
        SPGEngine.client_subscribe(self,self.node.getCmdTopic())

    def subDeviceCmd(self):
        deviceMap = self.node.getDeviceMap()
        for deviceId in self.node.getDeviceMap():           
            device = deviceMap[deviceId]
            cmdTopic = device.getCmdTopic()              
            SPGEngine.client_subscribe(self,cmdTopic)

    def updateDeviceData(self,deviceId, alias_value,data_type, data_value):

        #TODO: Direct dependency on Metric, to be refactored later  

        deviceMap = self.node.getDeviceMap()
        device = deviceMap[deviceId]
        dataTopic = device.getDataTopic()
        dataPayload = sparkplug.getDdataPayload()
        addMetric(dataPayload, None, alias_value, data_type, data_value)
        SPGEngine.client_publish(self, dataTopic, dataPayload)
 
    def publishNodeDeathCert(self):

        nDeathTopic = self.node.getDeathTopic()     
        deathPayload = self.node.getDeathcert()
        deathByteArray = bytearray(deathPayload.SerializeToString())   
        self.client.will_set(nDeathTopic, deathByteArray, 0, False)
        return deathPayload
    
    def client_init(self):

        self.client.username_pw_set(Config.myUsername, Config.myPassword)                    
        self.client.connect(Config.brokerAddr, Config.brokerPort, 60)                              
 
        # Short delay to allow connect callback to occur
        time.sleep(.01)
        self.client.loop()
        return self.client, self.connectStatus

    def client_connect(self):  

        SPGEngine.client_init(self)                                                        
        return self.client, self.connectStatus

    def client_disconnect(self):
        self.client.disconnect()
        return self.disconnectStatus
    
    def client_run(self):

        # death certificate
        SPGEngine.publishNodeDeathCert(self)

        # Client connect
        SPGEngine.client_connect(self)

        # Publish Node Birth certificates 
        SPGEngine.publishNodeBirthCert(self)

        # Publish Device Birth certificates
        SPGEngine.publishDeviceBirthCert(self)

        return self.client, self.connectStatus
    

        
        
    
        


        
        
        
        
        

        

    
       
        

     




    
