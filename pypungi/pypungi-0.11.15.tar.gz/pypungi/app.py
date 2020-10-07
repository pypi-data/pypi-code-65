'''
  this is a visualization class
'''
import statsmodels.tsa.api as tsa
import pandas as pd
import zerorpc


class app():
    '''Access to the services provided by the app
    Args:
        appParams (dict) : parameters needed to connect to app
    '''
    
    def __init__(self,port=None,modelHub=None):
        self.port = port 
        self.portStub            = 'tcp://127.0.0.1:'
        self.portGuess           = 4242 #check index.js in app for this number
        self.portSearchIncrement = 123  #check index.js in app for this number
        self.client = zerorpc.Client()
        self.modelHub = modelHub
        self.modelResult = {}  #result of a fitted model
        #connect:
        self.connect()
        
    def connect(self):
        '''
          connects to the pypungi
        '''
        if self.port is not None:
            self.client.connect(self.port)
        else:
            keepTrying = 1
            while keepTrying == 1:
                try: 
                    self.client.connect(self.portStub + str(self.portGuess))
                    self.ping()
                    self.port = self.portGuess
                    keepTrying = 0
                except:  
                    self.portGuess = self.portGuess + self.portSearchIncrement
    
    def ping(self,text='ping'):
        return(self.client.ping(text))
    
    def plot(self,data,select=None):
        '''
          given data and plottype process and send it to app
        '''
        
        if select is None:
            #if isinstance(data,pd.DataFrame) or isinstance(data,pd.Series):
            #    select = 'tseries'
            #else:
            select = 'line'
        
        rawdata = self._transform(data,select)
        #self.client.plot({'data':transmitData, 'plottype':plottype})
        self.client.plot({'rawdata':rawdata,'select':select})
    
    def model(self,modelName,*args,**kwargs):
        '''send model id (eg ols) and the 'app' part of the fitted model'''
        #self.model = statsModel(modelName,*args,**kwargs)
        #self.client.model(  {'id':modelName,'table':fitmodel.model['app'] } )
        self.modelResult = self.modelHub(modelName,*args,**kwargs)
        self.client.model(self.modelResult['app'])
     
    def _transform(self,data,select):
        
        if select in ['line','scatter']:
            return(self._transformDataTypeToDictionary(data)) #if series, transform to dataframe
        elif select in ['tseries']:
            sendData = {}
            sendData['rawdata'] = self._transformDataTypeToDictionary(data)
            sendData['tables'] = self._tsaStats(sendData['rawdata'])
            return(sendData)
        elif select in ['table']:
            return(self._transformDataTypeToDictionary(data,format='split'))
        else:
            return(self._transformDataTypeToDictionary(data))
    
    def _transformDataTypeToDictionary(self,data,format='list'):
        '''
          given data of certain type, transform it to the most common used dictionary.
          if a type of plot, as indicated by select, needs a specific data transformation, do it there.
          Else, introduce a new input var (select) here and use it. 
          
          for data:
          format should be list: eg {'a':[1,2,3,4], 'b':[1,2,3,4]}
          
          for tables:
          default format should be split: eg {'index': [0, 1], 'columns': [0, 1, 2], 'data': [[1, 2, 3], [1, 2, 3]]}
        '''
        if isinstance(data,pd.DataFrame) or isinstance(data,pd.Series):
            if 'date' in data.columns or 'index' in data.columns:
                return(pd.DataFrame(data).rename({'data':'index'},axis='columns').astype({'index':str}).to_dict(format))
            else:
                return(pd.DataFrame(data).assign(index = data.index).astype({'index':str}).to_dict(format))
        elif isinstance(data,list):
                return({'index':list(range(len(data))), '':data    })
        else:
            return(data)
    
    def _tsaStats(self,rawdata):
        '''for data in 'records' format: {'a':[1,2,3]}, calculate time series stats'''
        #TODO: it would be better to round on the app side and give user the option to select precission
        tableStats = {}
        
        #STATIONARITY TESTS
        kpssTable = {'columns': ['variable','stat','p-value','lags','10%','5%', '2.5%', '1%'] }
        data = []
        for var in rawdata.keys():
            if var != 'index':
                kpssTest = list(tsa.kpss(rawdata[var],nlags='auto'))
                kpssTest = [var] + [float(round(x,4)) for x in kpssTest[0:3] + list(kpssTest[3].values())] #float bc can't serialize numpy.int64
                data += [kpssTest]
        kpssTable['data'] = data
        tableStats['kpss'] = kpssTable
        
        adfTable = {'columns': ['variable','stat','p-value','lags','N obs', '1%','5%', '10%', 'IC'] }
        data = []
        for var in rawdata.keys():
            if var != 'index':
                adfTest = list(tsa.adfuller(rawdata[var]))
                adfTest = [var] + [float(round(x,2)) for x in adfTest[0:4] + list(adfTest[4].values())] + [round(adfTest[5],1)] #float bc can't serialize numpy.int64
                data += [adfTest]
        adfTable['data'] = data
        tableStats['adf'] = adfTable
        
        tableStats['describe'] = pd.DataFrame(rawdata).describe().T.reset_index().rename({'index':'variable'}, axis=1).to_dict('split')
        return(tableStats)
        
    
    def stash(self,data):
        
        if isinstance(data,pd.DataFrame):
            rawdata = data.to_dict('list')
        elif isinstance(data,pd.Series):
            rawdata = data.to_dict()
        else:
            rawdata = data
        
        content = {'data':rawdata, 'type': str(type(data))}
        
        self.client.stash(content)
    
    def getStash(self):
        stash = self.client.getStash('')
        if stash['type'] == "<class 'pandas.core.frame.DataFrame'>":
            return(pd.DataFrame(stash['data']))
        elif stash['type'] == "<class 'pandas.core.series.Series'>":
            return(pd.Series(stash['data']))
        else:
            return(stash)
    
    def download(self):
        download = self.client.load('')
        return(download)