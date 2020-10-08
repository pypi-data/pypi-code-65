from abc import ABCMeta, abstractmethod

import sys
#sys.path.insert(0, "../../../client_libraries/python/")
sys.path.insert(0, "../../libs/")
sys.path.insert(0, "../../src/")
import sparkplug_b as sparkplug
from sparkplug_b import *

from common.aliasmap import AliasMap
from common.config import Config

#Abstract Node 
class Device:

    __metaclass__ = ABCMeta

    def __init__(self, groupId, nodeId, deviceId):
        
        self.deviceMap = {}

        self.groupId = groupId
        self.nodeId = nodeId
        self.deviceId = deviceId

        self.__initPayload()
        self.__initDevInfo()
        self.__createTopics()

        print("Created a device with the Id : {id}  ".format(id=self.deviceId))

    def __createTopics(self):
        self.__cmd_topic = Config.spgproto + "/" + Config.groupId + "/DCMD/" + self.nodeId + "/#"
        self.__data_topic = Config.spgproto + "/" + Config.groupId + "/DDATA/" + self.nodeId + "/" + self.deviceId
        self.__birth_topic = Config.spgproto + "/" + Config.groupId + "/DBIRTH/" + self.nodeId + "/" + self.deviceId
        self.__death_topic = Config.spgproto + "/" + Config.groupId + "/DDEATH/" + self.nodeId + "/" + self.deviceId

    def __initPayload(self):
        #Dependency with external library sparkplug  
        self.__payload = sparkplug.getDeviceBirthPayload()
        
    def __initDevInfo(self):
        # Set up the Node Controls
        addMetric(self.__payload, "DeviceInfo/id", AliasMap.Entity_Id, MetricDataType.String, self.deviceId)
        # Set up the Node Controls
        #addMetric(self.__payload, "DeviceInfo/name", AliasMap.Entity_Name, MetricDataType.String, self.deviceName)

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

    def getName(self):
        return self.name

    def getId(self):
        return self.id

    @abstractmethod
    def getBirthCert(self):        
        pass

    @abstractmethod
    def getDeathcert(self):
        pass

    @abstractmethod
    def subsEvent(self):
        pass

    @abstractmethod
    def execCmd(self):
        pass
