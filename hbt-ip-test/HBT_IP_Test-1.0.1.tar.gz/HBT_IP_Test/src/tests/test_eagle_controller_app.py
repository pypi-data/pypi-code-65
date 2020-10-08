import sys
sys.path.insert(0, "../../src/")
sys.path.insert(0, "../../libs/")
import unittest
from apps.eagle_controller_app import msg_app

class Testmsg_handler(unittest.TestCase):


    # start unit test
    def test_start(self):
        testobj = msg_app()
        client, connect_status = testobj.start()
        self.assertEqual(connect_status, 0)
        
    # stop unit test
    def test_stop(self):

        testobj = msg_app()
        client, connect_status = testobj.start()
        if connect_status == 0:
            disconnect_status = testobj.stop()
            self.assertEqual(disconnect_status, 0)
    
   
