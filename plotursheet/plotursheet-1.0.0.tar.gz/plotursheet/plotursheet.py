#__main__.py
from gsheets import Sheets
from configparser import ConfigParser
import pandas as pd
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from PIL import Image 

sheets = Sheets.from_files('client_secrets.json', 'storage.json')
sheets  #doctest: +ELLIPSIS

def main():
    
    # Read URL of the Real Python feed from config file 
    configure=ConfigParser()
    configure.read_string(resources.readtext("reader","config.txt")) 
    url=configure.get("sheet","url")
    x = configure.get("sheet","x")
    y = configure.get("sheet","y")
    n = configure.get("sheet","n")
    df = pd.read_csv('detail.csv')
    s = sheets.get(url)
#load into csv
    s.sheets[n].to_csv('detail.csv', encoding='utf-8', dialect='excel')
    fig = plt.figure()
#plot using the columns
    # If both continuous 
    #Condition and bar plot or scatter options
    plt.scatter(df[x],df[y])
    plt.xlabel(x)
    plt.ylabel(y)
#save images
    fig.savefig('test.png')
# Read image 
    img = Image.open('test.png') 
# Output Images 
    img.show() 
    def plotty():
        



if __name__ == "main":
    main()


