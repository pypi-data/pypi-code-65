import pandas as pd
import numpy as np
import matplotlib.pyplot as plt



"""
Data Preprocessing Pipeline

1. Missing Values Analyzation
2. Missing Values Imputation
3. Categorical Cardinality
4. Categorical Cardinality removal
"""

#-----------------------Show Missing values ------------------------#

def showMissingValues(data):
    #Total Missing Values
    missing_val = data.isnull().sum()


    #Perchantage of Missing Values
    missing_val_percent = 100 * (data.isnull().sum()) / len(data)

    #Making a Table with the results
    missing_val_table = pd.concat([missing_val,missing_val_percent],axis=1)

    #Rename the columns
    missing_val_percent_ren_col = missing_val_table.rename(
        columns={0: 'Missing Values', 1: '% of Total Values'}

    )
    
    # Sort the table by percentage of missing descending
    missing_val_percent_ren_col = (missing_val_percent_ren_col[
        missing_val_percent_ren_col.iloc[:, 1] != 0].sort_values(
        '% of Total Values', ascending=False).round(1))

    #Print some summary Information
    print("Your dataframe has " +str(data.shape[1]) + "columns. \n"
         "There are " + str(missing_val_percent_ren_col.shape[0]) +
          " columns that have missing values.")

    #Returning the dataframe with missing values
    return missing_val_percent_ren_col



#---------------------------------------------------------------------------

#-----------------------Show Cardinality------------------------------------#
def showCardinality(data):
    #Finding the Categorical values
    cat_vars = [var for var in data.columns if data[var].dtypes == 'O']
    
    cat_var = []
    cat_unique = []
    for var in cat_vars:
        cat_var.append(var)
        cat_unique.append(len(data[var].unique()))
    cat_data = pd.DataFrame(cat_unique,cat_var)
    cat_data = cat_data.rename(
            columns={0: 'Cardinality',1: '% of Total Values'}
                )
    cat_data = cat_data.sort_values(by='Cardinality',ascending=False)
    return cat_data

#---------------------------------------------------------------------------

def numImputer(data,missing_feat,method):
    """
    missing values that are not strictly random, especially in the presence of a great 
    inequality in the number of missing values for the different variables, the mean 
    substitution method may lead to inconsistent bias. Furthermore, this approach adds 
    no new information but only increases the sample size and leads to an underestimate 
    of the errors. Thus, mean substitution is not generally accepted.


    Return Type: dataframe
    """
    df = data.copy()
    #Dropping all the columns that are completely Missing
    df.dropna(how='all',inplace=True)
    
    if method == 'mean':
        df[missing_feat] = df[missing_feat].fillna(df[missing_feat].mean())
    elif method == 'median':
        df[missing_feat] = df[missing_feat].fillna(df[missing_feat].median())
    return df



def catImputer(data,missing_feat,method):
    """
    Mode: For categorical feature we can select to fill in the 
    missing values with the most common value(mode

    Return type: dataframe
    """
    df = data.copy()
    if method == 'mode':
        df[missing_feat] = df[missing_feat].fillna(df[missing_feat].mode()[0],inplace=True)


    elif method == 'new_cat':
        df[missing_feat] = df[missing_feat].fillna('New')
