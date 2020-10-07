'''
'''
import pandas as pd

import statsmodels.tsa.api as tsa
from pypungi.models import ModelHub 
from pypungi.outlets import Outlets  


class hub():
    '''
       
       Default visualization is app. Other outlets are called by first 
       indicating that it will be used.
       Connects
       suggest run:
       
       import pungipy 
       
       pp = pungipy.link() 
       pp.hello()
       pp.plot('gdp')
    '''
    def __init__(self,outlets=['app'],port=None,dbInfo=None,latexPath=None):
        #visualization classes
        self.modelHub = ModelHub()  #transforms data before outlet sends it.  call method evaluates the model: modelName, *args, **kwargs
        self.outlets = Outlets(outlets,port=None,dbInfo=None,latexPath=None,model=self.modelHub)  
        self.app   = self.outlets.outlets['app']['link']
        self.db    = self.outlets.outlets['db']['link']
        self.latex = self.outlets.outlets['latex']['link']
        self.print = self.outlets.outlets['print']['link']
        #transformation classes
    
    
    def __call__(self):
        return(self.app)

if __name__ == '__main__':
    #v = link()  #notice, need a pungi session running for this to work.
    #v.checkConnection()
    #v.plot('gdp')  
    
    #pp = link()
    #pp.plot([1,2,3,4])
    #pp.plot([1,2,3,4,1,1,2,3,1,3,44,1,1],'tseries')
    
    #import numpy as np 
    # 
    #m = pd.DataFrame(np.random.normal(0,1,(100,4)), columns = ['a','asdasdf asdfas','c','d'])
    
    #pp.plot(m,'tseries')
    
    #import numpy
    #import statsmodels.api as sm
    #from main import link
    
    #X = sm.datasets.spector.load(as_pandas=False)
    #Y = sm.add_constant(X.exog, prepend=False)
    #pp = link()
    #pp.model('ols',X.endog,Y)
    
    #pp = hub(['app','print'])
    pp = hub()()
    
    
    pp.plot([1,2,3,4,5],'scatter')
    import numpy as np
    e = np.random.normal(0,1,[100,1])
    x = np.arange(100).reshape([100,1])
    y = 3*x + e
    pp.model('ols',x,3*y)    
    #pp.model('policybrief','hi')