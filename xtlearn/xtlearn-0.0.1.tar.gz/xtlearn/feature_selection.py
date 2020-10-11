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

from tqdm import tqdm
from time import sleep

from sklearn.base import BaseEstimator,TransformerMixin

from sklearn.preprocessing import MinMaxScaler


class FeatureSelector(BaseEstimator,TransformerMixin):
    '''
    Description
    ----------
    This class selects only the desired columns of a pandas dataframe
   
    Arguments
    ----------
    features: list of stirngs
        List of strings containing the column names of the dataframe that the user wants to use. 
        
    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        of selection in the final score
        
    Examples
    ----------
        >>> selector = FeatureSelector(features = ['first_col','sec_col'])
        >>> selector.fit_transform(X,y)
 
    '''
    
    def __init__(self,features,active = True):
        self.features = features
        self.active = active
        
    def fit(self,X,y=None):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            self.X = X.copy() 
            return self.X[self.features]


class FeatureRemover(BaseEstimator,TransformerMixin):
    '''
    Description
    ----------
    This class removes only the desired columns of a pandas dataframe
   
    Arguments
    ----------
    features: list of stirngs
        List of strings containing the column names of the dataframe that the user wants to remove. 
        
    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        of selection in the final score
        
    Examples
    ----------
        >>> selector = FeatureRemover(features = ['first_col','sec_col'])
        >>> selector.fit_transform(X,y)
 
    '''
    
    def __init__(self,features,active = True):
        self.features = features
        self.active = active
        
    def fit(self,X,y=None):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            self.X = X.copy() 
            return self.X.drop(columns = self.features)


class DropMissingDataColumns(BaseEstimator,TransformerMixin):
    '''
    Description
    ----------
    Remove the columns with more than a specified percent of missing data 
   
    Arguments
    ----------
    max_missing: float, default=0.05
        Maximum percent of missing values in column

    active: boolean
        This parameter controls if the selection will occour. This is useful in hyperparameters searchs to test the contribution
        of selection in the final score
        
    Examples
    ----------
        >>> drop = DropMissingDataColumns(max_missing = 0)
        >>> drop.fit_transform(X_trn,y_trn)

    '''
    
    def __init__(self,max_missing = 0.0 ,active=True):
        self.active = active
        self.max_missing = max_missing
        
    def fit(self,X,y=None):
        return self
        
    def transform(self,X):
        if not self.active:
            return X
        else:
            return self.__transformation(X)

    def __transformation(self,X_in):
        X = X_in.copy()
        missing_data = pd.DataFrame(X.isnull().sum().sort_values(ascending=False),columns = ['Missing'])
        max_numb = int(round(self.max_missing*len(X)))
        self.dropped_columns = list(missing_data.query('Missing > %.d' % max_numb).index)

        X = X.drop(self.dropped_columns,axis = 1)
        return X

