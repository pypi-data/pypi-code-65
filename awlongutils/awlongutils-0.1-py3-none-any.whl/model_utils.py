import pandas as pd
import numpy as np
import sys
import time
from os import listdir
from os.path import isdir,isfile

def check_filenames(df_files, data_folder, yaml_folder):
    # checks that the data files are in data_folder and yaml files are in yaml_folder
    
    # check folders exist
    assert isdir(data_folder) | (data_folder == '') ,data_folder + ' missing'
    assert isdir(yaml_folder)| (yaml_folder == ''),yaml_folder + ' missing'
    
    # check all necessary columns are in df_files
    for c in ['dataset','filename','yaml_filename']:
        assert c in df_files.columns, c +' missing from df_files'
    
    # check datasets exist
    for f in df_files.filename:
        assert isfile(data_folder + f),'missing:'+f

    # check yaml files exist
    for y in df_files.yaml_filename:
        assert isfile(yaml_folder + y), 'missing yaml:'+y
    
    # check there are not duplicated datasets
    assert df_files.dataset.duplicated().sum() == 0, 'duplicated datasets in df_files'
def check_dataset_types(df_files, datasets):
    # checks that all the right datasets are contained in df_files
    for c in datasets:
        assert c in df_files.dataset.values, c +' missing from df_files'

def check_input_samples(df_samples, cols_samples, date_samples):
    # checks all inputs for the function make_all_features
    
    # checks that cols_samples and date_samples are in df_samples
    for c in cols_samples:
        assert c in df_samples.columns
    
    assert date_samples in df_samples.columns