# import essential libraries
import gspread
from oauth2client.service_account import ServiceAccountCredentials

import pandas as pd

import matplotlib.pyplot as plt
plt.style.use('ggplot')

# styling plt
plt.rcParams['font.family'] = 'Hevletica'
plt.rcParams['font.serif'] = 'Ubuntu'
plt.rcParams['font.monospace'] = 'Ubuntu Mono'
plt.rcParams['font.size'] = 10
plt.rcParams['axes.labelsize'] = 10
plt.rcParams['axes.labelweight'] = 'bold'
plt.rcParams['axes.titlesize'] = 10
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 10
plt.rcParams['figure.titlesize'] = 12

# Set an aspect ratio
width, height = plt.figaspect(1/3)
fig = plt.figure(figsize=(width,height), dpi=400)

# defining api vars
scope = ["https://spreadsheets.google.com/feeds",'https://www.googleapis.com/auth/spreadsheets',"https://www.googleapis.com/auth/drive.file","https://www.googleapis.com/auth/drive"]

# Authorizes Gdrive API
def authorize(filename):
    creds = ServiceAccountCredentials.from_json_keyfile_name(filename, scope)
    client = gspread.authorize(creds)
    return client

# Loads sheet
def dataloader(filename, sheetname):
    client = authorize(filename)
    sheet = client.open(sheetname).sheet1  # Open the spreadhseet
    data = sheet.get_all_records()  # Get a list of all records
    return data

# working with Data
# converts into DataFrame for easier working with python
def to_df(data):
    df=pd.DataFrame(data)
    return df
# plots the graph
def plotter(df, x, y):
    if x!='timestamp':
        fig = plt.figure()
        plt.plot(df[x], df['y'])
        # naming the x axis 
        plt.xlabel(x) 
        # naming the y axis 
        plt.ylabel(y) 
        # giving a title to my graph 
        plt.title(f'{x} VS. {y}') 
        # function to show the plot 
        plt.show() 
        return fig
    else:
        df[x]=pd.to_datetime(df[x], unit='s')
        df = df.set_index(x)
        fig=plt.figure()
        # plotting the data
        df[y].resample('m').mean().plot()
        # df['average_sales'].resample('w').mean().plot()

        # naming the x axis 
        plt.xlabel(x) 
        # naming the y axis 
        plt.ylabel(y) 
        # giving a title to my graph 
        plt.title(f'{x} VS. {y}') 
        # function to show the plot 
        plt.show()
        return fig

