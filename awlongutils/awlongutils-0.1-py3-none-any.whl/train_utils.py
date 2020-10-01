# cookie cutter model training
#from .common_utils import (load_df_file, check_schema,load_df_with_dates)
from awlong_utils.awlong_utils import outcomes_utils, txt_utils, common_utils, labs_utils
from awlong_utils import awlong_utils
import pandas as pd
import numpy as np
import pickle
import xgboost as xgb
from os.path import split as path_split, isdir,isfile, abspath
from pathlib import Path

data_folder = '/apps/data/'

cols_samples = ['MRN','QUERY_RUN_DATE']
date_samples = 'QUERY_RUN_DATE'

today = str(pd.to_datetime('today').date())

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_curve, roc_auc_score, accuracy_score, recall_score, precision_score


def make_samples(years, samples='chairside', dx_labels=False):
    # make the rows/observations to be populated with training data (i.e. patient, date)
    # samples: pass in string indicating data source to build samples from
    # years: list of years to include training data from. eg: =['2017','2018','2019']
    # chairside: chairside treatment data
    # hospitalizations: hosp/outcomes data
    # dx_labels: path to diagnosis labels to use for hospitalization ICD codes, if needed for specifying dx groups
    
    if samples == 'chairside':
        path_cs = data_folder + 'HD_treatments/'
        cs = pd.DataFrame()
        
        # read in files into df
        for year in years:
            for q in ['Q1','Q2','Q3','Q4']:
                # should assert somewhere file exists
                if year in ['2017','2018']:
                    print(year + ': ' + q)
                    cs = cs.append(fix_cs_dates(pd.read_csv(path_cs + 'chairside_tx_' + q + '_' + year + '.csv')), sort=False)
                if year in ['2019','2020']:
                    print(year + ': ' + q)
                    try:
                        cs = cs.append(fix_cs_dates(pd.read_csv(path_cs + 'ChairsideTxt_' + q + year + '.csv')), sort=False)
                    except:
                        print('file not found')
        
        # set day after treatment for query run date
        cs['QUERY_RUN_DATE'] = cs['TIME_OFF_DATE'].fillna(cs['SHIFT_DATE']) + pd.Timedelta(1,'d')
        
        # assert dates not missing
        
        df_samples = cs[['MRN','QUERY_RUN_DATE']].copy()
        df_samples = df_samples.drop_duplicates()
        assert df_samples[['MRN','QUERY_RUN_DATE']].duplicated().sum() == 0, 'duplicated samples'
            
    if samples == 'hospitalizations':
        df_samples = build_HO(years, dx_labels=dx_labels)
        
    return df_samples   
            

def fix_cs_dates(cs):
    # fix dates for each file read in, date format depends on file origin
    # drop erroneous treatments
    try:
        cs = cs.loc[cs['TREATMENT_STATUS_ID'].isin([2,6])]  # 2='Absent', 3='Completed'
    except:
        cs = cs.loc[cs['TX_STS_NM']=='Completed']  # only options in this case are completed, started, ended
        
        # make dates dates
    try:
        cs['TIME_OFF_DATE'] = pd.to_datetime(cs['TIME_OFF_DATE'], format='%m/%d/%Y', errors='coerce').copy()
    except:
        cs['TIME_OFF_DATE'] = pd.to_datetime(cs['TX_MACH_OFF_DTM'], format='%m/%d/%Y', errors='coerce').copy()
        
    try:
        cs['SHIFT_DATE'] = pd.to_datetime(cs['SHIFT_DATE'], format='%Y-%m-%d %H:%M:%S', errors='coerce').copy()
    except:
        cs['SHIFT_DATE'] = pd.to_datetime(cs['TX_MACH_ON_DTM'], format='%m/%d/%Y', errors='coerce').copy()
    
    return cs


        
def build_HO(years, dx_labels=False):
    path_hosp = data_folder + 'outcomes/hospital_'
    hosp = pd.DataFrame()
    hosp_temp = pd.DataFrame()
        
    for year in years:
        try:
            hosp_temp = outcomes_utils.load_outcomes(path_hosp + year + '.csv', '../yaml/hospital_icd.yml',
                                                     '%Y-%m-%d %H:%M:%S', encoding='latin-1')
        except:  # if year in progress, file will say 'ytd'
            hosp_temp = outcomes_utils.load_outcomes(path_hosp + year + 'ytd.csv', '../yaml/hospital_icd.yml',
                                                     '%Y-%m-%d %H:%M:%S', encoding='latin-1')
        hosp = hosp.append(hosp_temp, sort=False)
        
    hosp = outcomes_utils.clean_HO(hosp)
        
    if dx_labels:
        hosp = buckets(hosp, dx_labels)
        
    hosp = hosp.drop_duplicates(subset=['MRN','HOSP_ADMIT_DT'], keep='first')
    assert hosp[['MRN','HOSP_ADMIT_DT']].duplicated().sum()==0
    
    return hosp
        
        
def buckets(hosp, dx_labels):
    ICD_buckets = pd.read_csv(dx_labels)
    
    ICD_buckets = ICD_buckets.rename(columns={'DIAGNOSIS_CODE':'ICD10',
                                              'ICD_NBR':'ICD10',
                                              'DIAGNOSIS_DECRIPTION':'ICD10_description',
                                              'ICD_DESC':'ICD10_description',
                                              'DIAGNOSIS_GROUP':'Bucket_Label'})

    hosp = pd.merge(hosp, ICD_buckets[['ICD10','Bucket_Label']].rename(columns={'ICD10':'ICD_1_NBR',
                                                                                'Bucket_Label':'Bucket_Label_1'}),
                    how='left', on='ICD_1_NBR') 
    
    hosp = pd.merge(hosp, ICD_buckets[['ICD10','Bucket_Label']].rename(columns={'ICD10':'ICD_2_NBR',
                                                                                'Bucket_Label':'Bucket_Label_2'}),
                    how='left', on='ICD_2_NBR') 

    hosp = pd.merge(hosp, ICD_buckets[['ICD10','Bucket_Label']].rename(columns={'ICD10':'ICD_3_NBR',
                                                                                'Bucket_Label':'Bucket_Label_3'}),
                    how='left', on='ICD_3_NBR') 

    hosp = pd.merge(hosp, ICD_buckets[['ICD10','Bucket_Label']].rename(columns={'ICD10':'ICD_4_NBR',
                                                                                'Bucket_Label':'Bucket_Label_4'}),
                    how='left', on='ICD_4_NBR') 

    # fill missing buckets with Unknown
    hosp.loc[hosp['Bucket_Label_1'].isnull(), 'Bucket_Label_1'] = 'Unknown'

    
    for bucket in ICD_buckets['Bucket_Label'].unique():
        hosp['HO_' + bucket] = ((hosp.Bucket_Label_1 == bucket) |
                                (hosp.Bucket_Label_2 == bucket) |
                                (hosp.Bucket_Label_3 == bucket) |
                                (hosp.Bucket_Label_4 == bucket)).astype('int')
    

    hosp = hosp.drop_duplicates()
    assert hosp.duplicated().sum() == 0, 'duplicated hospitalizations'

    bucket_list = ['HO_' + bucket for bucket in ICD_buckets['Bucket_Label'].unique()]
    
    hosp['HO_sum'] = hosp[bucket_list].sum(axis=1)
    
    return hosp


def make_outcomes(years, outcomes='hospitalizations', dx_labels=False):
    # the 0 or 1 labels to merge into samples for training
    # currently only for hospitalizations
    if outcomes == 'hospitalizations':
        df_outcomes = build_HO(years, dx_labels=dx_labels)        
        
    return df_outcomes


def make_training_data(df_samples, outcomes, outcomes_date_col, add_prior_hosp=False, dx_target=False):
    # add_prior_hosp adds prior hospitalizations to samples as part of the training data (if also used for outcomes)
    # dx_target: dx group to predict from buckets --> bucket_list above (e.g. 'INF', 'FO')
    assert 'QUERY_RUN_DATE' in df_samples.columns, "'QUERY_RUN_DATE' missing from samples"
    assert outcomes_date_col in outcomes.columns, outcomes_date_col + " missing from outcomes"
    
    df_left = df_samples.sort_values('QUERY_RUN_DATE').reset_index(drop=True)
    df_right = outcomes.sort_values(outcomes_date_col).reset_index(drop=True)

    df_samples_ho = pd.merge_asof(df_left, df_right, left_on='QUERY_RUN_DATE', right_on=outcomes_date_col,
                                  by='MRN', direction='forward', allow_exact_matches=True)
    
    if add_prior_hosp:
        df_left = df_samples.sort_values('QUERY_RUN_DATE').reset_index(drop=True)
        df_right = outcomes.rename(columns={'HOSP_ADMIT_DT':
                                            'LAST_HOSP_ADMIT_DT',
                                            'HOSP_DISCH_DT':
                                            'LAST_HOSP_DISCH_DT'}).sort_values('LAST_HOSP_ADMIT_DT').reset_index(drop=True)

        df_prior_ho = pd.merge_asof(df_left, 
                                    df_right[['MRN','LAST_HOSP_ADMIT_DT','LAST_HOSP_DISCH_DT']],
                                    left_on='QUERY_RUN_DATE',
                                    right_on='LAST_HOSP_ADMIT_DT',
                                    by='MRN',
                                    direction='backward',
                                    allow_exact_matches=True)
        n = len(df_samples_ho)
        df_samples_ho = pd.merge(df_samples_ho, df_prior_ho, on=['MRN','QUERY_RUN_DATE'], how='left')
        assert len(df_samples_ho) == n, 'something went wrong: length of samples changed'
        
    # remove rows where patient currently admitted
    rows_current_admit = (df_samples_ho.QUERY_RUN_DATE > df_samples_ho.LAST_HOSP_ADMIT_DT) &\
                         (df_samples_ho.QUERY_RUN_DATE <= df_samples_ho.LAST_HOSP_DISCH_DT)
        
    df_samples_ho = df_samples_ho.loc[~rows_current_admit]
    
    if dx_target:
        # andy's code originally set targets from days 0-6 of query run date,
        # which means many of the high predictions were for notes stating PT discharged to ER, ambulance called, etc.
        df_samples_ho['OUTPUT_LABEL'] = ((df_samples_ho['HO_' + dx_target] > 0) &
                                         ((df_samples_ho['HOSP_ADMIT_DT'] -
                                           df_samples_ho['QUERY_RUN_DATE']).dt.days < 8) &  # <8 so it's 1-7
                                         ((df_samples_ho['HOSP_ADMIT_DT'] -
                                           df_samples_ho['QUERY_RUN_DATE']).dt.days >= 1)).astype('int')  # added >=1
    else:
        df_samples_ho['OUTPUT_LABEL'] = (((df_samples_ho['HOSP_ADMIT_DT'] - df_samples_ho['QUERY_RUN_DATE']).dt.days < 8) &
                                          ((df_samples_ho['HOSP_ADMIT_DT'] - df_samples_ho['QUERY_RUN_DATE']).dt.days >= 1)).astype('int')
    
    return df_samples_ho


def filter_tx(df_tx_all, df_samples, date_samples):
    # from pred041_utils
    df_tx_all = pd.merge(df_tx_all, df_samples, on = ['MRN'], how = 'left')
    df_tx_all = df_tx_all.loc[(df_tx_all.TX_ON_DATETIME < df_tx_all[date_samples]) &
                              (df_tx_all.TX_ON_DATETIME >= (df_tx_all[date_samples] - pd.Timedelta(90,'d')))]
    df_tx_all = df_tx_all.drop([date_samples],1)
    df_tx_all = df_tx_all.drop_duplicates()
    return df_tx_all


def get_feats_tx(df_samples, cols_samples, date_samples,df_data):
    cols_data = ['PRESTANDSBP', 'PRESTANDDBP', 'PRESITSBP', 'PRESITDBP', 'PRE_WEIGHT', 'PRE_TEMP',
                 'POSTSTANDSBP', 'POSTSTANDDBP', 'POSTSITSBP', 'POSTSITDBP', 'QB', 'QD',
                 'POST_WEIGHT', 'POST_TEMP', 'SALINE', 'TXT_TIME', 'OLC', 'KECN', 'TX_PRE_TARGET_WT_NUM',
                 'TX_PRE_AVAIL_WT_NUM', 'TX_PRE_RESP_RATE', 'TX_PRE_PULSE_RATE', 'TX_POST_WT_LOSS_NUM',
                 'TX_POST_RESP_RATE', 'TX_POST_PULSE_RATE', 'IDWG_TX_INTERVAL_DAY_CNT', 
                 'IDWG_PREV_POST_WGT_NUM', 'IDWG_KG_NUM', 'EDW', 'IDWG_PER_DAY', 'POST_WT_PCT', 'PRE_WT_PCT',
                 'IDWG_PCT', 'IDWG_DAY_PCT', 'TARGET_WT_PCT', 'LOSS_WT_PCT', 'AVAIL_WT_PCT',
                 'LOSS_TARGET_PCT', 'LOSS_IDWG_PCT', 'TX_END_UNEXPECTED', 
                 'TX_TOT_HEPARIN_ADMIN_QTY', 'TX_PRE_O2SAT_PCT', 'TX_POST_O2SAT_PCT',  # newly added
                 'Disc_Loc_Vasc_Acc_Ctr', 'Disc_Loc_Skilled_Nurse_Fac', 'Disc_Loc_Correctional_Facility',
                 'Disc_Loc_Unknown', 'Disc_Loc_rehab', 'Disc_Loc_Nursing_Home', 'Disc_Loc_hospital', 'Disc_Loc_other',
                 'Disc_Loc_Assisted_Living', 'Disc_Loc_home', 'End_Reason_Pt_late', 'End_Reason_Tech_Difficulty',
                 'End_Reason_Pt_request', 'End_Reason_Unknown', 'End_Reason_Poor_Access_Flow',
                 'End_Reason_hypotension', 'End_Reason_AMA', 'End_Reason_emergency', 'End_Reason_other',
                 'End_Reason_MD', 'End_Reason_System_Problem', 'End_Reason_hospitalization', 'End_Reason_Clotted_Access']
    
    tx_date = 'TX_ON_DATETIME'
    window_days = [7, 30, 90]

    # groupby mrn and date
    if df_data.duplicated(subset = [tx_date,'MRN']).sum() == 0:
        df_data_group = df_data
    else:
        df_data_group = df_data[cols_data +[tx_date,'MRN']].groupby(['MRN',tx_date]).mean()
        df_data_group = df_data_group.reset_index()
    assert df_data_group.duplicated(subset = [tx_date,'MRN']).sum() == 0, 'duplicated dates'
    # preprocess
    #df_clinic_samples = txt_utils.add_major_clinic(['MRN'],df_samples,cols_samples, date_samples, 
    #                 df_data,  tx_date)

    df_tx_samples = common_utils.preprocess_last_history(['MRN'],df_samples, cols_samples, date_samples, \
                           df_data_group,cols_data, tx_date, \
                           window_days,by_col = 0)
    #df_tx = pd.merge(df_tx_samples, df_clinic_samples, on = cols_samples, how = 'left')
    df_tx = df_tx_samples
    
    df_tx['days_last_tx'] = (df_tx[date_samples] - df_tx[tx_date]).dt.total_seconds()/(24*3600)
    
    assert len(df_tx) == len(df_samples),'number of samples changed'
    return df_tx


def get_feats_labs(df_samples, cols_samples, date_samples, df_data):

    labs_date = 'SPEC_DRAW_DT'
    window_days = [7,30,90,180]
    #'VitaminD','BunCreat'
    cols_data = ['Albumin', 'Sodium', 'HGB', 'WBC',
       'Neutrophils', 'Lymphocytes', 'Creatinine', 'TSAT', 'Potassium',
       'Phosphorus', 'Chloride', 'Ferritin', 'URR', 'Calcium', 'Bicarbonate',
       'IntactPTH', 'HgbA1C', 'CaCorrect', 'VitaminD', 'VitaminB12',
       'Platelets', 'PT', 'BUN', 'Monocytes', 'Eosinophils', 'Basophils',
       'BunCreat']

    for c in ['MRN','SPEC_DRAW_DT']:
        assert c in df_data.columns, c + ' not in df_data'
    
    for c in cols_samples:
        assert c in df_samples, c + ' not in df_samples'
    
    common_utils.check_schema(df_data,cols_data + [labs_date])  
    
    # groupby mrn and date
    df_data_group = df_data[cols_data +[labs_date,'MRN']].groupby(['MRN',labs_date]).mean()
    df_data_group = df_data_group.reset_index()
    
    # preprocess
    df_labs_samples = common_utils.preprocess_last_history(['MRN'],df_samples, cols_samples, date_samples, \
                           df_data_group,cols_data, labs_date, \
                           window_days, by_col = 1)
    assert len(df_labs_samples) == len(df_samples),'number of samples changed'
    
    # labs
    labs_fcn_cds = ['MEAN','MAX','MIN','STD']
    labs_cols_diff = ['MEAN','MAX','MIN']
    labs_days = [str(w) for w in window_days]   
    cols_labs_hist = [c+'_' +n + '_' + f for c in cols_data for n in labs_days for f in labs_fcn_cds ]
    cols_labs_hist_delta = [col + '_' + day + '_'+m + '_DIFF' for col in cols_data for day in labs_days for m in labs_cols_diff]
    cols_labs = cols_data+ cols_labs_hist+ cols_labs_hist_delta
    
    return df_labs_samples[cols_samples + cols_labs]


def filter_outcomes(df_outcomes_all, df_samples, date_samples):
    
    df_outcomes_all = pd.merge(df_outcomes_all, df_samples, on = ['MRN'], how = 'inner')

    df_outcomes_all = df_outcomes_all.loc[(df_outcomes_all.ABS_STRT_DT < df_outcomes_all[date_samples])]

    df_outcomes_all = df_outcomes_all.drop([date_samples],1)
    df_outcomes_all = df_outcomes_all.drop_duplicates()
    return df_outcomes_all


def get_feats_outcomes(df_samples, cols_samples, date_samples,df_data):
    
    # get counts of temp abs
    
    cols_data = ['HO','NS','ER','OP','RS','TF','TN']
    outs_date = 'ABS_STRT_DT'
    window_days = [30, 90,180]

    df_outs_samples = common_utils.preprocess_sums(['MRN'],df_samples, cols_samples, date_samples, \
                       df_data,cols_data, outs_date, window_days)
    assert len(df_outs_samples) == len(df_samples),'number of samples changed'
    
    cols = [c for c in df_outs_samples.columns if c not in cols_samples]
    
    df_outs_samples[cols] = df_outs_samples[cols].fillna(0)
    
    # get the max date 
    df_max_date = outcomes_utils.add_max_dates(df_samples, cols_samples, date_samples, df_data)
    
    # merge
    df = pd.merge(df_outs_samples, df_max_date, on = cols_samples, how = 'left')
    
    # calculate features for the dates
    for cc in cols_data:
        df['days_last_start_'+cc]= (df[date_samples] - df[cc+'_ABS_STRT_DT']).dt.days
        df['days_last_end_'+cc]= (df[date_samples] - df[cc+'_ABS_END_DT']).dt.days
        df['last_stay_'+cc]= (df[cc+'_ABS_END_DT'] - df[cc+'_ABS_STRT_DT']).dt.days
        df['ever_'+cc] = (~df['days_last_start_'+cc].isnull()).astype('int')

    assert len(df) == len(df_samples),'number of samples changed'
    return df


def clean_notes(df, col):
    # clean the notes for column col by filling in any missing notes with a space
    # check for missing columns
    for c in ['CLINICALNOTETEXT']:
        assert c in df.columns, c + ' not in df'

    assert col in df.columns, col + ' not in df'
        
    # fill missing data
    df[col] = df[col].fillna(' ')
    return df


def tokenizer_better(text):
    # tokenize the text by replacing punctuation and numbers with spaces and lowercase all words
    punc_list = string.punctuation+'0123456789'
    t = str.maketrans(dict.fromkeys(punc_list, " "))
    text = text.lower().translate(t)
    tokens = word_tokenize(text)
    return tokens


def filter_ecc_notes(df_ecc_notes_all, df_samples, date_samples):
    
    df_ecc_notes_all = pd.merge(df_ecc_notes_all, df_samples, on=['MRN'], how='inner')
    #print(df_ecc_notes_all.columns)
    df_ecc_notes_all = df_ecc_notes_all.loc[(df_ecc_notes_all.ENTEREDDT <= df_ecc_notes_all[date_samples]) & 
                                           (df_ecc_notes_all.ENTEREDDT >= (df_ecc_notes_all[date_samples] - pd.Timedelta(30,'d')))]

    #df_ecc_notes_all = df_ecc_notes_all.drop([date_samples],1)
    df_ecc_notes_all = df_ecc_notes_all.drop_duplicates()
    return df_ecc_notes_all


def filter_chairside_notes(df_chairside_notes_all, df_samples, date_samples):
    
    df_chairside_notes_all = pd.merge(df_chairside_notes_all, df_samples, on = ['MRN'], how = 'inner')

    df_chairside_notes_all = df_chairside_notes_all.loc[(df_chairside_notes_all.TIME_ON_DATE <= df_chairside_notes_all[date_samples]) & 
                                           (df_chairside_notes_all.TIME_ON_DATE >= (df_chairside_notes_all[date_samples] - pd.Timedelta(30,'d')))]

    #df_chairside_notes_all = df_chairside_notes_all.drop([date_samples],1)
    df_chairside_notes_all = df_chairside_notes_all.drop_duplicates()
    return df_chairside_notes_all


def join_chairside_notes(df):     
    # fill nan and join the notes
    for c in ['PRE_OBSERVATION','PRE_OTHER_COMMENTS','POST_OBSERVATION','POST_OTHER_COMMENTS','NOTE_TEXT','RN_NOTES']:
        df[c] = df[c].fillna('')
    df['ALL_NOTES'] = df['PRE_OBSERVATION'] + '. ' + \
                      df['PRE_OTHER_COMMENTS']+ '. ' + \
                      df['POST_OBSERVATION']+ '. ' + \
                      df['POST_OTHER_COMMENTS']+ '. ' + \
                      df['NOTE_TEXT']+ '. ' + \
                      df['RN_NOTES']
    df[['ALL_NOTES']] = df[['ALL_NOTES']].fillna('')
    # check that there are no missing values
    assert df[['ALL_NOTES']].isnull().sum().sum() == 0, 'There should not be any missing numbers'
    
    return df


def process_bp_med(df_samples, cols_samples, date_samples, df_bp):
    # from andy's pred041 model
    # processes the bp meds
    
    df_bp['BP_MED'] = 1
    
    df_bp_merge = pd.merge(df_samples, df_bp, how = 'left', on = 'MRN')
    
    # filter to active BP meds
    df_bp_merge = df_bp_merge.loc[(df_bp_merge['DERIVED_START_DATE'] < df_bp_merge[date_samples])&
                             (df_bp_merge['STOP_DATE'].isnull() | (df_bp_merge['STOP_DATE'] >= df_bp_merge[date_samples]))]
    
    # count number of active BP meds
    df_bp_num = df_bp_merge.groupby(['MRN','QUERY_RUN_DATE']).BP_MED.sum()
    # maximum date
    df_bp_max_dt = df_bp_merge.groupby(['MRN','QUERY_RUN_DATE']).DERIVED_START_DATE.max()
    
    # concatenate
    df_bp_samples = pd.concat([df_bp_num, df_bp_max_dt],axis = 1).reset_index()
    
    # calculate days since last start
    df_bp_samples['days_last_start_bp_med'] = (df_bp_samples['QUERY_RUN_DATE'] - df_bp_samples['DERIVED_START_DATE']).dt.total_seconds()/(24*3600)
    
    # merge on samples
    df_bp_samples = pd.merge(df_samples, df_bp_samples, on = cols_samples, how = 'left')
    # fill missing
    df_bp_samples['BP_MED'] = df_bp_samples['BP_MED'].fillna(0)
        
    assert len(df_bp_samples) == len(df_samples)
    
    return df_bp_samples[cols_samples+['BP_MED','days_last_start_bp_med']]



# wrappers for the above functions

def add_chairside(samples, years):
    yaml_filename = '../yaml/Txt_dev.yml'
    
    cs = pd.DataFrame()
    for year in years:
        for q in ['Q1_','Q2_','Q3_','Q4_']:  # can limit quarters for testing
            print('reading cs treatments for ' + q + year)
            try:
                cs = cs.append(txt_utils.load_tx(data_folder+'HD_treatments/TX_KCNG_' + q + year + '.csv',
                                                 yaml_filename, encoding='latin-1'))
            
                cs = cs.loc[cs['MRN'].isin(samples['MRN'].unique())]
                cs = filter_tx(cs, samples, date_samples)
                print('loaded')
            except:
                print('file not found')
    
    print('processing chairside treatments')
    #df_tx_filt = filter_tx(cs, samples, date_samples)
    
    df_tx_process = txt_utils.process_tx(cs)  # df_tx_filt
    
    df_tx_samples = get_feats_tx(samples, cols_samples, date_samples, df_tx_process)
    print('finished chairside treatments')
    return df_tx_samples


def add_labs(samples, years):
    yaml_filename = '../yaml/labs_dev.yml'
        
    df_labs_all = pd.DataFrame()
    for year in years:
        print('reading ' + year + ' labs')
        df_labs_all = df_labs_all.append(labs_utils.load_labs(data_folder+'labs/RawLabs' + year + '.csv',
                                                              yaml_filename, encoding='latin-1'), sort=False)
        print('loaded')
        
    print('making labs features')
    df_labs_samples = get_feats_labs(samples, cols_samples, date_samples, df_labs_all)
    print('finished labs')
    return df_labs_samples


def add_absences(samples, years):
    yaml_filename = '../yaml/Absence_prod.yml'
    
    df_outs = pd.DataFrame()
    
    for year in years:
        print('reading ' + year + ' absences')
        df_outs = df_outs.append(outcomes_utils.load_outcomes(data_folder + 'outcomes/Absence_' + year + '.csv',
                                                              yaml_filename, '%m/%d/%Y', encoding='utf-8'))
        print('loaded')
    
    print('making absence features')
    df_outs = filter_outcomes(df_outs, samples, date_samples)
    
    df_outs = outcomes_utils.add_feats_outcomes(df_outs)
    
    df_outs = get_feats_outcomes(samples, cols_samples, date_samples, df_outs)
    print('finished absences')
    return df_outs
    

def add_ecc_notes(samples, years):
    ecc_notes = pd.DataFrame()
    
    for year in years:
        for q in ['Q1_', 'Q2_', 'Q3_', 'Q4_']:
            print('loading ' + q + year)
            my_file = Path(data_folder + 'ecube_notes/ecube_notes_' + q + year + '.csv')
            if my_file.is_file():
                temp = pd.read_csv(my_file)
                # deal with date format differences
                try:
                    temp['ENTEREDDT'] = pd.to_datetime(temp['ENTEREDDT'], errors='raise')
                    temp['ENTEREDDT_DT'] = pd.to_datetime(temp['ENTEREDDT'], errors='coerce').dt.date.copy()
                except:
                    temp['ENTEREDDT'] = pd.to_datetime(temp['ENTEREDDT'], format='%d%b%Y:%H:%M:%S.%f', errors='raise')
                    temp['ENTEREDDT_DT'] = pd.to_datetime(temp['ENTEREDDT'], errors='coerce').dt.date.copy()
                if 'ClinicalNoteText' in temp.columns:
                    temp = temp.rename(columns={'ClinicalNoteText':'CLINICALNOTETEXT'})
                ecc_notes = ecc_notes.append(temp)
                print('loaded')
            else:
                print('file not found')
    
    print('processing ecc notes')
    ecc_notes['MRN'] = pd.to_numeric(ecc_notes['MRN'], errors = 'coerce')
    ecc_notes = ecc_notes.loc[ecc_notes.MRN.notnull()]
    ecc_notes['MRN'] = ecc_notes['MRN'].astype('int64')
    
    ecc_notes = ecc_notes.loc[ecc_notes['MRN'].isin(samples['MRN'].unique())]
    # multiple submitted same day, different time
    # from andy's notebook:
    # Since there are a bunch of notes that get submitted at exact same time,
    # let's drop duplicated times and ignore the loss of data for training purposes.
    # Concatenating notes will take forever at this scale for now. 
    ecc_notes = ecc_notes.drop_duplicates(subset=['MRN','ENTEREDDT_DT'], keep='first')
    
    #ecc_notes = ecc_notes.rename(columns={'ClinicalNoteText':'CLINICALNOTETEXT'})
    
    ecc_notes = clean_notes(ecc_notes, 'CLINICALNOTETEXT')
    
    ecc_notes = filter_ecc_notes(ecc_notes, samples, date_samples)
    
    #vect = pickle.load(open("../models/my_vectorizer.model", "rb"))
    #print('vectorizing ecc notes')
    #ecc_notes['ecc_vect'] = vect.transform(ecc_notes['CLINICALNOTETEXT'].values)
    print('finished ecc notes')
    return ecc_notes


def add_cs_notes(samples, years):
    cs_notes = pd.DataFrame()
    path_cs = data_folder + 'chairside/'
    # read in files into df
    for year in years:
        for q in ['Q1','Q2','Q3','Q4']:
            # should assert somewhere file exists
            if year in ['2018']:
                print('loading cs notes for ' + year + ': ' + q)
                cs_notes = cs_notes.append(pd.read_csv(path_cs + 'chair_notes_' + year + q + '.csv'), sort=False)
                print('loaded')
            if year in ['2019']:
                print('loading cs notes for ' + year + ': ' + q)
                if q in ['Q1','Q2']:
                    cs_notes = cs_notes.append(pd.read_csv(path_cs + 'chair_notes_' + year + q + '.csv'), sort=False)
                    print('loaded')
                if q in ['Q3','Q4']:
                    cs_notes = cs_notes.append(pd.read_csv(path_cs + 'chairside_notes_' + q + '_' + year + '.csv'), sort=False)
                    print('loaded')
            if year in ['2020']:
                print('loading cs notes for ' + year + ': ' + q)
                if q in ['Q1']:
                    cs_notes = cs_notes.append(pd.read_csv(path_cs + 'chairside_notes_' + q + '_' + year + '.csv'), sort=False)
                    print('loaded')
                else:
                    print('skipping')
    
    print('processing cs notes')
    cs_notes['MRN'] = pd.to_numeric(cs_notes['MRN'], errors='coerce')
    cs_notes = cs_notes.loc[cs_notes.MRN.notnull()]
    cs_notes['MRN'] = cs_notes['MRN'].astype('int64')
    cs_notes['TIME_ON_DATE'] = pd.to_datetime(cs_notes['TIME_ON_DATE'], format='%m/%d/%Y')
    
    cs_notes = cs_notes.drop_duplicates(subset=['MRN','TIME_ON_DATE'], keep='first')
    
    cs_notes = filter_chairside_notes(cs_notes, samples, date_samples)
    
    cs_notes = join_chairside_notes(cs_notes)
    
    cs_notes = cs_notes.drop_duplicates(subset=['MRN','TIME_ON_DATE'], keep='first')
    
    #vect = pickle.load(open("../models/my_vectorizer_chairside.model", "rb"))
    #print('vectorizing cs notes')
    #cs_notes['cs_vect'] = vect.transform(cs_notes['ALL_NOTES'].values)
    print('finished cs notes')
    return cs_notes
    
    
def add_bp_meds(samples, years):
    # taken from pred041 utils, need to drop duplicates ended at slightly different times (same day)
    
    df_bp = pd.DataFrame()
    
    for year in years:
        if year in ['2018']:
            for q in ['Q1','Q2','Q3','Q4']:
                print('reading BP data from ' + q + ' ' + year)
                df_bp = df_bp.append(pd.read_csv(data_folder + 'meds/BP_MEDS_RX_' + year + q + '.csv'))
                print('loaded')
        if year in ['2019','2020']:
            print('reading BP data from ' + year)
            df_bp = df_bp.append(pd.read_csv(data_folder + 'meds/BP_MEDS_RX' + year + '.csv'))
            print('loaded')
    
    print('processing bp meds')
    df_bp['DERIVED_START_DATE'] = pd.to_datetime(df_bp['DERIVED_START_DATE'], format='%d%b%Y:%H:%M:%S', errors='coerce')
    df_bp['STOP_DATE'] = pd.to_datetime(df_bp['STOP_DATE'], format='%d%b%Y:%H:%M:%S', errors='coerce')
    
    df_bp = process_bp_med(samples, cols_samples, date_samples, df_bp)
    print('finished bp meds')
    return df_bp
    
    
def add_data(samples, years, chairside=False, labs=False, absences=False, ecc_notes=False, cs_notes=False, bp_meds=False):
    
    data = samples.copy()
    if chairside:
        data = data.merge(add_chairside(samples, years), on=cols_samples, how='left')
        assert len(data) == len(samples), 'samples changed during chairside step'
        
    if labs:
        data = data.merge(add_labs(samples, years), on=cols_samples, how='left')
        assert len(data) == len(samples), 'samples changed during labs step'
        
    if absences:
        data = data.merge(add_absences(samples, years), on=cols_samples, how='left')
        assert len(data) == len(samples), 'samples changed during absences step'
    
    if ecc_notes:
        data = data.merge(add_ecc_notes(samples, years), on=cols_samples, how='left')
        data = data.drop_duplicates(subset=['MRN','QUERY_RUN_DATE'])
        assert len(data) == len(samples), 'samples changed during ecc notes step'
    
    # save progress
    #pickle
    #print('saving progress: ' + data_folder + 'temp_processed_data_' + today + '.pickle')
    #with open(data_folder + 'temp_processed_data_' + today + '.pickle', 'wb') as f:
    #    pickle.dump(data, f)
    
    if cs_notes:
        data = data.merge(add_cs_notes(samples, years), on=cols_samples, how='left')
        data = data.drop_duplicates(subset=['MRN','QUERY_RUN_DATE'])
        assert len(data) == len(samples), 'samples changed during cs notes step'
        
    if bp_meds:
        data = data.merge(add_bp_meds(samples, years), on=cols_samples, how='left')
        assert len(data) == len(samples), 'samples changed during bp meds step'
    
    print('data added!')
    return data



# model training

def calc_specificity(y_actual, y_pred, thresh):
    return sum((y_pred < thresh) & (y_actual == 0)) /sum(y_actual ==0)


def calc_prevalence(y_actual):
    return sum((y_actual == 1)) /len(y_actual)


def train_notes_model(X_train, y_train, X_valid, y_valid, vect):
    X_train = vect.transform(X_train)
    X_valid = vect.transform(X_valid)
    
    # logistic regression

    import matplotlib.pyplot as plt

    clf=LogisticRegression(C = 1.0, penalty = 'l2', random_state = 42)
    clf.fit(X_train, y_train)
    
    #pickle.dump(clf, open("../models/ecc_bow.model", "wb"))
    
    y_train_preds = clf.predict_proba(X_train)[:,1]
    y_valid_preds = clf.predict_proba(X_valid)[:,1]
    
    fpr_train, tpr_train, thresholds_train = roc_curve(y_train, y_train_preds)
    fpr_valid, tpr_valid, thresholds_valid = roc_curve(y_valid, y_valid_preds)


    thresh = 0.5

    auc_train = roc_auc_score(y_train, y_train_preds)
    auc_valid = roc_auc_score(y_valid, y_valid_preds)

    print('Train prevalence:%.3f'%calc_prevalence(y_train))
    print('Valid prevalence:%.3f'%calc_prevalence(y_valid))

    print('Train AUC:%.3f'%auc_train)
    print('Valid AUC:%.3f'%auc_valid)

    print('Train accuracy:%.3f'%accuracy_score(y_train, y_train_preds >= thresh))
    print('Valid accuracy:%.3f'%accuracy_score(y_valid, y_valid_preds >= thresh))

    print('Train recall:%.3f'%recall_score(y_train, y_train_preds>= thresh))
    print('Valid recall:%.3f'%recall_score(y_valid, y_valid_preds>= thresh))

    print('Train precision:%.3f'%precision_score(y_train, y_train_preds>= thresh))
    print('Valid precision:%.3f'%precision_score(y_valid, y_valid_preds>= thresh))

    print('Train specificity:%.3f'%calc_specificity(y_train, y_train_preds, thresh))
    print('Valid specificity:%.3f'%calc_specificity(y_valid, y_valid_preds, thresh))

    plt.plot(fpr_train, tpr_train,'r-', label = 'Train AUC: %.2f'%auc_train)
    plt.plot(fpr_valid, tpr_valid,'b-',label = 'Valid AUC: %.2f'%auc_valid)
    plt.plot([0,1],[0,1],'-k')
    plt.xlabel('False Positive Rate',fontsize = 15)
    plt.ylabel('True Positive Rate',fontsize = 15)
    plt.legend(fontsize = 15)
    plt.xticks(fontsize = 15)
    plt.yticks(fontsize = 15)
    plt.show()
    
    feature_importances = pd.DataFrame(clf.coef_[0], index=vect.get_feature_names(),
                                       columns=['importance']).sort_values('importance', ascending=False)
    
    num = 50
    ylocs = np.arange(num)
    
    # get the feature importance for top num and sort in reverse order
    values_to_plot = feature_importances.iloc[:num].values.ravel()[::-1]
    feature_labels = list(feature_importances.iloc[:num].index)[::-1]

    plt.figure(num=None, figsize=(8, 15), dpi=80, facecolor='w', edgecolor='k');
    plt.barh(ylocs, values_to_plot, align = 'center')
    plt.ylabel('Features')
    plt.xlabel('Importance Score')
    plt.title('Positive Feature Importance Score - Logistic Regression')
    plt.yticks(ylocs, feature_labels)
    plt.show()
    
    # negative feature importance score plot
    values_to_plot = feature_importances.iloc[-num:].values.ravel()
    feature_labels = list(feature_importances.iloc[-num:].index)

    plt.figure(num=None, figsize=(8, 15), dpi=80, facecolor='w', edgecolor='k');
    plt.barh(ylocs, values_to_plot, align = 'center')
    plt.ylabel('Features')
    plt.xlabel('Importance Score')
    plt.title('Negative Feature Importance Score - Logistic Regression')
    plt.yticks(ylocs, feature_labels)
    plt.show()
    
    return clf


def clean_columns_dict(col2use):
    # cleans the columns to drop bad characters
    
    col2use_clean = col2use.copy()

    char_replace = ' #</.=-():>[]>'
    for cr in char_replace:
        col2use_clean = [c.replace(cr,'_') for c in col2use_clean]

    return dict(zip(col2use, col2use_clean))


def get_feats_ecc_notes(df_samples, cols_samples, date_samples,df_data):

    data_date = 'ENTEREDDT'
    window_days = [7,30]
   
    cols_data = ['pred_ecc_note']

    for c in ['MRN','ENTEREDDT']:
        assert c in df_data.columns, c + ' not in df_data'
    
    for c in cols_samples:
        assert c in df_samples, c + ' not in df_samples'
    
    common_utils.check_schema(df_data,cols_data + [data_date])  
    
    # groupby mrn and date
    df_data_group = df_data[cols_data +[data_date,'MRN']].groupby(['MRN',data_date]).mean()
    df_data_group = df_data_group.reset_index()
    
    # preprocess
    df_data_samples = common_utils.preprocess_last_history(['MRN'],df_samples, cols_samples, date_samples, \
                           df_data_group,cols_data, data_date, \
                           window_days, by_col = 1)
    assert len(df_data_samples) == len(df_samples),'number of samples changed'
    
    # ecc
    fcn_cds = ['MEAN','MAX','MIN']#,'STD']
    cols_diff = ['MEAN','MAX','MIN']
    days = [str(w) for w in window_days]   
    cols_hist = [c+'_' +n + '_' + f for c in cols_data for n in days for f in fcn_cds ]
    cols_hist_delta = [col + '_' + day + '_'+m + '_DIFF' for col in cols_data for day in days for m in cols_diff]
    cols_all = cols_data+ cols_hist+ cols_hist_delta
    
    
    return df_data_samples[cols_samples + cols_all]


def get_feats_chairside_notes(df_samples, cols_samples, date_samples,df_data):

    data_date = 'TIME_ON_DATE'
    window_days = [7,30]
   
    cols_data = ['pred_chairside_note']

    for c in ['MRN','TIME_ON_DATE']:
        assert c in df_data.columns, c + ' not in df_data'
    
    for c in cols_samples:
        assert c in df_samples, c + ' not in df_samples'
    
    common_utils.check_schema(df_data,cols_data + [data_date])  
    
    # groupby mrn and date
    df_data_group = df_data[cols_data +[data_date,'MRN']].groupby(['MRN',data_date]).mean()
    df_data_group = df_data_group.reset_index()
    
    # preprocess
    df_data_samples = common_utils.preprocess_last_history(['MRN'],df_samples, cols_samples, date_samples, \
                           df_data_group,cols_data, data_date, \
                           window_days, by_col = 1)
    assert len(df_data_samples) == len(df_samples),'number of samples changed'
    
    # ecc
    fcn_cds = ['MEAN','MAX','MIN']#,'STD']
    cols_diff = ['MEAN','MAX','MIN']
    days = [str(w) for w in window_days]   
    cols_hist = [c+'_' +n + '_' + f for c in cols_data for n in days for f in fcn_cds ]
    cols_hist_delta = [col + '_' + day + '_'+m + '_DIFF' for col in cols_data for day in days for m in cols_diff]
    cols_all = cols_data+ cols_hist+ cols_hist_delta
    
    return df_data_samples[cols_samples + cols_all]


class pred_model(object):
    # This is the model for predicting with the treatment notes
    def __init__(self):
        pass
    
    
    def train(self, df_train, y_train, df_valid, y_valid, col2use, params, num_trees,
              file = 'model'
              ):
        self.file = file
        
        X_train = df_train[col2use].as_matrix()
        dt = xgb.DMatrix(X_train,label=y_train, feature_names = col2use)
        
        X_valid = df_valid[col2use].as_matrix()
        dv = xgb.DMatrix(X_valid,label=y_valid, feature_names = col2use)

        
        xgboost_model = xgb.train(params, dt, num_trees, [(dt, "train"),(dv, "valid")], verbose_eval=25,
                                  early_stopping_rounds=params['early_stopping_rounds'])

        print('saving '+file)
        pickle.dump(xgboost_model, open(file, "wb"))
        print('done')
    
        self.model = xgboost_model       
        
    
    def predict(self, df, model_file, pred_contribs=False):
        # predict probability or prediction contributions for the model file
        self.model = pickle.load(open(model_file, "rb"))
        col2use = self.model.feature_names
        X = df[col2use].as_matrix()
        data = xgb.DMatrix(X, feature_names = col2use)
        
        return self.model.predict(data, pred_contribs=pred_contribs)
    

def add_predictions_reasons(df_all, pred_name, model_file, var2eng_file, var2eng_yaml, num_reasons):
    # creates predictions and adds the reasons

    # prediction
    my_model = pred_model()
    df_all[pred_name] = my_model.predict(df_all, model_file)
    
    # reasons
    df_var2eng = common_utils.load_df_file(var2eng_file, var2eng_yaml)
    var_include = list(df_var2eng.loc[df_var2eng.Include_in_reasons == 1, 'Variable'].values)
    var_include = [v for v in var_include if v in my_model.model.feature_names]
    df_all = add_reasons(df_all, var_include, model_file, num_reasons)  
    
    return df_all


def add_reasons(df, col2include, model_file, num_reasons):
    # adds the num_reasons to the dataframe df using model model_file and only the cols in col2include
    
    df_contribs = get_pred_contribs(df, model_file)
    df = convert_contribs_to_reasons(df, df_contribs, col2include, num_reasons = 20)
    
    # add the reasons
    df = pd.concat([df,df.apply(get_reasons,axis = 1)],axis = 1)

    return df


def get_pred_contribs(df, model_file):
    # gets the feature contribs from XGB and stores in a dataframe
    
    my_model=  pred_model()
    preds_z_contribs = my_model.predict(df, model_file,pred_contribs = True)

    # extract the column names
    col2use = my_model.model.feature_names

    # add the reasons 
    df_contribs = pd.DataFrame(preds_z_contribs[:,:-1], columns = col2use , index = df.index)
 
    return df_contribs


def convert_contribs_to_reasons(df, df_contribs, col2include, num_reasons):
    # takes the dataframe of contributions and adds the top num_reasons in an array
    # stores this array in big df
    
    # check necessary columns are in df_active_pts
    for c in col2include:
        assert c in df_contribs.columns, c +' not in df_contribs'

    # check length of the two dfs match
    assert len(df) == len(df_contribs), 'df lengths are different'
    
    # check index are equal
    pd.testing.assert_index_equal(df.index, df_contribs.index)
    
    df['reasons'] = df_contribs[col2include].apply(lambda s: s.nlargest(num_reasons).index.tolist(),axis=1)
    return df


def get_reasons(s):
    # converts the reasons array to add Reason and Reason Value for each reason
    
    # check necessary index in series
    for c in ['reasons']:
        assert c in s, c +' not in series'

    all_reasons = s['reasons']
    num_reasons = len(all_reasons)
    reasons = list(np.array(all_reasons))
    reasons_vals = list(s[all_reasons].values)
    return pd.Series(reasons+reasons_vals, index=['Reason'+str(i) for i in range(1,num_reasons+1)]+['Reason'+str(i)+'_value' for i in range(1,num_reasons+1)])
    
    return s


def build_deliverable(df, n, model_file, pred_col, is_development, model_name, model_version):
    # This creates the deliverable
    
    if len(df) > 0:
    
        # restrict to top n
        #pred_col = 'pred'
        df = df.sort_values(pred_col,ascending = False).iloc[:n].reset_index(drop = True)

        # model file
        my_model = pred_model()
        preds_z_contribs = my_model.predict(df, model_file,pred_contribs = True)

        # extract the column names
        col2use = my_model.model.feature_names

        num_reasons = 20
        
        # add the reasons above threshold 0.05
        df_preds = pd.DataFrame(preds_z_contribs[:,:-1], columns = col2use , index = df.index)
        df['reasons'] = df_preds.apply(lambda s: s.nlargest(num_reasons).index.tolist(),axis=1)
        df['reasons_pct'] = df_preds.apply(lambda s: s.nlargest(num_reasons).tolist(),axis=1)

        neg_sum = ((preds_z_contribs[:,:-1] <= 0)*preds_z_contribs[:,:-1]).sum(axis = 1)
        bias = preds_z_contribs[:,-1]
        df['thresh'] = -np.log(1/(df[pred_col]-0.05) -1)    - neg_sum - bias
        df = pd.concat([df,df.apply(get_reasons,args = ('all',),axis = 1),
                        df.apply(get_reasons_pct,args = ('all',),axis = 1)],axis = 1)
    df_deliverable = make_deliverable_columns(df, is_development, model_name, model_version)
     
    return df_deliverable

def make_deliverable_columns(df, is_development, model_name, model_version):
    # This funcion builds the columns for the deliverable
    
    # columns to keep
    cols_deliverable = ['MRN','QUERY_RUN_DATE','pred']+\
            ['Reason'+str(i) for i in range(1,21)] + \
            ['Reason'+str(i)+'_value' for i in range(1,21)] +\
            ['MODEL','MODEL_VERSION',
            'MY_FAC_ID','Age','Vintage']

            
    if len(df) > 0:
    
        # Model and version
        df['MODEL'] = model_name #'IHPM'
        df['MODEL_VERSION'] = model_version #3.0
        
        # Get the query date and treatment date
        df['QUERY_RUN_DATE'] = pd.to_datetime(df['QUERY_RUN_DATE']).dt.normalize()
        assert type(df['QUERY_RUN_DATE'][0])== pd.Timestamp, 'QUERY_RUN_DATE not a datetime'
        
        return df[cols_deliverable]
    else:
        return pd.DataFrame(columns = cols_deliverable)


def write_csv_deliverable(df_all, full_file_name, model_version, pred_col):
    # writes the csv with teh following columns
    cols_deliverable = ['MRN','QUERY_RUN_DATE',pred_col,'VERSION_NUM'] + ['Reason'+str(i) for i in range(1,21)] + \
            ['Reason'+str(i)+'_value' for i in range(1,21)]
    
    df_all['VERSION_NUM'] = model_version #1.02
    
    # check columns are in df
    for c in cols_deliverable:
        assert c in df_all, c + ' not in df'
    
    # create upper case that matches database schema
    keys = ['Reason'+str(i) for i in range(1,21)] + \
                ['Reason'+str(i)+'_value' for i in range(1,21)]
    values = ['REASON_VAR'+str(i) for i in range(1,21)] + \
                ['REASON_VALUE'+str(i) for i in range(1,21)]
    upper_dict = dict(zip(keys, values)) 
    upper_dict.update({'QUERY_RUN_DATE':'PREDICTION_DATE',
                      pred_col:'PREDICTION_SCORE'})    
    
    # check the specified file path exists
    my_path,filename = path_split(abspath(full_file_name))
    assert isdir(my_path), 'file name path does not exist'
    
    df_all[cols_deliverable].rename(columns = upper_dict).to_csv(full_file_name, index = False)
    
    return df_all[cols_deliverable].rename(columns = upper_dict)