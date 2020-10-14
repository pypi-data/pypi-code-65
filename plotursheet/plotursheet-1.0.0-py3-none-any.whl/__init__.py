from gsheets import Sheets
from configparser import SafeConfigParser
import codecs
from importlib import resources 
import pandas as pd
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image 

def plotty():
    parser = SafeConfigParser()
    sheets = Sheets.from_files('~/client_secrets.json','~/storage.json')
    sheets  #doctest: +ELLIPSIS
    # Read URL of the Real Python feed from config file  
    with codecs.open('config.txt', 'r', encoding='utf-8') as f:
        parser.readfp(f)
    url = parser.get('sheet', 'url')
    x = parser.get('sheet', 'x')
    y = parser.get('sheet', 'y')
    n = int(parser.get('sheet', 'n'))
    print(url,x,y,n)
    s = sheets.get(url)
#load into csv
    s.sheets[n].to_csv('detail.csv', encoding='utf-8', dialect='excel')
    df = pd.read_csv('detail.csv')
    fig = plt.figure()
#plot using the columns
    # If both continuous 
    	#Condition and bar plot or scatter options can be given
    plt.scatter(df[x],df[y])
    plt.xlabel(x)
    plt.ylabel(y)
#save images
    fig.savefig('test.png')
# Read image 
    img = Image.open('test.png') 
# Output Images 
    img.show() 