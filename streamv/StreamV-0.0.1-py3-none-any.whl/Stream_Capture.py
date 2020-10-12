import socket
import time
import numpy as np
import cv2
import struct
import threading

server_address = ('0.0.0.0',10040)

server_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
client_socket = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)


threadLock_2 = threading.Lock()
threadLock_1 = threading.Lock()

#Server_Thread
class Receive_fhead(threading.Thread):
    def run(self):
        fhead_size = struct.calcsize('l')
        buf,addr = server_socket.recvfrom(fhead_size)
        self.result_1 = buf
        self.result_2 = addr

    def get_result(self):
        threading.Thread.join(self)
        try:
            return self.result_1, self.result_2
        except Exception:
            return None

#Server_Thread
class Receive_data_size(threading.Thread):
    def __init__(self,data_size,addr):
        threading.Thread.__init__(self)
        self.data_size = data_size
        self.addr = addr
    def run(self):
        #threadLock_1.acquire()
        recvd_size = 0
        data_total = b''
        server_socket.sendto(b'okay',self.addr)
        if not recvd_size == self.data_size:
            if self.data_size - recvd_size > 32768:#4096
                print('OKOK')
                data,addr = server_socket.recvfrom(32768)#error
                recvd_size += len(data)
            else:
                print("???")
                data,addr = server_socket.recvfrom(32768)
                recvd_size = data_size
            data_total += data
            self.result = data_total
        #threadLock_1.release()
    def get_result(self):
        threading.Thread.join(self)
        try:
            return self.result
        except:
            print('R')

#Client_Thread
class Send_fhead(threading.Thread):
    def __init__(self,data):
        threading.Thread.__init__(self)
        self.data = data
    def run(self):

        threadLock_2.acquire()
        print('Send fhead...')
        fhead = struct.pack('l',len(self.data))
        #print(len(self.data))
        client_socket.sendto(fhead,server_address)
        back,addr = client_socket.recvfrom(32768)
        back = bytes.decode(back)
        print(back)
        print(len(self.data))
        if(back=='okay'):
            print('gogogo')
            for i in range(len(self.data)//32768+1):
                if 32768*(i+1)>len(self.data):
                    #time.sleep(0.002)
                    client_socket.sendto(self.data[32768*i:],server_address)
                    print('This is send_1: ',len(self.data[32768*i:]))
                else:
                    print('222')
                    client_socket.sendto(self.data[32768*i:32768*(i+1)],server_address)
                    print('This is send_2: ',len(self.data[32768*i:32768*(i+1)]))
        threadLock_2.release()

def Socket_bind(IP,PORT):
    address = (IP,PORT)
    server_socket.bind(address)
    server_socket.settimeout(20)




def Server():

    Thread_1 = Receive_fhead()
    Thread_1.start()
    buf = Thread_1.get_result()[0]
    addr = Thread_1.get_result()[1]
    #fhead_size = struct.calcsize('l')
    #buf,addr = server_socket.recvfrom(fhead_size)
    print('This is buf: ',len(buf))
    if len(buf) == 4:
        data_size = struct.unpack('l',buf)[0]
        recvd_size = 0
        data_total = b''
        server_socket.sendto(b'okay',addr)
        #Thread_2 = Receive_data_size(data_size,addr)
        #Thread_2.start()
        #data_total = Thread_2.get_result()
        while not recvd_size == data_size:
            if data_size - recvd_size > 32768:
                data,addr = server_socket.recvfrom(32768)#error
                print('this is OKOK: ',len(data))
                recvd_size += len(data)
            else:
                data,addr = server_socket.recvfrom(32768)
                print('this is ???: ',len(data))
                recvd_size = data_size
            data_total += data
    else:
        print('error') 
    print(len(data_total))
    frame = np.frombuffer(data_total,np.uint8)
    img_decode = cv2.imdecode(frame,cv2.IMREAD_COLOR)
    #cv2.imshow('result',img_decode)
    #print(img_decode)
    #cv2.waitKey(1)
    return img_decode


def Socket_Client(IP,PORT):
    global server_address
    server_address = (IP,PORT)


def Client_Capture(Img):
    #cap = cv2.VideoCapture(CAP)#CAP

    #ret, frame = cap.read()
    #res = cv2.resize(Img,(Img.shape[0],Img.shape[1]),interpolation=cv2.INTER_AREA)
    img_encode = cv2.imencode('.jpg',Img)[1]
    data_encode = np.array(img_encode)
    data = data_encode.tobytes()
    Thread_1 = Send_fhead(data)
    Thread_1.start()
    #cv2.imshow('hello',frame)

    #cap.release()
    #cv2.destroyAllWindows()
    #client_socket.close()
