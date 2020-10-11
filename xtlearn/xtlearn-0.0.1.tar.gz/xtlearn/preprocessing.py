#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""

Description
----------
Some simple classes to be used in sklearn pipelines for pandas input

Informations
----------
    Author: Eduardo M.  de Morais
    Maintainer:
    Email: emdemor415@gmail.com
    Copyright:
    Credits:
    License:
    Version:
    Status: in development
    
"""
import numpy, math, scipy, pandas
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator,TransformerMixin
from sklearn.preprocessing import MinMaxScaler

class ReplaceValue(BaseEstimator,TransformerMixin):
    '''
    Description
    ----------
    Replace all values of a column by a specific value.
   
    Arguments
    ----------
    feature_name: str
        name of the column to replace

    value:
        Value to be replaced

    replace_by:
        Value to replace

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score
        
    Examples
    ----------
        >>> replace = ReplaceValue('first_col','val','new_val')
        >>> replace.fit_transform(X,y)
    '''
    
    def __init__(self,feature_name,value,replace_by,active=True):
        self.active = active
        self.feature_name = feature_name
        self.value = value
        self.replace_by = replace_by
        
    def fit(self,X,y):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self,X_in):
        X = X_in.copy()
        X[self.feature_name] = X[self.feature_name].replace(self.value,self.replace_by)
        return X


class OneFeatureApply(BaseEstimator,TransformerMixin):
    '''
    Description
    ----------
    Apply a passed function to all elements of column
   
    Arguments
    ----------
    feature_name: str
        name of the column to replace

    apply: str
        String containing the lambda function to be applied

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score
        
    Examples
    ----------
        >>> apply = OneFeatureApply(feature_name = 'first_col',apply = 'np.log1p(x/2)')
        >>> apply.fit_transform(X_trn,y_trn)
    '''
    
    def __init__(self,feature_name,apply = 'x',active=True,variable = 'x'):
        self.feature_name = feature_name
        self.apply = eval('lambda ?: '.replace('?',variable)+apply)
        self.active = active
        
    def fit(self,X,y):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)
        
    def __transformation(self,X_in):
        X = X_in.copy()
        X[self.feature_name] = self.apply(X[self.feature_name])
        return X
    

class FeatureApply(BaseEstimator,TransformerMixin):
    '''
    Description
    ----------
    Apply a multidimensional function to the features.
   
    Arguments
    ----------

    apply: str
        String containing a multidimensional lambda function to be applied. The name of the columns must appear in the string inside the tag <>. Ex. `apply = "np.log(<column_1> + <column_2>)" `

    destination: str
        Name of the column to receive the result

    drop: bool
        The user choose if the old features columns must be deleted.

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score
        
    Examples
    ----------
        >>> apply = FeatureApply( destination = 'result_column', apply = 'np.log1p(<col_1> + <col_2>)')
        >>> apply.fit_transform(X_trn,y_trn)

    '''
    
    def __init__(self,apply = 'x',active=True,destination = None,drop = False ):
        self.apply = apply
        self.active = active
        self.destination = destination
        self.drop = drop 
        
    def fit(self,X,y):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)
        
    def __transformation(self,X_in):
        X = X_in.copy()
        
        cols = list(X.columns)
        variables = self.__get_variables(self.apply,cols)
        len_variables = len(variables)
        
        
        new_column = self.__new_column(self.apply,X)
        
        if self.drop:
            X = X.drop(columns = variables)
        
        if self.destination:
            if self.destination == 'first':
                X[variables[0]] = new_column

            elif self.destination == 'last':
                X[variables[-1]] = new_column
                
            else:
                if type(self.destination) == str:
                    X[self.destination] = new_column 
                else:
                    print('[Warning]: <destination> is not a string. Result is on "new_column"')
                    X['new_column'] = new_column
        else:
            if len_variables == 1:
                X[variables[0]] = new_column
            else:
                X['new_column'] = new_column

        return X
    

    def __findall(self,string,pattern):
        return [i for i in range(len(string)) if string.startswith(pattern, i)]


    def __remove_duplicates(self,x):
        return list(dict.fromkeys(x))
    
    def __get_variables(self,string,checklist,verbose = 1):

        start_pos = self.__findall(string,'<') 
        end_pos   = self.__findall(string,'>') 
        
        prop_variables = self.__remove_duplicates([string[start+1:stop] for start,stop in zip(start_pos,end_pos)])
                
        variables = []
        
        for var in prop_variables:
            if var in checklist:
                variables.append(var)
            else:
                if verbose > 0:
                    print('[Error]: Feature '+var+' not found.')

        return variables
        

    def __new_column(self,string,dataframe):
        cols = list(dataframe.columns)
        variables = self.__get_variables(string,cols,verbose = 0)
        function = eval('lambda '+','.join(variables)+': '+string.replace('<','').replace('>',''))

        new_list = []
        for ind,row in dataframe.iterrows():
            if len(variables) == 1:
                var = eval('[row[\''+variables[0]+'\']]')
            else:
                var = eval(','.join(list(map(lambda st: 'row[\''+st+'\']',variables))))
                
            new_list.append(function(*var))

        return new_list

class Encoder(BaseEstimator,TransformerMixin):
    '''
    Description
    ----------
    Encodes categorical features
   
    Arguments
    ----------

    drop_first: boll
        Whether to get k-1 dummies out of k categorical levels by removing the first level.

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        in the final score

    '''
    
    def __init__(self,active=True,drop_first=True):
        self.active = active
        self.drop_first = drop_first
        
    def fit(self,X,y=None):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)
        
    def __transformation(self,X_in):        
        return pd.get_dummies(X_in,drop_first=self.drop_first)



class MeanModeImputer(BaseEstimator,TransformerMixin):
    '''
 
    Description
    ----------
    Not documented yet
   
    Arguments
    ----------
    Not documented yet
   
    '''
    
    def __init__(self,features = 'all', active = True):
        self.features = features
        self.active   = active
        
    def fit(self,X,y = None):
        
        if self.features == 'all':
            self.features = list(X.columns)

        # receive X and collect its columns
        self.columns = list(X.columns )
        
        # defining the categorical columns of X
        self.numerical_features   = list(X._get_numeric_data().columns)
        
        # definig numerical columns of x
        self.categorical_features = list(set(list(X.columns )) - set(list(X._get_numeric_data().columns)))


        
        self.mean_dict = {} 

        for feature_name in self.features:
            if feature_name in self.numerical_features:
                self.mean_dict[feature_name] = X[feature_name].mean()
            elif feature_name in self.categorical_features:
                self.mean_dict[feature_name] = X[feature_name].mode()[0]

        return self
        
    def transform(self,X,y=None):
        if not self.active:
            return X
        else:
            return self.__transformation(X,y)

    def __transformation(self,X_in,y_in = None):
        X = X_in.copy()
        

        for feature_name in self.features:

            new_list = []

            if X[feature_name].isna().sum() > 0:
                for ind,row in X[[feature_name]].iterrows():
                    if pd.isnull(row[feature_name]):
                        new_list.append(self.mean_dict[feature_name])
                    else:
                        new_list.append(row[feature_name])

                X[feature_name] = new_list
        return X



class ScalerDF(BaseEstimator,TransformerMixin):
    '''

    '''
    
    def __init__(self,max_missing = 0.0 ,active=True):
        self.active = active
        self.max_missing = max_missing
        
    def fit(self,X,y = None):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self,X_in):
        X = X_in.copy()
        scaler = MinMaxScaler(copy=True, feature_range=(0, 1))

        try:
            ind = np.array(list(X.index)).reshape(-1,1)
            ind_name = X.index.name

            df = pd.concat([
                pd.DataFrame(scaler.fit_transform(X),columns = list(X.columns)),
                pd.DataFrame(ind,columns = [ind_name])
            ],1)

            X = df.set_index('Id')
        
        except:
            X = pd.DataFrame(scaler.fit_transform(X),columns = list(X.columns))

        return X

class DataFrameImputer(TransformerMixin):

    def __init__(self):
        """
        https://stackoverflow.com/a/25562948/14204691
        
        Impute missing values.

        Columns of dtype object are imputed with the most frequent value 
        in column.

        Columns of other types are imputed with mean of column.

        """
    def fit(self, X, y=None):

        self.fill = pd.Series([X[c].value_counts().index[0]
            if X[c].dtype == np.dtype('O') else X[c].mean() for c in X],
            index=X.columns)

        return self

    def transform(self, X, y=None):
        return X.fillna(self.fill)


class EncoderDataframe(TransformerMixin):
    """

    """

    def __init__(self,separator = '_',drop_first = True):
        self.numerical_features = None
        self.categorical_features = None
        self.separator = separator
        self.drop_first = drop_first
        
        # 
        
    def fit(self, X, y=None):
        
        # receive X and collect its columns
        self.columns = list(X.columns )
        
        # defining the categorical columns of X
        self.numerical_features   = list(X._get_numeric_data().columns)
        
        # definig numerical columns of x
        self.categorical_features = list(set(list(X.columns )) - set(list(X._get_numeric_data().columns)))
        
        # make the loop through the columns
        new_columns = {}
        
        for col in self.columns:
            
            # if the column is numerica, append to new_columns
            if col in self.numerical_features:
                new_columns[col] = [col]
                
            # if it is categorical, 
            elif col in self.categorical_features:
                
                # get all possible categories
                unique_elements = X[col].unique().tolist()
                
                # drop the last if the user ask for it
                if self.drop_first:
                    unique_elements.pop(-1)
                
                # make a loop through the categories
                new_list = []
                for elem in unique_elements:
                    new_list.append(elem)
                    
                new_columns[col] = new_list
                    
        self.new_columns = new_columns

        return self

    def transform(self, X, y=None):
        X_ = X.reset_index(drop = True).copy()
        
        # columns to be transformed
        columns = X_.columns
        
        # columns fitted
        if list(columns) != self.columns:
            print('[Error]: The features in fitted dataset are not equal to the dataset in transform.')
        
        list_df = []
        for col in X_.columns:
            if col in self.numerical_features:
                list_df.append(X_[col])
            elif col in self.categorical_features:
                for elem in self.new_columns[col]:
                    serie = pd.Series(
                                list(map(lambda x: int(x),list(X_[col] == elem))),
                                name = str(col)+self.separator+str(elem))
                    list_df.append(serie)
        
        return pd.concat(list_df,1)


from sklearn.preprocessing import OrdinalEncoder


class OrdinalEncoderDataframe(TransformerMixin):
    '''
    >>> enc = OrdinalEncoderDataframe(feature_categories = {
                'ExterQual':['Po','Fa','TA','Gd','Ex'],
                'ExterCond':['Po','Fa','TA','Gd','Ex']})
    >>> X = enc.fit_transform(X)
    '''

    def __init__(self,feature_categories):        
        self.feature_categories = feature_categories

    def fit(self, X, y=None):
        self.enc = {}
        for feature_name in self.feature_categories.keys():
            self.enc[feature_name] = OrdinalEncoder([self.feature_categories[feature_name]])
            self.enc[feature_name].fit(np.array(X_trn[feature_name].values).reshape(-1,1))
        return self

    def transform(self, X, y=None):
        X_ = X.copy()
        
        for feature_name in self.feature_categories.keys():
            X_[feature_name] = self.enc[feature_name].transform(np.array(X_[feature_name].values).reshape(-1,1))
            
        return X_