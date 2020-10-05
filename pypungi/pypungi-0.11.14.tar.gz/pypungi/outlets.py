'''
  Link class - the links take data and send them to outlets.  
'''
import statsmodels.tsa.api as tsa
import pandas as pd
import zerorpc

from pypungi.app import app

class Outlets:
    '''Mediates connection to outlet
    
    Attributes:
        connectTo (list) : which outlets to use - app, console, latex, db
        db (dict)        : data needed to connect to databases
        latex (dict)     : data needed to connect to a folder of latex outputs as plots tables
        console (dict)   : data needed to print to console 
    '''
    def __init__(self,outlets=['app'],port=None,dbInfo=None,latexPath=None,model=None):
        '''
        Args:
            connectTo (list) : which outlets - app, console, latex, db 
            port (str)       : the tcp of the app
            db (str)         : db connection info
            latexPath (str)  : path where to save latex outputs
            model (obj)      : a callable object (has __call__) that takes data and transforms it for each outlet
        '''
        self.selectedOutlets = outlets
        self.outlets = dict(
            app  = {
                'port':port,
                'connected':'app' in outlets,
                'link': self.linkApp(port,'app' in outlets,model)
            },
            db = {
                'dbInfo' : dbInfo,
                'connected':'db' in outlets,
                'link': self.linkDB(dbInfo,'db' in outlets,model)
            },
            latex = {
                'latexPath' : latexPath,
                'connected':'latex' in self.selectedOutlets,
                'link': self.linkLatex(latexPath,'latex' in outlets,model)                
            },
            print = {
                'connected':'print' in self.selectedOutlets,
                'link': self.linkPrint('print' in outlets,model)                
            },
        )   
    
    def notConnected(self,*args,**kwargs):
        print('outlet not connected')
    
    def linkApp(self,port,start,model):
        '''connects to app
        
        '''
        if start :
            return(app(port,model))
        else :
            return(self.notConnected)
    
    def linkDB(self,dbInfo,start,model):
        if start :
            print('db connected')
        else :
            return(self.notConnected)        
        
    def linkLatex(self,latexPath,start,model):
        if start :
            print('latex connected')
        else :
            return(self.notConnected)        
            
    def linkPrint(self,start,model):
        if start :
            print('print connected')
        else :
            return(self.notConnected)        
    
    def __call__(self,start):
        if start :
            print('connected')
        else :
            return(self.notConnected)        
