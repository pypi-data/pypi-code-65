from abc import ABCMeta, abstractmethod


import sys
#sys.path.insert(0, "../../../client_libraries/python/")
sys.path.insert(0, "../../libs/")
sys.path.insert(0, "../../src/")

import time
import logging
import random
from queue import Queue

import sparkplug_b as sparkplug
from sparkplug_b import *
from common.aliasmap import AliasMap
from common.config import Config

#Abstract Node 
class Node:

    #__metaclass__ = ABCMeta

    def __init__(self, groupId, nodeId):
        
        self.deviceMap = {}
        self.groupId = groupId
        self.nodeId = nodeId

        logging.basicConfig(level=logging.DEBUG,
                            format='(%(threadName)-9s) %(message)s',)

        self.BUF_SIZE = 100
        self.eventQueue = Queue(self.BUF_SIZE)

        self.__initPayload()
        self.__initNodeInfo()
        self.__initNodeControl()
        self.__createTopics()

        print("Created a node with Id : {id}  ".format(id=self.nodeId))

    def __initPayload(self):
        #Dependency with external library sparkplug  
        self.__payload = sparkplug.getNodeBirthPayload()
        
    def __initNodeInfo(self):
        # Set up the Node Controls
        addMetric(self.__payload, "NodeInfo/id", AliasMap.Entity_Id, MetricDataType.String, self.nodeId)
        # Set up the Node Controls
        #addMetric(self.__payload, "NodeInfo/name", AliasMap.Entity_Name, MetricDataType.String, self.name)

    def __initNodeControl(self):
         # These are Node controlls which are commons across the Nodes, so keeping it in the core module. 
        addMetric(self.__payload, "Eagle Command Controls/Next Server", AliasMap.Next_Server, MetricDataType.Boolean, False)
        addMetric(self.__payload, "Eagle Command Controls/Rebirth", AliasMap.Rebirth, MetricDataType.Boolean, False)
        addMetric(self.__payload, "Eagle Command Controls/Reboot", AliasMap.Reboot, MetricDataType.Boolean, False)


    def getPayload(self):
        return self.__payload

    def __createTopics(self):
        self.__cmd_topic = Config.spgproto + "/" + Config.groupId + "/NCMD/" + self.nodeId + "/#"
        self.__data_topic = Config.spgproto + "/" + Config.groupId + "/NDATA/" + self.nodeId 
        self.__birth_topic = Config.spgproto + "/" + Config.groupId + "/NBIRTH/" + self.nodeId 
        self.__death_topic = Config.spgproto + "/" + Config.groupId + "/NDEATH/" + self.nodeId 

    def getBirthTopic(self):
        return self.__birth_topic

    def getDeathTopic(self):
        return self.__death_topic

    def getCmdTopic(self):
        return self.__cmd_topic

    def getDataTopic(self):
        return self.__data_topic

    def getPayload(self):
        return self.__payload

    def addDevice(self, deviceId, device):
        self.deviceMap[deviceId] = device

    def removeDevice(self, deviceId):
        del self.deviceMap[deviceId]

    def getDevice(self, deviceId):
        return self.deviceMap[deviceId]

    def getDeviceMap(self):
        return self.deviceMap

    def getName(self):
        return self.name

    def getId(self):
        return self.id

    def getBirthCert(self):
        
        return self.__payload

    #@abstractmethod
    def getDeathcert(self):
        pass

    #@abstractmethod
    def subEvent(self):
        pass

    #@abstractmethod
    def execCmd(self):
        pass
