import configparser
class Bytum:
    def __init__(self,User,Password,Email='NULL'):
        self.User = User
        self.Password = Password
        self.Email = Email
        self.conf = configparser.ConfigParser()
    def info(self):
        print("UserName:",self.User,"   ""Password:",self.Password)
    def saveasfile(self):
         self.conf['User'] = {'Username':self.User,
                              'Password':self.Password,
                              'Email_Adress':self.Email
                              }
         with open(self.User,'w') as configfile:
             self.conf.write(configfile)
    def readfile(self,rfile):
        try:
            self.conf.read(rfile)
            print(self.conf['User']['Username'])
            print(self.conf['User']['Password'])
            print(self.conf['User']['Email_Adress'])
        except:
            print("Error,cannot get the info.Maybe the file doesn't exist.")
