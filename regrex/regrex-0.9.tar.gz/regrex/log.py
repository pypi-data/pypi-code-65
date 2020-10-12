from datetime import datetime
from colorama import init 
from termcolor import colored 
init() 
localtime = lambda x: datetime.now().strftime('%H:%M:%S')

def log(strvalue):
    print("[{}] {}".format(localtime(None), str(strvalue)))

def newline():
    print("")

def error(strvalue):
    print("[{}]".format(localtime(None)), colored("[ERROR]", 'white', 'on_red'), strvalue)

error("hi")
