# -*- coding: utf-8 -*-
"""
Created on Sat Jul 10 10:08:27 2020

@author: TechClub
"""
"""

The Phygital Library with following Features.

PWM - 4 Pins (To control 2 Motors, 4 LED strips and 1 RGB LED Strip)
Servo - 3 Pins static (Dedicated pins for Servo)
Configurable I/O - 8 Pins
Configurations for Pins can be:
1. Digital Input
2. Digital Output
3. Analog Input - first 5 Pins
4. Servo


Packet received from Borad : 62 Bytes (Including Start & Stop Bit)
Packet to be Sent to Board : 56 Bytes(Including Start & Stop Bit)

Set Packet for Configurable Pins : 11 Bytes(Including Start & Stop Bit)
"""



from threading import Timer
import serial
import requests
import time
# import EmailTest

#variable for SMS function
global response
global Auth_Key1


#def serialInit(PortName):


SendData = list("&@000000000000000000000000000000000000^")
global receivedData
global data1
global data
global ser
receivedData = ['&',      '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                          '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                          '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                          '0', '0','0','0','0','0','0','0','0','0','0','0',
                          '0', '0', '0', '0', '0', '0', '0', '0', '0', '0',
                          '0', '0','0','0','0','0','0','0','0','0','0','0',
                          
                '^']

setPacket=['&','$','a','a','a','a','a','a','^']

setPacketState="Not"

global timer

def pinMode(PinNum,Mode):
    global setPacketState
    
    if PinNum=='A0':
        Num=1
    if PinNum=='A1':
        Num=2
    if PinNum=='A2':
        Num=3
    if PinNum=='A3':
        Num=4
    if PinNum=='A4':
        Num=5
    if PinNum=='A5':
        Num=6

    # setPacketState="Not"
    
    Mode=Mode.lower()
    
    if Mode=="dinput":
        setPacket[Num+1]="a"
        
    if Mode=="doutput":
        setPacket[Num+1]="b"
        
    if Mode=="ainput":
        setPacket[Num+1]="c"
        
    if Mode=="ultrasonic":
        setPacket[2]="u"
        setPacket[3]="u"
        
    return setPacket

def init(PortName,debug='a'):
    global debug1
    global ser
    global timer
    global setPacket
    global setPacketState
    
    
    
    ser = serial.Serial()
    ser.baudrate=115200
    ser.port=PortName
    ser.open()
    time.sleep(1)
    # ser.flush()
    # time.sleep(1)
    timer=RepeatTimer(0.5,Show)
    timer.start()
    debug1=debug
    return debug1


class RepeatTimer(Timer):
    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)

i=0
def Show():
    # print("in")
    global SendData1
    global i
    global receivedData
    global data
    global data1
    global setPacket
    global setPacketState
    global debug1
    
    # print(setPacketState)
    if setPacketState=="Not":
        print("i")
        str1 = ''.join(setPacket)
        ser.write((str1).encode())
#        print(str1)
        setPacketState="Sent"
        # data=str(ser.readline()) #Received Data in String
        # receivedData=list(data)
        # ser.flush()
        
    else:   
        str1 = ''.join(SendData)
        ser.write((str1).encode())
#        print(str1)
        data=str(ser.readline()) #Received Data in String
#        print("Serial Data Sent")
        data1=data
#        print(data)
    
        if('&' in data):
            receivedData=list(data) #Converted Data to List(Array)
            # print(receivedData)
            if(debug1=='p'):
                print(data)
    return receivedData



def SendSMS(Number,Message,Auth_Key="r"):

    global response
    # global Auth_Key1
    # Channel=1
   # Renuka's AuthKey : s3zHP85MtQjGZqEypi0nxJYc9hlSgX4aFKfCI1buvw2ToUO7mWxBWTtZpbJ7AcQrCdK8UOhV15sFYHe0 
    if Auth_Key=="r":
        Auth_Key1="s3zHP85MtQjGZqEypi0nxJYc9hlSgX4aFKfCI1buvw2ToUO7mWxBWTtZpbJ7AcQrCdK8UOhV15sFYHe0"
    else:
        Auth_Key1=Auth_Key
    
    # if Channel == 1:
    #     Auth_Key1 = "86AmSeoipQBCKcPz2l5ZU1j3XJRsabgMhYLdvDywNuqT9fGr7kJPYjaOrS50UomfLQGtd4IMgHp69R81"

    url = "https://www.fast2sms.com/dev/bulk"

    payload = "sender_id=FSTSMS&message="+":: Muktangan Exploratory's IoT :: "+ Message +"&language=english&route=p&numbers="+str(Number)

    headers = {

    'authorization': Auth_Key1,

    'Content-Type': "application/x-www-form-urlencoded",

    'Cache-Control': "no-cache"

    }
    response = requests.request("POST", url, data=payload, headers=headers)

    return response


    
def setPWM(PinNum,Value):
     Temp1 = list(str(Value))
     if(Value >=100):
        if(PinNum==3):
            SendData[17]=Temp1[0]
            SendData[18]=Temp1[1]
            SendData[19]=Temp1[2]

        if(PinNum==5):
            SendData[20]=Temp1[0]
            SendData[21]=Temp1[1]
            SendData[22]=Temp1[2]
            
        if(PinNum==6):
            SendData[23]=Temp1[0]
            SendData[24]=Temp1[1]
            SendData[25]=Temp1[2]

       

     if(Value <100) and (Value >=10) :
        if(PinNum==3):
            SendData[17]='0'
            SendData[18]=Temp1[0]
            SendData[19]=Temp1[1]

        if(PinNum==5):
            SendData[20]='0'
            SendData[21]=Temp1[0]
            SendData[22]=Temp1[1]
            
        if(PinNum==6):
            SendData[23]='0'
            SendData[24]=Temp1[0]
            SendData[25]=Temp1[1]

        

     if(Value <10)  :
        if(PinNum==3):
            SendData[17]='0'
            SendData[18]='0'
            SendData[19]=Temp1[0]

        if(PinNum==5):
            SendData[20]='0'
            SendData[21]='0'
            SendData[22]=Temp1[0]
            
        if(PinNum==6):
            SendData[23]='0'
            SendData[24]='0'
            SendData[25]=Temp1[0]

        
    



def ConvertAngle(ServoNum,Angle,ServoState):
    # print(ServoState)

    Temp1 = list(str(Angle))
    
    if ServoState=="static":
        if(Angle >=100):
            if(ServoNum==9):
                SendData[8]=Temp1[0]
                SendData[9]=Temp1[1]
                SendData[10]=Temp1[2]
    
            if(ServoNum==10):
                SendData[11]=Temp1[0]
                SendData[12]=Temp1[1]
                SendData[13]=Temp1[2]
    
            if(ServoNum==11):
                SendData[14]=Temp1[0]
                SendData[15]=Temp1[1]
                SendData[16]=Temp1[2]
    
        if(Angle <100) and (Angle >=10) :
            if(ServoNum==9):
                SendData[8]='0'
                SendData[9]=Temp1[0]
                SendData[10]=Temp1[1]
    
            if(ServoNum==10):
                SendData[11]='0'
                SendData[12]=Temp1[0]
                SendData[13]=Temp1[1]
    
            if(ServoNum==11):
                SendData[14]='0'
                SendData[15]=Temp1[0]
                SendData[16]=Temp1[1]
    
        if(Angle <10)  :
            if(ServoNum==9):
                SendData[8]='0'
                SendData[9]='0'
                SendData[10]=Temp1[0]
    
            if(ServoNum==10):
                SendData[11]='0'
                SendData[12]='0'
                SendData[13]=Temp1[0]
    
            if(ServoNum==11):
                SendData[14]='0'
                SendData[15]='0'
                SendData[16]=Temp1[0]
                
    



           

def MoveServo(ServoNum,Angle,ServoState="static"):

    if(Angle>180):
        Angle=180
    if(Angle<0):
        Angle=0
    
    ConvertAngle(ServoNum,Angle,ServoState)

def dWrite(PinNum,Val):
    if(PinNum=='A0'):
        if(Val==1):
            SendData[2]='1'
        else:
            SendData[2]='0'

    if(PinNum=='A1'):
        if(Val==1):
            SendData[3]='1'
        else:
            SendData[3]='0'

    if(PinNum=='A2'):
        if(Val==1):
            SendData[4]='1'
        else:
            SendData[4]='0'

    if(PinNum=='A3'):
        if(Val==1):
            SendData[5]='1'
        else:
            SendData[5]='0'
            
    if(PinNum=='A4'):
        if(Val==1):
            SendData[6]='1'
        else:
            SendData[6]='0'

    if(PinNum=='A5'):
        if(Val==1):
            SendData[7]='1'
        else:
            SendData[7]='0'

   



#All Read functions need to look for 2 positions ahead as additional b' bits
# are received with the data as a part of encoding
    
def aRead(PinNum):
    AData=''.join(receivedData)
    # print(AData)
    if(PinNum=='A0'):
        A1Val=int(AData[9:13])
        return A1Val
    if(PinNum=='A1'):
        A2Val=int(AData[13:17])
        return A2Val
    if(PinNum=='A2'):
        A3Val=int(AData[17:21])
        return A3Val
    if(PinNum=='A3'):
        A4Val=int(AData[21:25])
        return A4Val
    if(PinNum=='A4'):
        A5Val=int(AData[25:29])
        return A5Val
    if(PinNum=='A5'):
        A6Val=int(AData[29:33])
        return A6Val
   



def dRead(PinNum):
    if PinNum=='A0':
        Num=1
    if PinNum=='A1':
        Num=2
    if PinNum=='A2':
        Num=3
    if PinNum=='A3':
        Num=4
    if PinNum=='A4':
        Num=5
    if PinNum=='A5':
        Num=6

    if(receivedData[Num+2]=='1'):

            return 1
    else:
            return 0
            #print(data)
            
            
def ultraSonicRead():
    UData=''.join(receivedData)
    U1Val=int(UData[33:37])
    return U1Val
    
def close():
    global ser
    global timer
    global setPacketState
    
    setPacketState="Not"
    timer.cancel()
    
    ser.close()
    

 # print(aRead(2))

#    if( dRead(3) == 1):
#        print ('Sensed')
#        dWrite(1,1)
#    else:
#         print ('Clear')
#         dWrite(1,0)

##MotorControl(2,"CW",255)
##MotorControl(1,"CCW",9)
#MoveServo(3,0)
#dWrite(1,1)
#dWrite(2,0)
#dWrite(3,1)
#dWrite(4,0)
#
#RGB(0,0,255)

