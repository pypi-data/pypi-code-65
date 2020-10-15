import IfxPy
from ctypes import *
import threading
import os

def printme1(outValue1):
   "This prints a passed string into this function1"
   print ("\nTest for callback function, value = ", outValue1)
   return

def printme2(outValue2):
   "This prints a passed string into this function2"
   print ("\nTest for callback function, value = ", outValue2)
   return
 
def task1():
    print("Task 1 assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 1: {}".format(os.getpid()))
    temp4 = IfxPy.register_smart_trigger_loop(conn, printme1, temp, "t1", "informix", "sheshdb", "select * from t1;", "label1", False, False)
    #temp4 = IfxPy.register_smart_trigger_loop(conn, printme1, temp, "बस", "informix", "sheshdb_utf8", "select * from बस;", "label1", False, False)
 
def task2():
    print("Task 2 assigned to thread: {}".format(threading.current_thread().name))
    print("ID of process running task 2: {}".format(os.getpid()))
    #temp5 = IfxPy.register_smart_trigger_loop(conn, printme2, temp, "t2", "informix", "sheshdb", "select * from t2;", "label2", False, False)
    temp5 = IfxPy.register_smart_trigger_loop(conn, printme2, temp, "t2", "informix", "sheshdb_utf8", "select * from t2;", "label2", False, False)
 
# if __name__ == "__main__":
             
# ConStr = "SERVER=ol_informix1410;DATABASE=sheshdb_utf8;HOST=127.0.0.1;SERVICE=1067;UID=informix;PWD=xxxx;DB_LOCALE=en_us.utf8;CLIENT_LOCALE=en_us.UTF8;"
ConStr = "SERVER=ol_informix1410;DATABASE=sheshdb;HOST=127.0.0.1;SERVICE=1067;UID=informix;PWD=IFMX4pass;"

conn = IfxPy.connect( ConStr, "", "")

temp = IfxPy.open_smart_trigger(conn, "Unique1", False, 5, 1, 0)
print ("\nFile descriptor = ", temp)
 
# creating threads
t1 = threading.Thread(target=task1, name='t1')
t2 = threading.Thread(target=task2, name='t2')  
 
# starting threads
t1.start()
t2.start()
 
# wait until all threads finish
t1.join()
t2.join()

IfxPy.close(conn)
print ("Done")