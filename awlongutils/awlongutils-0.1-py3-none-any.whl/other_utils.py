# python code for processing a KCNG treatment table
from .common_utils import (load_df_file, check_schema,load_df_with_dates)
import pandas as pd
from pandas.api.types import CategoricalDtype
import time
import numpy as np

def make_pt_info_cats(df_pt_info):
    # make the categorical features for RACE_CD, PT_ETHNICITY_CD, MARITAL_STS_CD
    
    # check required columns are there
    check_schema(df_pt_info,['RACE_CD','PT_ETHNICITY_CD','MARITAL_STS_CD'])

    # one hot encode
    cats_race = CategoricalDtype(categories=['W', 'B', 'U', 'A', 'M', 'N', 'O'],  ordered=True) 
    df_pt_info.RACE_CD = df_pt_info.RACE_CD.fillna('U')
    df_pt_info.RACE_CD = df_pt_info.RACE_CD.astype(cats_race)
    race_group_ohe = pd.get_dummies(df_pt_info.RACE_CD, prefix ='RACE')
    df_pt_info = pd.concat([df_pt_info, race_group_ohe],axis = 1)
   
    df_pt_info.PT_ETHNICITY_CD = df_pt_info.PT_ETHNICITY_CD.fillna('U')
    cats_ethnic = CategoricalDtype(categories=['N','H','U'],  ordered=True) 
    df_pt_info.PT_ETHNICITY_CD = df_pt_info.PT_ETHNICITY_CD.astype(cats_ethnic)
    hispanic_group_ohe = pd.get_dummies(df_pt_info.PT_ETHNICITY_CD, prefix ='ETHNIC')
    df_pt_info = pd.concat([df_pt_info, hispanic_group_ohe],axis = 1)

    cats_marital = CategoricalDtype(categories=['D', 'S', 'M', 'L', 'W', 'U', 'C', 'T'],  ordered=True) 
    df_pt_info.MARITAL_STS_CD = df_pt_info.MARITAL_STS_CD.fillna('U')
    df_pt_info.MARITAL_STS_CD = df_pt_info.MARITAL_STS_CD.astype(cats_marital)
    marital_group_ohe = pd.get_dummies(df_pt_info.MARITAL_STS_CD, prefix ='MARITAL')
    df_pt_info = pd.concat([df_pt_info, marital_group_ohe],axis = 1)

    return df_pt_info
    
def add_date_feats_pt_info(df_pt_info, date_samples):
    # check required columns are there
    check_schema(df_pt_info,['DOB','FDD_1','FDD_2','FDD_3',date_samples])
    
    # convert DOB assuming format
    df_pt_info['DOB'] = pd.to_datetime(df_pt_info['DOB'], format = '%d%b%Y:%H:%M:%S', errors = 'coerce',dayfirst=True)
        
    # convert FDDS
    df_pt_info['FDD_1'] = pd.to_datetime(df_pt_info['FDD_1'], errors = 'coerce')
    df_pt_info['FDD_2'] = pd.to_datetime(df_pt_info['FDD_2'], errors = 'coerce')
    df_pt_info['FDD_3'] = pd.to_datetime(df_pt_info['FDD_3'], errors = 'coerce')
    
    # remove FDD's > target date
    df_pt_info.loc[df_pt_info.FDD_1 > df_pt_info[date_samples], 'FDD_1'] = pd.NaT
    df_pt_info.loc[df_pt_info.FDD_2 > df_pt_info[date_samples], 'FDD_2'] = pd.NaT
    df_pt_info.loc[df_pt_info.FDD_3 > df_pt_info[date_samples], 'FDD_3'] = pd.NaT
    # get minimum FDD
    df_pt_info['FDD'] = df_pt_info[['FDD_1','FDD_2','FDD_3']].min(axis = 1)

    # calculate age and vintage
    df_pt_info['Age'] = (df_pt_info[date_samples] - df_pt_info['DOB']).dt.days/365.25
    df_pt_info['Vintage'] = (df_pt_info[date_samples] - df_pt_info['FDD']).dt.days/365.25

    return df_pt_info
    

def process_pt_info(df_samples, df_data, cols_samples, date_samples):
    # This function processes the patient info
    
    # merge data on samples
    assert df_data.MRN.duplicated().sum() == 0, 'duplicated MRNs'
    
    df_pt_info = pd.merge(df_samples[cols_samples],\
                          df_data, on = 'MRN',how = 'left')
    assert len(df_pt_info) == len(df_samples), 'number of samples grew'

    
    
    # check required columns are there
    check_schema(df_pt_info,['DOB','FDD_1','FDD_2','FDD_3','GENDER_CD',\
                             'RACE_CD','PT_ETHNICITY_CD','MARITAL_STS_CD',
                            'PT_HGT_CENTIM_VAL'])

    # add categorical columns
    df_pt_info = make_pt_info_cats(df_pt_info)
    # add features based on date
    df_pt_info = add_date_feats_pt_info(df_pt_info,date_samples)
    
    # calculate extra columns
    df_pt_info['ismale'] = (df_pt_info.GENDER_CD == 'M').astype('int')

    
    return df_pt_info

def load_comorbids(csv_filename, yaml_filename, encoding):
    # load the treatment table and convert dates
    
    dates = ['DX_STRT_DTM']
    date_formats = ['%m/%d/%Y']*len(dates)
    df = load_df_with_dates(csv_filename, yaml_filename, dates, date_formats, encoding = 'utf-8')
   
    return df



def process_comorbids(df_comorbids, df_comorb_groups):
    # This function cleans the comorbidities data
    
    groupby_cols = ['MRN','DX_STRT_DTM']
    
    #delete the period
    df_comorbids['ICD_NBR']= df_comorbids.ICD_NBR.str.replace('.','')
    
    # merge with the groups
    df_comorb_reduced = pd.merge(df_comorbids[['MRN','ICD_NBR','DX_STRT_DTM']], 
                                 df_comorb_groups[['ICD_TEXT','COMORBID_GROUP_DETAIL']].rename(columns = {'ICD_TEXT':'ICD_NBR'}), 
                                 how = 'left', on = 'ICD_NBR')
  
    # fillna with other
    df_comorb_reduced.COMORBID_GROUP_DETAIL = df_comorb_reduced.COMORBID_GROUP_DETAIL.fillna('Other')
    
    # create categoricals
    cats_comorb = CategoricalDtype(categories=['Hepatitis', 'Infection', 'Other', 'Diabetes', 'Anemias',
       'Peripheral_Vascular_or_Arterial_Disease', 'Cardiac_Dysrhythmias',
       'Hyperparathyroidism', 'Ischemic_Heart_Disease',
       'MI_incl_Cardiac_Arrest', 'Congestive_Heart_Failure', 'COPD',
       'Pneumonia', 'Cerebrovascular_Disease', 'Cancer_other_than_skin',
       'Drug_or_Alchohol_Depedence', 'HIV_AIDS',
       'Gastrointestinal_Tract_Bleeding','Hypertension',
       'Amputation','Other_Mental_Disorders','Other_Intellectual_Disorders',
       'Injurious_Wounds','Malnutrition'],  ordered=True) 

    df_comorb_reduced.COMORBID_GROUP_DETAIL = df_comorb_reduced.COMORBID_GROUP_DETAIL.astype(cats_comorb)
    comorbid_group_ohe = pd.get_dummies(df_comorb_reduced.COMORBID_GROUP_DETAIL, prefix ='COMORB')
    df_comorb_reduced = pd.concat([df_comorb_reduced, comorbid_group_ohe],axis = 1)
    
    # get counts
    cols_comorbid = list(comorbid_group_ohe.columns)
    df_comorb = df_comorb_reduced.groupby(groupby_cols)[cols_comorbid].sum()
    df_comorb = df_comorb.reset_index()
    
    # count the total
    df_comorb['COMORBID_COUNT'] = df_comorb.loc[:,[c for c in df_comorb.columns if c not in groupby_cols]].sum(axis = 1)

    return df_comorb

    
