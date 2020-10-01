# python code for processing a KCNG treatment table
from .common_utils import (load_df_file, check_schema)
import pandas as pd
from pandas.api.types import CategoricalDtype
import time
import numpy as np

def load_tx(csv_filename, yaml_filename, encoding):
    # load the treatment table and convert dates
    
    df_tx = load_df_file(csv_filename, yaml_filename, encoding)
    
    # check required columns are there
    check_schema(df_tx,['TX_MACH_ON_DTM','TimeStart','TX_SRC_TREATMENT_ID','FAC_ID'])
    
    # set up the treatment date times
    #df_tx['IDWG_PREV_POST_DT'] = pd.to_datetime(df_tx['IDWG_PREV_POST_DT'], format = '%d%b%Y:%H:%M:%S')
    df_tx['TimeStart'] = df_tx['TimeStart'].fillna('00:01:00')
    df_tx['TX_ON_DATETIME'] = pd.to_datetime(df_tx['TX_MACH_ON_DTM']+' '+df_tx['TimeStart'], format='%m/%d/%Y %H:%M:%S',errors='coerce')
    df_tx['FAC_ID'] = pd.to_numeric(df_tx['FAC_ID'],errors='coerce')
    
    # sort by tx_on_datetime
    df_tx = df_tx.sort_values(['MRN','TX_ON_DATETIME']).reset_index(drop = True)
    
    # drop duplicated rows and keep the last one
    df_tx = df_tx.drop_duplicates(subset = ['TX_SRC_TREATMENT_ID'], keep = 'last')
        
    return df_tx
    
def add_extra_num_feats(df_tx):
    # this function calculates a couple extra features for the treatment table
    
    # checks schema
    check_schema(df_tx, ['PRE_WEIGHT','TX_PRE_AVAIL_WT_NUM',
                                      'IDWG_TX_INTERVAL_DAY_CNT','IDWG_KG_NUM',
                                      'POST_WEIGHT','TX_PRE_TARGET_WT_NUM',
                                      'TX_POST_WT_LOSS_NUM'])
    
    # initialize new columns with nan
    new_cols = ['EDW', 'IDWG_PER_DAY', 'POST_WT_PCT',
           'PRE_WT_PCT', 'IDWG_PCT', 'IDWG_DAY_PCT', 'TARGET_WT_PCT',
           'LOSS_WT_PCT', 'AVAIL_WT_PCT', 'LOSS_TARGET_PCT', 'LOSS_IDWG_PCT']
    for c in new_cols:
        df_tx[c] = np.nan
    
    # estimate edw based on treatment table
    df_tx['EDW'] = df_tx['PRE_WEIGHT']-df_tx['TX_PRE_AVAIL_WT_NUM']

    # calculate IDWG per day
    rows = (df_tx.IDWG_TX_INTERVAL_DAY_CNT != 0.0)& (df_tx.IDWG_TX_INTERVAL_DAY_CNT.notnull())
    df_tx.loc[rows,'IDWG_PER_DAY'] = df_tx.loc[rows,'IDWG_KG_NUM'] / df_tx.loc[rows,'IDWG_TX_INTERVAL_DAY_CNT']
    
    # calculate weights as percent of EDW
    rows = (df_tx.EDW != 0.0) & (df_tx.EDW.notnull())
    df_tx.loc[rows,'POST_WT_PCT'] = df_tx.loc[rows,'POST_WEIGHT']/df_tx.loc[rows,'EDW']
    df_tx.loc[rows,'PRE_WT_PCT'] = df_tx.loc[rows,'PRE_WEIGHT']/df_tx.loc[rows,'EDW']
    df_tx.loc[rows,'IDWG_PCT'] = df_tx.loc[rows,'IDWG_KG_NUM']/df_tx.loc[rows,'EDW']
    df_tx.loc[rows,'IDWG_DAY_PCT'] = df_tx.loc[rows,'IDWG_PER_DAY']/df_tx.loc[rows,'EDW']
    df_tx.loc[rows,'TARGET_WT_PCT'] = df_tx.loc[rows,'TX_PRE_TARGET_WT_NUM']/df_tx.loc[rows,'EDW']
    df_tx.loc[rows,'LOSS_WT_PCT'] = df_tx.loc[rows,'TX_POST_WT_LOSS_NUM']/df_tx.loc[rows,'EDW']
    df_tx.loc[rows,'AVAIL_WT_PCT'] = df_tx.loc[rows,'TX_PRE_AVAIL_WT_NUM']/df_tx.loc[rows,'EDW']

    # calculate loss percents of other weights
    rows = (df_tx.TX_PRE_TARGET_WT_NUM != 0.0)& (df_tx.TX_PRE_TARGET_WT_NUM.notnull())
    df_tx.loc[rows,'LOSS_TARGET_PCT'] = -df_tx.loc[rows,'TX_POST_WT_LOSS_NUM']/df_tx.loc[rows,'TX_PRE_TARGET_WT_NUM']
    rows = (df_tx.IDWG_KG_NUM != 0.0)& (df_tx.IDWG_KG_NUM.notnull())
    df_tx.loc[rows,'LOSS_IDWG_PCT'] = -df_tx.loc[rows,'TX_POST_WT_LOSS_NUM']/df_tx.loc[rows,'IDWG_KG_NUM']

    return df_tx

def add_cat_feats(df_tx):
    # add categorical features to the table
    
    # checks schema
    check_schema(df_tx, ['TX_END_STS_NM', 'TX_POST_DISCH_TO_LOCN_NM','TX_END_REAS_NM'])

    # did treatment end unexpectedly?
    df_tx['TX_END_STS_NM'] = df_tx['TX_END_STS_NM'].fillna('Unexpected')
    df_tx['TX_END_UNEXPECTED'] = (df_tx.TX_END_STS_NM == 'Unexpected').astype('int')

    # add discharge location
    df_tx['TX_POST_DISCH_TO_LOCN_NM'] = df_tx['TX_POST_DISCH_TO_LOCN_NM'].fillna('NO VALUE')
    disch_dict = {'Nursing Home':'Nursing_Home', 'Vascular Access Center':'Vasc_Acc_Ctr',
                  'Assisted Living':'Assisted_Living', 'Skilled Nursing Facility':'Skilled_Nurse_Fac', 
                  'Correctional Facility':'Correctional_Facility',
                    'Home':'home', 'NO VALUE':'Unknown', 'Rehab':'rehab',
                   'Hospital':'hospital', 'Other':'other'}
    df_tx = df_tx.replace({'TX_POST_DISCH_TO_LOCN_NM':disch_dict})
    cat_disch_type = CategoricalDtype(categories=list(set(disch_dict.values())),  ordered=True) 
    df_tx.TX_POST_DISCH_TO_LOCN_NM = df_tx.TX_POST_DISCH_TO_LOCN_NM.astype(cat_disch_type)   
    disch_group_ohe = pd.get_dummies(df_tx.TX_POST_DISCH_TO_LOCN_NM, prefix ='Disc_Loc')
    df_tx = pd.concat([df_tx, disch_group_ohe],axis = 1)

    # add end treatment reason
    df_tx['TX_END_REAS_NM'] = df_tx['TX_END_REAS_NM'].fillna('unknown')
    tx_end_dict = {'Patient Request':'Pt_request', 'Patient Signed off AMA':'AMA',
       'Patient Arrived Late for Tx':'Pt_late', 'System Problem':'System_Problem', 
       'Technical Difficulties':'Tech_Difficulty', 'Per Doctor Order':'MD', 
        'Poor Access Flow':'Poor_Access_Flow', 'Clotted Access':'Clotted_Access',
                   'unknown':'Unknown','Other':'other','Hypotension':'hypotension',
       'Hospitalization':'hospitalization', 'Emergency':'emergency'}
    df_tx = df_tx.replace({'TX_END_REAS_NM':tx_end_dict})
    cat_tx_end_type = CategoricalDtype(categories=list(set(tx_end_dict.values())),  ordered=True) 
    df_tx.TX_END_REAS_NM = df_tx.TX_END_REAS_NM.astype(cat_tx_end_type)   
    end_group_ohe = pd.get_dummies(df_tx.TX_END_REAS_NM, prefix ='End_Reason')
    df_tx = pd.concat([df_tx, end_group_ohe],axis = 1) 
    return df_tx

def get_clinic_stats(g,tx_date):
    return pd.Series({'CLINIC_COUNT':len(g),
                      'LAST_TX_DT': g[tx_date].max()})

def process_tx(df_tx):
    
    # adds extra numerical features
    df_tx = add_extra_num_feats(df_tx)
    # adds categorical features
    df_tx = add_cat_feats(df_tx)
    
    return df_tx
def add_major_clinic(cols_merge,df_samples,cols_samples, samples_date, 
                     df_tx,  tx_date):
    
    # merge the treatments on the samples
    df = pd.merge(df_samples, df_tx, how = 'inner', on = cols_merge)
    
    # filter to treatments in the last 30 days
    df[tx_date+'norm'] = df[tx_date].dt.normalize()
    df[samples_date+'norm'] = df[samples_date].dt.normalize()
    df = df.loc[(df[tx_date+'norm'] >= (df[samples_date+'norm'] - pd.Timedelta(30,'d'))) &\
                 (df[tx_date+'norm'] <= df[samples_date+'norm'])]
    
    
    # count the number of treatments at each clinic
    df_clinic = (df.groupby(cols_samples + ['FAC_ID']).apply(lambda g:get_clinic_stats(g,tx_date))).reset_index()
    df_clinic = df_clinic.sort_values(cols_samples + ['CLINIC_COUNT','LAST_TX_DT'], ascending = False).reset_index(drop = True)
    df_my_clinic = (df_clinic[cols_samples +['FAC_ID']].groupby(cols_samples).nth(0)).reset_index().rename(columns = {'FAC_ID':'MY_FAC_ID'})
    
    df_clinic_samples = pd.merge(df_samples[cols_samples], df_my_clinic[cols_samples + ['MY_FAC_ID']],
                                 how = 'left', on = cols_samples)
    return df_clinic_samples

    
    
    