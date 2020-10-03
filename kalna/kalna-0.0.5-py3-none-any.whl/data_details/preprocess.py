import pandas as pd
import numpy as np
import matplotlib.pyplot as plt




def read_data(file):
    data = pd.read_csv(file)
    return data

def show_data(data,no_of_records):
    return data.head(no_of_records)

#Analyse the Missing Values
def analyse_na_values(data,var):
    df = data.copy()
    
    df[var] = np.where(df[var].isnull(),1,0)
    
    df.groupby(var)['SalePrice'].median().plot.bar()
    plt.title(var)
    plt.show()


def show_missing_value(data):
    vars_with_na = [var for var in data.columns if data[var].isnull().sum()>1]
    print(vars_with_na)
    for var in vars_with_na:
        analyse_na_values(data,var)


    

