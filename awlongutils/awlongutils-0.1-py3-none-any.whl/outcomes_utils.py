# python code for processing a lab table
from .common_utils import (load_df_file, check_schema, load_df_with_dates)
import pandas as pd
import time
import numpy as np


def load_outcomes(csv_filename, yaml_filename, out_format, encoding):
    # load the treatment table and convert dates
    
    dates = ['ABS_STRT_DT', 'ABS_END_DT', 'HOSP_ADMIT_DT', 'HOSP_DISCH_DT']
    date_formats = [out_format]*len(dates)
    df = load_df_with_dates(csv_filename, yaml_filename, dates, date_formats, encoding = 'utf-8')
    
    df = df.drop_duplicates()
    
    # clean the hospitalization dates
    df = clean_HO(df)
    
    return df

def clean_HO(df_HO):
    
    # make missing abs nan
    df_HO.loc[df_HO.ABS_STRT_DT == pd.to_datetime('01/01/1900', errors = 'coerce'),'ABS_STRT_DT'] = pd.NaT

    # remove hosp admit dates that don't make sense
    window_days = 14
    df_HO.loc[(df_HO.HOSP_ADMIT_DT > df_HO.ABS_END_DT + pd.to_timedelta(window_days,unit = 'd')),'HOSP_ADMIT_DT'] = pd.NaT
    df_HO.loc[(df_HO.HOSP_DISCH_DT > df_HO.ABS_END_DT + pd.to_timedelta(window_days,unit = 'd')),'HOSP_DISCH_DT'] = pd.NaT
    df_HO.loc[(df_HO.HOSP_ADMIT_DT < df_HO.ABS_STRT_DT - pd.to_timedelta(window_days,unit = 'd')),'HOSP_ADMIT_DT'] = pd.NaT
    df_HO.loc[(df_HO.HOSP_DISCH_DT < df_HO.ABS_STRT_DT - pd.to_timedelta(window_days,unit = 'd')),'HOSP_DISCH_DT'] = pd.NaT
 
    # fill in missing dates with the absence dates
    df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.HOSP_ADMIT_DT.isnull(),'HOSP_ADMIT_DT'] = df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.HOSP_ADMIT_DT.isnull(),'HOSP_ADMIT_DT'].fillna(df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.HOSP_ADMIT_DT.isnull(),'ABS_STRT_DT'])
    df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.HOSP_DISCH_DT.isnull(),'HOSP_DISCH_DT'] = df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.HOSP_DISCH_DT.isnull(),'HOSP_DISCH_DT'].fillna(df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.HOSP_DISCH_DT.isnull(),'ABS_END_DT'])

    df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.ABS_STRT_DT.isnull(),'ABS_STRT_DT'] = df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.ABS_STRT_DT.isnull(),'ABS_STRT_DT'].fillna(df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.ABS_STRT_DT.isnull(),'HOSP_ADMIT_DT'])
    df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.ABS_END_DT.isnull(),'ABS_END_DT'] = df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.ABS_END_DT.isnull(),'ABS_END_DT'].fillna(df_HO.loc[(df_HO.RSN_CD == 'HO')& df_HO.ABS_END_DT.isnull(),'HOSP_DISCH_DT'])

    
    
    return df_HO


def add_feats_outcomes(df):
    
    # check that rsn_cd is present
    check_schema(df,['RSN_CD'])
    
    for rsn_cd in ['HO','NS','ER','OP','RS','TF','TN']:
    
        df[rsn_cd] = (df['RSN_CD'] == rsn_cd).astype('int')
        
    return df
    
    
def add_max_dates(df_samples, cols_samples, date_samples, df_data):
    # get the max abs_str date before each date_sample for each rsn_cd
    check_schema(df_data,['MRN','RSN_CD','ABS_STRT_DT','ABS_END_DT'])
    
    date_data = 'ABS_STRT_DT'
    
    # merge the samples on the data
    df = pd.merge(df_samples[list(set(cols_samples+[date_samples]))], df_data, on = 'MRN',how = 'left')
    
    # restrict to samples with date_data < data_samples (don't include = since the data is not available)
    df = df.loc[(df[date_data] <(df[date_samples]))]

    # sort by abs strt dt
    df = df.sort_values(['MRN',date_data],ascending = False).reset_index(drop = True)
    
    # groupby rsn_cd and keep the last row 
    df_last_abs = (df.groupby(cols_samples+['RSN_CD']).nth(0)).reset_index()
    
    # pivot the dates by rsn_cd keeping the max (even though there is only one)
    df_table = pd.pivot_table(df_last_abs, values=['ABS_STRT_DT','ABS_END_DT'], 
                                  index=cols_samples,
                                 columns=['RSN_CD'], aggfunc='max')
    
    # rename the columns
    df_table.columns = ['_'.join(col[::-1]).strip() for col in df_table.columns.values]

    # add the missing dates
    expected_dates_all= [[rsn_cd + '_ABS_STRT_DT',rsn_cd +'_ABS_END_DT'] for rsn_cd in ['HO','NS','ER','OP','RS','TF','TN']]
    expected_dates = [item for sublist in expected_dates_all for item in sublist]
    df_table = df_table.reindex(columns = expected_dates)
    
    # make sure all columns are dates
    for e in expected_dates:
        df_table[e] = pd.to_datetime(df_table[e], errors = 'coerce')
    
    df_outcomes_samples = pd.merge(df_samples[cols_samples], df_table.reset_index(), on = cols_samples, how = 'left')
    
    return df_outcomes_samples
    