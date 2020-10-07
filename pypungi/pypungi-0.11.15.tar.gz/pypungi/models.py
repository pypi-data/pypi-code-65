'''
  This is a "transformation class" takes data in a format and returns data in a format...
'''

import statsmodels.api as sm
import pandas as pd

class ModelHub:
    #distributes model to the right model class 
    def __init__(self):
        self.model = {}
        self.statsModels = statsModels()
    def __call__(self,modelName,*args,**kwargs):
        if modelName in ['ols']:
            self.model = self.statsModels(modelName,*args,**kwargs)
            return(self.model)
        else :
            outlets = ['model','fit','app','latex','db','print']
            self.model = { outlet : dict(id = modelName,args = args,kwargs = kwargs) for outlet in outlets }
            return(self.model)


class statsModels():
    '''
      self.model should have: "app" key - the data to be sent to app
                              "latex" key - data to be sent to a latex doc
                              "db"  key - data to be stored in a db
    
    '''
    def __init__(self):
        pass
    
    def __call__(self,modelName,*args,**kwargs):
        self.modelName = modelName
        self.args = args
        self.kwargs = kwargs
        self.model = {}
    
        if self.modelName == 'ols':
            self.model['model'] = sm.OLS(*self.args,**self.kwargs)
            self.model['fit']   = self.model['model'].fit()
            self.model['app']   = dict(
                id='ols',
                table = self.model['fit'].summary2().as_html(), 
                residuals = pd.DataFrame({
                    'resid':list(self.model['fit'].resid)}).reset_index().to_dict('list'),
                predict = pd.DataFrame({ 
                    'value' :  list(self.model['fit'].model.endog), 
                    'prediction' : list(self.model['fit'].predict())}
                    ).reset_index().to_dict('list')
            )
            self.model['latex'] = self.model['fit'].summary2().as_latex()
            self.model['db']    = ""
            self.model['print'] = self.model['fit'].summary2()
    
        return(self.model)


if __name__ == '__main__':
    import numpy as np
    e = np.random.normal(0,1,[100,1])
    x = np.arange(100).reshape([100,1])
    y = 3*x + e
    model = ModelHub()
    model('ols',y,100*x)
    