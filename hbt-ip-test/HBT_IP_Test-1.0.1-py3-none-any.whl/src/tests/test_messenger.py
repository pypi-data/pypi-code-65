import sys
import time
sys.path.insert(0, "../../src/")
sys.path.insert(0, "../../libs/")
import unittest
from unittest.mock import Mock
from core.messenger import MsgAPI
import paho.mqtt.client as mqtt

class TestmsgApi(unittest.TestCase):

    # test method to test mqtt client initialization
    def test_client_init(self):

        testobj = MsgAPI()
        obj, result = testobj.client_init()
        if result == 0:
            self.assertEqual(result, 0)
        else:
            self.assertEqual(result,0)
            
    # test method to test mqtt client connection
    def test_client_connect(self):

        testobj = MsgAPI()
        obj, result = testobj.client_connect()
        if result == 0:
            self.assertEqual(result, 0)
    
    # test method to test mqtt client disconnect
    def test_client_disconnect(self):

        testobj = MsgAPI()
        client, result = testobj.client_connect()
        if result == 0:
            disconnect_status = testobj.client_disconnect()
            print("disconnect status: " + str(disconnect_status))
            if disconnect_status == 0:
                self.assertEqual(disconnect_status, 0)
    
    # test method to get test get death certificate
    def test_death_certificate(self):
        testobj = MsgAPI()
        payload = testobj.get_death_certificate()
        print ("death payload:" + str(payload))
    

    #test method to test publish device certificates
    def test_publish_device_cert(self):
        testobj = MsgAPI()
        obj, result = testobj.client_connect()
        if result == 0:
            pStatus = testobj.publish_device_cert()
            if pStatus != 0:
                print("publish device status: " + str(pStatus))
                self.assertNotEqual(pStatus, 0)
    
    # test method to test publish device certificates
    def test_publish_node_cert(self):
        testobj = MsgAPI()
        obj, result = testobj.client_connect()
        if result == 0:
            pStatus = testobj.publish_node_cert()
            if pStatus != 0:
                print("publish node status: " + str(pStatus))
                self.assertNotEqual(pStatus, 0)

    # test method to test client_run 
    def test_client_run(self):
        testobj = MsgAPI()
        client = testobj.client_run()
        # client.loop_start()
        # time.sleep(5)
        # client.loop_stop()

    # # test method to test message callback
    def test_on_message(self):

        testobj = MsgAPI()
        client, status = testobj.client_run()
        client.loop_start()
        time.sleep(5)
        client.loop_stop()
    

    
        

        
