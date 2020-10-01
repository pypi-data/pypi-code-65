# python code for processing a lab table
from .common_utils import (load_df_file, check_schema,load_df_with_dates)
import pandas as pd
import time
import numpy as np

def load_labs(csv_filename, yaml_filename, encoding):
    # load the treatment table and convert dates
    
    dates = ['SPEC_DRAW_DT']
    date_formats = ['%m/%d/%Y']*len(dates)
    df = load_df_with_dates(csv_filename, yaml_filename, dates, date_formats, encoding = 'utf-8')
   
    return df

def load_kinetics(csv_filename, yaml_filename, encoding):
    # load the treatment table and convert dates
    
    dates = ['txt_date']
    date_formats = ['%m/%d/%Y']*len(dates)
    df = load_df_with_dates(csv_filename, yaml_filename, dates, date_formats, encoding = 'utf-8')

    df = df.rename(columns = {'txt_date':'kin_date'})
    
    
    return df

