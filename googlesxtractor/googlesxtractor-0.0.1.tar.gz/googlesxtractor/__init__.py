#!/usr/bin/env python
# coding: utf-8

# In[10]:


import pandas as pd
from matplotlib import pyplot as plt


# In[11]:


def xtract(googleSheetId,worksheetName):
        URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(googleSheetId,worksheetName)
        df = pd.read_csv(URL)
        print(df) 
        l = []
        print(df.columns)
        print("select the required x,y for plotting")
        x=input()
        y=input()
        l.append(x)
        l.append(y)
        x = list(df[l[0]].values)
        y = list(df[l[1]].values)

        plt.plot(x,y)
        
        l.clear()
        


# In[ ]:





# In[ ]:





# In[ ]:





# In[ ]:




