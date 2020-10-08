import sys
#sys.path.insert(0, "../libs/")
sys.path.insert(0, "../../src/")
from core.msg_handler import msg_handler

if __name__ == "__main__":
    msgObj = msg_handler()
    client, status = msgObj.start()
    #m.stop()
    print("Everything passed")