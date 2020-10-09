
import socket
import os
from sys import getsizeof
import pickle
import math
import struct
import numpy as np

## Last update : 20/09/20 by hykim
## update contents : 
# 09/20
# file transmit checked
# if the received file is already exist, receive process is end
# OpenIQfile function added
# 09/23
# index input translate to int value for matlab compatible
# 09/24
# function names are changed
#09/25
# OpenIQ function is changed
# Input file = pickle file
# Output file = np array

def OpenIQ(main_idx, sub_idx):
    f=open('IQ_'+str(int(main_idx))+'_'+str(int(sub_idx))+'.dat','rb')
    with open('./IQ_pickle.dat', 'rb') as f:
        iq_data = pickle.load(f)
        f.close()
    return iq_data


def SendResult(team_num, main_idx, sub_idx, ans):
    filename = 'ANS_'+str(int(team_num))+'_'+str(int(main_idx))+'_'+str(int(sub_idx))+'.dat'
    with open(filename,'wb') as f:
        pickle.dump(ans,f)
        f.close()
    client = Client()
    client.SocketConnect()
    client.Transmit(main_idx,sub_idx,filename)
    client.SocketClose()

def ChamberTransmit(main_idx,sub_idx):
    filename = 'IQ_'+str(int(main_idx))+'_'+str(int(sub_idx))+'.dat'
    client = Client()
    client.SocketConnect()
    client.Transmit(main_idx,sub_idx,filename)
    client.SocketClose()

def ReceiveIQ(main_idx,sub_idx):
    filename = 'IQ_'+str(int(main_idx))+'_'+str(int(sub_idx))+'.dat'
    
    if not os.path.exists(filename):
        client = Client()
        client.SocketConnect()
        client.Receive(main_idx,sub_idx)
        client.SocketClose()


class Client :
    HOST = '166.104.231.196' 
    PORT = 9998
    
    BufferSize = 1024
    msg_state = ['state0:','state1:','state2:','state3:','state4:']

    ## Team Information--------------------------------------------------------

    def __init__(self):
        pass

    ## Connect to Server---------------------------------------------------------

    def SocketConnect(self):
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_socket.connect((self.HOST, self.PORT)) 
        
    ## Receive file from Server------------------------------------------------
    def Receive(self,main_idx,sub_idx): 
        filename = 'IQ_'+str(main_idx)+'_'+str(sub_idx)+'.dat'
        self.Debug('Receive_file')

        # request to server to receive file 
        # state[0]
        self.client_socket.sendall((self.msg_state[0]+'rx').encode())

        while True:
            msg = self.client_socket.recv(self.BufferSize)
            msg = msg.decode()
            msg_header = msg[0:7]
            msg_payload = msg[7:]

            # check state[0] response 
            # ok    => state[1]
            # error => break
            if msg_header == self.msg_state[0]:
                if msg_payload == 'ok':
                    self.Debug('state0 : Receive allowed')
                    self.client_socket.sendall((self.msg_state[1]+filename).encode())
                else:
                    self.Debug('state0 : Error = Receive not allowed')
                    break
            
            # check state[1] response 
            # filename  => state[2]
            # error     => break
            elif msg_header == self.msg_state[1]:
                if msg_payload == filename:
                    self.Debug('state1 : filename checked')
                    self.client_socket.sendall((self.msg_state[2]).encode())
                else:
                    self.Debug('state1 : '+filename+' is not exist at server')
                    break

            # check state[2] response
            # filesize => state[3]
            elif msg_header == self.msg_state[2]:
                self.Debug('state2 : filesize checked')
                filesize = int(msg_payload)
                self.client_socket.sendall((self.msg_state[3]+'ready_to_receive').encode())

            # check state[3] response
            # start_receive => receive file and state[4]
            # error         => break
            elif msg_header == self.msg_state[3]:
                if msg_payload == 'start_receive':
                    self.Debug('state3 : file receive start')

                    cnt_data =0
                    f = open(filename,'wb') 
                    while True:
                        data = self.client_socket.recv(self.BufferSize)
                        f.write(data)
                        cnt_data +=len(data)
                        if cnt_data >= filesize:
                            break
                    f.close()

                    # filesize check after receive process is done
                    if filesize == os.path.getsize(filename):
                        self.client_socket.sendall((self.msg_state[4]+'ok').encode())
                        self.Debug('state4 : receive success')
                        break
                    else:
                        self.client_socket.sendall((self.msg_state[4]+'error').encode())
                        self.Debug('state4 : Error = filesize error')
                        break
                else:
                    self.Debug('state3 : Error = wait')
                    break

            else:
                self.Debug('Unexpected header')
                break


    ## Send file to Server-------------------------------------------------------
    def Transmit(self,main_idx,sub_idx,filename):
        # check if the file is exist 
        if not os.path.exists(filename):
            self.Debug('Error : The file is not exist')   
        else:
            self.Debug(filename+' is exist')
            filesize = os.path.getsize(filename)

            # request to server to transmit file
            # state[0]
            self.client_socket.sendall((self.msg_state[0]+'tx').encode()) 

            while True:
                msg = self.client_socket.recv(self.BufferSize)
                msg = msg.decode()
                msg_header = msg[0:7]
                msg_payload = msg[7:]

                # check state[0] response
                # ok    => state[1]
                # error => break
                if msg_header == self.msg_state[0]:
                    if msg_payload == 'ok':
                        self.Debug('state0 : Transmit allowed')
                        self.client_socket.sendall((self.msg_state[1]+filename).encode()) 
                    else:
                        self.Debug('state0 : Error = Transmit not allowed')
                        break

                # check state[1] response
                # filename ok   => state[2]
                # error         => break
                elif msg_header == self.msg_state[1]:
                    if msg_payload == filename:
                        self.Debug('state1 : filename checked')
                        self.client_socket.sendall((self.msg_state[2]+str(filesize)).encode())
                    else:
                        self.Debug('state1 : Error = filename')
                        break
                
                # check state[2] response
                # filesize ok    => state[3]
                # filesize error => break
                elif msg_header == self.msg_state[2]:
                    if int(msg_payload) == filesize:
                        self.Debug('state2 : filesize checked')
                        self.client_socket.sendall((self.msg_state[3]+'ready_to_transmit').encode())
                    else:
                        self.Debug('state2 : Error = filesize check')
                        break

                # check state[3] response
                # start_transmit => start transmit file and state[4]
                # error          => break
                elif msg_header == self.msg_state[3]:
                    if msg_payload == 'start_transmit':
                        self.Debug('state3 : file transmit start')
                        with open(filename, "rb") as f:
                            self.client_socket.sendfile(f,0)
                        f.close()
                    else:
                        self.Debuf('state3 : Error = wait')
                        break
                
                # check state[3] response
                # ok    => Transmit sucess
                # error => break
                elif msg_header == self.msg_state[4]:
                    if msg_payload == 'ok':
                        self.Debug('state4 : Transmit success')
                        break
                    else:
                        self.Debug('state4 : Error = filesize error')
                        break
  
                else:
                    self.Debug('Unexpected header')
                    break
  

    ## Disconnect to Server------------------------------------------------------

    def SocketClose(self):
        self.Debug('Disconnect to Server'+str(self.HOST)+':'+str(self.PORT))
        self.client_socket.close()

    def Debug(self, str_):
        debug_on = True
        if debug_on == True :
            print(str_)





    
