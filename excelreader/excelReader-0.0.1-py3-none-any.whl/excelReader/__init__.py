# -*- coding: utf-8 -*-
"""
Created on Fri Oct  9 15:13:32 2020

@author: Windows-10
"""

# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
from pprint import pprint
import matplotlib.pyplot as plt
import pandas as pd

def data_loading(filename,json_path):
    scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

    creds = ServiceAccountCredentials.from_json_keyfile_name(json_path, scope)

    client = gspread.authorize(creds)
    sheet = client.open(filename).sheet1
    data = sheet.get_all_records()  
    dataframe = pd.DataFrame(sheet.get_all_records())
    print(dataframe.head())
    return dataframe
    
def data_plotting(df,x,y):
    plt.plot(df[x],df[y],'bo')
    plt.xlabel(x)
    plt.ylabel(y)
    plt.title("plotting")
    plt.legend()
    plt.show()

