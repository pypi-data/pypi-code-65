import pandas as pd
import matplotlib.pyplot as plt

def extractData(spreadSheetId,spreadSheetName):
    
    URL = 'https://docs.google.com/spreadsheets/d/{0}/gviz/tq?tqx=out:csv&sheet={1}'.format(spreadSheetId,spreadSheetName)
    df = pd.read_csv(URL)

    print("Select two columns from below list")
    print(list(df))

    x_column = input("X-axis - ")
    y_column = input("Y-axis - ")
    
    df.plot.bar(x=x_column, y=y_column, rot=0)
    plt.show()
    

