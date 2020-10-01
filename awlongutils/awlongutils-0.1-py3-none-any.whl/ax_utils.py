# python code for processing a lab table
from .common_utils import (load_df_file, check_schema, load_df_with_dates, make_dummies,merge_keep_last)
import pandas as pd
import time
import numpy as np
from pandas.api.types import CategoricalDtype


def load_ax(csv_filename, yaml_filename, ax_format,encoding):
    # load the treatment table and convert dates
    
    dates = ['AX_CRT_DT','AX_ENTER_DT','COLLECTED_DT','CREATE_DT']
    date_formats = [ax_format]*len(dates)
    df = load_df_with_dates(csv_filename, yaml_filename, dates, date_formats, encoding)
    #'%d%b%Y:%H:%M:%S'   '%Y-%m-%d %H:%M:%S'    
  
    return df

def convert_yes_no(df,c):
    # this function converts yes/no/unknown to 1,0,-1

    check_schema(df,[c])
    
    df.loc[~df[c].isin(['Yes','No']),c] = 'UNK'        
    df[c] = df[c].fillna('UNK')
    df[c] = df[c].replace({'Yes':1,'No':0,'UNK':-1})
    return df

def convert_all_yes_no(df,cols):
    # converts all yes/no/unkonwn in columns
    # check required columns are there
    check_schema(df,cols)

    for c in cols:
        df = convert_yes_no(df, c)

    return df

def split_checkbox(df,col,my_cats):
    # splits the checkboxes
    
    # check the col is in df
    check_schema(df,[col])
    
    # split on the code \x1e
    df[col] = df[col].fillna('UNK').str.split('\x1e')
    # create categories
    cats = CategoricalDtype(categories=my_cats,  ordered=True) 
    # split and make dummies
    df_checkbox = pd.get_dummies(df[col].apply(pd.Series).stack().astype(cats), drop_first = True, prefix= col).sum(level=0)
    
    # change from categorical index to regular columns
    df_checkbox.columns = [col+ '_'+m for m in my_cats[1:]]
    return df_checkbox


def clean_CRN_HT(df):
    
    cols = ['CRN_HTInterest','CRN_HTOnHT','CRN_HTReferred']
    # check required columns are there
    check_schema(df,cols)
    df = convert_all_yes_no(df,cols)
    return df
    

    
def clean_CSW(df):
    # converts Yes/No columns into 1,0,-1 (no value)
    
    cols = ['CSW_CurrLiveBarr', 'CSW_AppHous','CSW_MemSp','CSW_SpiritComm','CSW_NeedAddlSup','CSW_PHQ2Complete','CSW_PHQ3Higher',
                  'CSW_CESD10Comp','CSW_CESD1010High','CSW_PhyNotify','CSW_WrInfoNoEng',
                  'CSW_DiffUnder','CSW_CognStatusCh','CSW_PresPln','CSW_ImmCov','CSW_PtReEducGoal','CSW_RelTran','CSW_VocRehab']
    
    # convert all yes/no
    check_schema(df,cols)
    df = convert_all_yes_no(df,cols)
    
    return df



def add_CSW_cats(df):
    # create one hot encoding for each column specified below and combine them
    
    # check required columns are there
    check_schema(df,['CSW_ActLevel','CSW_DlyLifeDec','CSW_LevAsst','CSW_PCMentalHlth','CSW_PtAffordPrem','CSW_PtAlcoholUse',
'CSW_PtCurrEmpl','CSW_PtEducLevel','CSW_PtFmInteract','CSW_PtInsStatus','CSW_PtRelStatus','CSW_PtSleepMeds','CSW_SupportGroup',
        'FA_PrimLang','FA_SecLang'])

    df_ActLevel = make_dummies(df,'CSW_ActLevel',['UNK','Better than 3 months ago', 'The same as 3 months ago',
       'Less than 3 months ago'])
    df_DlyLifeDec = make_dummies(df,'CSW_DlyLifeDec',['UNK','Independent',
       'Modified independence-some difficulty in new situations',
       'Severely impaired-never/rarely makes decisions',
       'Moderately impaired'])
    df_LevAsst = make_dummies(df,'CSW_LevAsst',['UNK','Independent', 'Requires some assistance', 'Requires total care'])
    df_PCMentalHlth = make_dummies(df,'CSW_PCMentalHlth',['UNK','None', 'Current', 'Past'])
    df_PtAffordPrem = make_dummies(df,'CSW_PtAffordPrem',['UNK','No', 'Yes', 'Refer to Financial Coordinator'])
    df_PtAlcoholUse = make_dummies(df,'CSW_PtAlcoholUse',['UNK','No', 'Yes', 'Declined to answer'])
    df_PtCurrEmpl = make_dummies(df,'CSW_PtCurrEmpl',['UNK','Disabled on SSDI', 'Retired', 'Unemployed',
       'Employed - part time', 'Employed - full time',
       'Employed but on medical leave', 'Homemaker', 'Veteran',
       'Military'])
    df_PtEducLevel = make_dummies(df,'CSW_PtEducLevel',['UNK','Graduated high school', 'Graduated from 2 or 4 year college',
       'Some college', 'Graduate school', 'GED',
       'More than 8 years but less than 12', '8 or less years of school',
       'Vocational/technical school', 'Current student'])
    df_PtFmInteract = make_dummies(df,'CSW_PtFmInteract',['UNK','Daily', 'Weekly', 'Less frequently than monthly', 'Monthly'])
    df_PtInsStatus = make_dummies(df,'CSW_PtInsStatus',['UNK','Full coverage', 'Partial coverage', 'No coverage, self pay'])
    df_PtRelStatus = make_dummies(df,'CSW_PtRelStatus',['UNK','Single', 'Married', 'Domestic partner', 'Divorced', 'Separated',
       'Widowed'])
    df_PtSleepMeds = make_dummies(df,'CSW_PtSleepMeds',['UNK','No', 'Currently', 'Yes'])
    df_SupportGroup = make_dummies(df,'CSW_SupportGroup',['UNK','No', 'Currently', 'Yes'])
    df_PrimLang = make_dummies(df,'FA_PrimLang',['UNK','English', 'Spanish', 'Other', 'Tagalog', 'Vietnamese', 'French',
       'Russian'])
    df_SecLang = make_dummies(df,'FA_SecLang',['UNK','French', 'Not applicable', 'English', 'Spanish', 'Other',
       'Vietnamese', 'Tagalog', 'Russian'])  
    
   
    df_cats = pd.concat([df_ActLevel, df_DlyLifeDec, df_LevAsst,df_PCMentalHlth,  df_PtAffordPrem, df_PtAlcoholUse, df_PtCurrEmpl,\
                   df_PtEducLevel, df_PtFmInteract, df_PtInsStatus, df_PtRelStatus, df_PtSleepMeds, df_SupportGroup, df_PrimLang,\
                   df_SecLang],axis = 1)
    cols_cats = list(df_cats.columns)
    # add on the columns
    df = pd.concat([df,df_cats],axis = 1)
    
    # fill missing columns
    df[cols_cats] = df[cols_cats].fillna(0)

    
    return df

   
def split_checkboxes_CSW(df):
    
    # check_schema
    check_schema(df,['CSW_AsstReq', 'CSW_AsstPat','CSW_PtCopeStress', 'CSW_PtConcerns'])
    
    CSW_AsstReq_split = split_checkbox(df,'CSW_AsstReq',['UNK','Meal preparation' ,'Laundry' ,'Housekeeping', 'Bathing' , 'Dressing', 'Toileting', 'Shopping', 'Medication management', 'Managing medical appointments', 'Managing finances', 'Feeding'])
    CSW_AsstPat= split_checkbox(df,'CSW_AsstPat',['UNK','Family', 'Other, specify', 'Home health services' ,'Caregiver'])
    CSW_PtCopeStress=split_checkbox(df,'CSW_PtCopeStress',['Keeps to him/herself', 'Talk to family', 'Prayer or meditation' ,'Other',
 'Talk to friends', 'Resources on the internet' ,'Talk with a professional'])
    CSW_PtConcerns= split_checkbox(df,'CSW_PtConcerns',['No concerns', 'Other' ,'Adjustment to dialysis or relationship issues',
 'Income' ,'Access to food', 'Housing/mortgage/rent' ,'Access to medication', 'Utilities', 'Legal'])
    
    df_checkboxes = pd.concat([CSW_AsstReq_split, CSW_AsstPat, CSW_PtCopeStress, CSW_PtConcerns],axis = 1)
    
    cols_checkboxes = list(df_checkboxes.columns)
    # add on the columns
    df = pd.concat([df,df_checkboxes],axis = 1)
    # fill missing columns
    for c in cols_checkboxes:
        df[c] = df[c].fillna(0)
    
    return df

def add_feats_CSW(df):
    
    df = clean_CSW(df)
    df = add_CSW_cats(df)
    df = split_checkboxes_CSW(df)
    
    return df


def process_CSW(df_samples, df_data, cols_samples, date_samples):
    # This function processes the patient info
        
    # merge data on samples
    df_data = df_data.drop_duplicates()
    date_data= 'AX_ENTER_DT'
    
    df_data = df_data.sort_values(['MRN','AX_ENTER_DT','COLLECTED_DT'], ascending = False)
    df_data = df_data.drop_duplicates(subset = ['MRN','AX_ENTER_DT'], keep = 'first')
    
    #df_CSW_samples = merge_keep_last(df_samples[cols_samples], df_data, \
    #                                 date_samples, date_data, ['MRN'],cols_samples, use_equal = 1)
    
    df_samples = df_samples.sort_values(date_samples).reset_index(drop = True)
    df_data = df_data.sort_values(date_data).reset_index(drop = True)

    df_CSW_samples = pd.merge_asof(df_samples, 
                      df_data,
                 left_on = date_samples,
                 right_on = date_data,
                 by = 'MRN',
                 direction  = 'backward')
    
    df_CSW_samples = df_CSW_samples.sort_values(cols_samples).reset_index(drop = True)
    
    df_CSW_samples = add_feats_CSW(df_CSW_samples)
    
    df_CSW_samples['days_since_CSW'] = (df_CSW_samples[date_samples] - df_CSW_samples['AX_ENTER_DT']).dt.days

    
    return df_CSW_samples

    

def clean_CRD(df):
    # converts Yes/No columns into 1,0,-1 (no value)
    
    cols = ['FA_Alcohol','FA_DinesSelf','FA_DinesSpouse','FA_FoodAllergy','FA_FoodIntol','FA_GiSymptomsNH',
          'FA_MealsSelf','FA_MealsSpouse','FA_OralProb','FA_PicaYN','FA_ReligDietRstr','FA_RxMedDepend',
          'FA_SelfRestrict','FA_ShopSelf','FA_ShopSpouse','FA_Substances','FA_UrineOutput','FA_Edentulous',
          'FA_HxDiarrhea','FA_HxNausea','FA_DinesFamMem','FA_MealsFamMemb','FA_ShopFamMemb','FA_HxConstip',
          'FA_HxSatiety','FA_ToothDecay','FA_HxTasteAlt','FA_MealsOther','FA_DiffChew','FA_HxHtburn',
          'FA_FoodAssist','FA_HxVomit','RDSN_SympPsych','FA_DinesInstitut','FA_MealsInstitut','FA_ShopOther',
          'FA_HxAbdPain','RDSN_AbdPainFreq','RDSN_SympMed','FA_DinesOther','FA_MissingTeeth','FA_IllFitDent',
          'FA_MealsMW','FA_HxDysphagia','FA_DinesCongregt','FA_OralAbscess','FA_HxHiccups','FA_HxGastropares',
          'FA_DiabSelfMgmt','FA_DiabBldGluMon','FA_DiabDental','FA_DiabFootCheck','FA_DiabExercise']
    
    # convert all yes/no
    check_schema(df,cols + ['FA_OverallNutr'])
    df = convert_all_yes_no(df,cols)
    
    # convert nutrition to number 
    df['FA_OverallNutr'] = pd.to_numeric(df['FA_OverallNutr'],errors = 'coerce')
    df['FA_OverallNutr'] = df['FA_OverallNutr'].fillna(-1)
    
    return df

def add_CRD_cats(df):
    # create one hot encoding for each column specified below and combine them
    
    # check required columns are there
    check_schema(df,['FA_AdherDietInst','FA_AdhereDietMed','FA_AppetiteIntak','FA_EstCalIntake','FA_EstProtIntake','FA_GISymptoms',
            'FA_MealsOutWk','FA_ReceptDietEdu','FA_UnderstndDiet','FA_AvgIDWG','FA_DiabMeds','TC_Use'])

    FA_AdherDietInst = make_dummies(df,'FA_AdherDietInst',['UNK','Fair' ,'Good' ,'Poor'])
    FA_AdhereDietMed = make_dummies(df,'FA_AdhereDietMed',['UNK','Fair', 'Poor', 'Good'])
    FA_AppetiteIntak = make_dummies(df,'FA_AppetiteIntak',['UNK','Decreased/intake poor; >2 weeks duration',
 'Good/change is slight and/or of short duration', 'Good/no change',
 'Poor/intake poor and decreasing, unable to eat, starvation'])
    FA_EstCalIntake = make_dummies(df,'FA_EstCalIntake',['UNK','Adequate', 'Inadequate'])
    FA_EstProtIntake = make_dummies(df,'FA_EstProtIntake',['UNK','Inadequate', 'Adequate'])
    FA_GISymptoms = make_dummies(df,'FA_GISymptoms',['UNK','Few symptoms, intermittent', 
 'Some symptoms; >2 weeks duration',
 'Some or all symptoms frequent or daily; >2 weeks'])
    FA_MealsOutWk = make_dummies(df,'FA_MealsOutWk',['UNK','Rarely' ,'Occasionally', 'Often' ])
    FA_ReceptDietEdu = make_dummies(df,'FA_ReceptDietEdu',['UNK','Fair' ,'Good', 'Poor'])
    FA_UnderstndDiet = make_dummies(df,'FA_UnderstndDiet',['UNK','Good', 'Fair' , 'Poor' ])
    FA_AvgIDWG = make_dummies(df,'FA_AvgIDWG',['UNK','In target' ,'Above target', 'Below target'])
    FA_DiabMeds = make_dummies(df,'FA_DiabMeds',['UNK','Uses as prescribed' ,'Not applicable', 'Does not use as prescribed'])
    TC_Use = make_dummies(df,'TC_Use',['UNK','Never used', 'Former user' , 'Current user']) 
    
   
    df_cats = pd.concat([FA_AdherDietInst, FA_AdhereDietMed, FA_AppetiteIntak,FA_EstCalIntake,  FA_EstProtIntake, FA_GISymptoms, FA_MealsOutWk,FA_ReceptDietEdu, FA_UnderstndDiet, FA_AvgIDWG, FA_DiabMeds, TC_Use],axis = 1)
    cols_cats = list(df_cats.columns)
    # add on the columns
    df = pd.concat([df,df_cats],axis = 1)
    
    # fill missing columns
    df[cols_cats] = df[cols_cats].fillna(0)

    
    return df
def split_checkboxes_CRD(df):
    
    # check_schema
    check_schema(df,['FA_DiabDiet'])
    
    df_checkboxes = split_checkbox(df,'FA_DiabDiet',['UNK','CHO controlled','No conc sweets','Other'])
        
    cols_checkboxes = list(df_checkboxes.columns)
    # add on the columns
    df = pd.concat([df,df_checkboxes],axis = 1)
    # fill missing columns
    for c in cols_checkboxes:
        df[c] = df[c].fillna(0)
    
    return df


def add_feats_CRD(df):
    
    df = clean_CRD(df)
    df = add_CRD_cats(df)
    df = split_checkboxes_CRD(df)
    
    return df
def process_CRD(df_samples, df_data, cols_samples, date_samples):
    # This function processes the patient info
        
    # merge data on samples
    df_data = df_data.drop_duplicates()
    date_data= 'AX_ENTER_DT'
    
    df_data = df_data.sort_values(['MRN','AX_ENTER_DT','COLLECTED_DT'], ascending = False)
    df_data = df_data.drop_duplicates(subset = ['MRN','AX_ENTER_DT'], keep = 'first')
    
    #df_CRD_samples = merge_keep_last(df_samples[cols_samples], df_data, \
    #                                 date_samples, date_data, ['MRN'],cols_samples, use_equal = 1)
    df_samples = df_samples.sort_values(date_samples).reset_index(drop = True)
    df_data = df_data.sort_values(date_data).reset_index(drop = True)

    df_CRD_samples = pd.merge_asof(df_samples, 
                      df_data,
                 left_on = date_samples,
                 right_on = date_data,
                 by = 'MRN',
                 direction  = 'backward')
    
    df_CRD_samples = df_CRD_samples.sort_values(cols_samples).reset_index(drop = True)
    
    df_CRD_samples = add_feats_CRD(df_CRD_samples)
    
    # drop unnecessary columns & add days since
    df_CRD_samples['days_since_CRD'] = (df_CRD_samples[date_samples] - df_CRD_samples['AX_ENTER_DT']).dt.days

    return df_CRD_samples

def clean_CRN(df):
    # converts Yes/No columns into 1,0,-1 (no value)
    
    cols_yn = ['CRN_AnemiaIrdose', 'CRN_Anemiacomor', 'CRN_BPVolMon', 'CRN_HBsAgUnknown', 'CRN_HTReferred', 'CRN_LTResultsRev', 'CRN_MMMedsReview', 'CRN_PrimaryCP', 'CRN_RespTobacco', 'PD_Status4', 'CRN_AllergiesRev', 'CRN_AnemiaGoal', 'CRN_BPAdvSymp', 'CRN_ResiRenalFun', 'CRN_SkinFtCkAsmt', 'FA_AmputPros', 'FA_DiabBldGluMon', 'FA_DiabDental', 'PD_AccsID5', 'CRN_AnemiaIrind', 'CRN_PresBFR', 'CRN_RespSputumDR', 'CRN_VAInterventn', 'CRN_CardioMDnot', 'CRN_MMLabsReview', 'CRN_VAProblem2', 'PD_Type4', 'CRN_DDGoal', 'CRN_GastNotifyMD', 'CRN_GeniNoUrine', 'CRN_InfTympanic', 'CRN_PresAdequate', 'CRN_RespSecSmoke', 'CRN_RespSputumPU', 'CRN_VAProblem1', 'CRN_VAProblem3', 'CRN_AnemiaHypo', 'CRN_BPStable', 'CRN_CMCMusclecr', 'CRN_TransInt', 'FA_AmpHealed', 'PD_AccsID4', 'CRN_BPErratic', 'CRN_HTOnHT', 'CRN_TransList', 'CRN_UpToDate', 'CRN_PresAdheres', 'CRN_RespSputumNA', 'CRN_TransRef', 'FA_Type5', 'PD_Type5', 'CRN_DDPresRev', 'CRN_Endo', 'FA_SkinIntact', 'PD_ExitSite4', 'PD_Status3', 'CRN_AnemiaBldLss', 'CRN_AnemiaESA', 'CRN_AnemiaReact', 'CRN_HTInterest', 'CRN_InfOral', 'CRN_PDProblem1', 'CRN_Rieviewed', 'FA_DiabExercise', 'FA_Status5', 'PD_ExitSite3', 'CRN_AnemiaIrPr', 'CRN_BPVAchWt', 'CRN_HBcUnknown', 'CRN_MMGoal', 'PD_Type3', 'CRN_CardFacEdema', 'CRN_InfAxillary', 'CRN_InflUnknown', 'CRN_LTNewDialys', 'CRN_MedsRev', 'CRN_RespOxyNA', 'CRN_TBUnknown', 'CRN_AnemiaPrTra', 'CRN_PDProblem2', 'CRN_PheuUnknown', 'CRN_TransPending', 'CRN_HepBUnknown', 'CRN_InfKnown', 'CRN_RecTrtOpt', 'CRN_RespSputumBL', 'CRN_OtherPlan', 'PD_ExitSite5', 'VA_AccsID5', 'CRN_AnemiaRHosp', 'CRN_CardSacEdema', 'CRN_HBsAbUnknown', 'CRN_PDProblem3', 'FA_DiabFootCheck', 'FA_DiabSelfMgmt', 'FA_Site5', 'PD_AccsID3', 'PD_Status5']
    
    cols_num = ['CRN_AmbMultiMeds', 'CRN_AmbNeuroProb', 'CRN_HBsAb', 'FA_DiabExTimes', 'FA_Hand', 'PA_ChestInt', 'PA_PDCathInt', 'AR_HospDchgDate', 'FA_ArmShoulder', 'FRD24_DateChonic', 'PA_HeadacheInt', 'CRN_AmbConfused', 'CRN_AmbUnsteady', 'CRN_CardioAsRRat', 'FA_ArmAboveElbow', 'FA_Toes', 'CRN_AmbChgEnv', 'CRN_AmbMultiDiag', 'CRN_HBsAg', 'CRN_Influenza', 'CRN_RespRate', 'FA_DentalExamDt', 'AR_HospAdmDate', 'CRN_AmbPoorEye', 'CRN_CardioAsARat', 'CRN_InterWtGain', 'CRN_WtTrigger', 'PA_LowerInt', 'FA_LegAboveKnee', 'FA_NbFingers', 'FA_LegAtHip', 'FA_PartialFoot', 'PA_ExtInt', 'CRN_InfTemp', 'FA_DiabBldGlRes', 'PA_OtherInt', 'CMD_DlDoseGlOth', 'CRN_Geniurineout', 'PA_VAInt', 'VA_AccsID2', 'CRN_HBc', 'CRN_HepB', 'CRN_VACanArtPr', 'FA_Foot', 'FA_PartialHand', 'PA_MuscleInt', 'PA_UrinInt', 'VA_AccsID4', 'CMD_CalciumGlOth', 'CMD_MinMetGlOth', 'CRN_AmbPrevFall', 'PA_BackInt', 'PA_NeckInt', 'FA_ArmBelowElbow', 'PA_AbdInt', 'VA_AccsID3', 'CRN_AmbAvgScore', 'CRN_AmbDrugsAlc', 'FA_LegBelowKnee', 'PD_AccsID2', 'CRN_AmbPhysDisab', 'CRN_TBSkinTest', 'PA_JointInt', 'PA_NeckJawInt', 'PA_UpperInt', 'VA_AccsID1', 'CRN_Pheumovax', 'CRN_RespOxyInt', 'FA_Fingers', 'FA_NbToes', 'PD_AccsID1']    
    # convert all yes/no
    check_schema(df,cols_yn + cols_num)
    df = convert_all_yes_no(df,cols_yn)
    
    # convert numerical to numbers
    for c in cols_num:    
        df[c] = pd.to_numeric(df[c],errors = 'coerce')
        df[c] = df[c].fillna(-1)
    
    return df

def add_CRN_cats(df):
    # create one hot encoding for each column specified below and combine them
    
    data_cats1 = [['FA_Site3', ['UNK', 'Leg-Right', 'Subclavian-Right', 'Jugular-Right', 'Subclavian-Left', 'Leg-Left', 'Above Elbow-Left', 'Jugular-Left', 'Below Elbow-Left', 'Above Elbow-Right', 'Other-Right', 'Other-Left']], ['FA_Type3', ['UNK', 'Catheter-Tunneled', 'Catheter-Unknown', 'AV Graft-GORE ACUSEAL', 'Catheter-Non-tunneled', 'AV Graft-Standard (PTFE)', 'AV Fistula-Standard']], ['PA_UrDuration', ['UNK', 'A few minutes', 'A few hours', 'A few seconds', '> 24 hours', '> 12 hours']], ['PA_UrinFreq', ['UNK', 'Daily', 'Weekly', 'On-going', 'Hourly', 'Monthly']], ['PA_NeckJawDur', ['UNK', '> 24 hours', 'A few hours', 'A few minutes', 'A few seconds', '> 12 hours']], ['PA_NeckJawFreq', ['UNK', 'On-going', 'Daily', 'Weekly', 'Monthly', 'Hourly']], ['PA_UrinOns', ['UNK', '> one month', 'Within last month', 'Within last 24 hours', 'Within last week']], ['PA_NeckJawOns', ['UNK', '> one month', 'Within last 24 hours', 'Within last week', 'Within last month']], ['PA_VAFreq', ['UNK', 'Hourly', 'Daily', 'On-going', 'Weekly', 'Monthly']], ['PA_VADuration', ['UNK', 'A few hours', '> 24 hours', 'A few minutes', 'A few seconds', '> 12 hours']], ['FA_Status3', ['UNK', 'Active', 'Waiting for Removal', 'Maturing']], ['PA_ChestDuration', ['UNK', '> 24 hours', 'A few minutes', '> 12 hours', 'A few hours', 'A few seconds']], ['PA_ChestFreq', ['UNK', 'On-going', 'Monthly', 'Daily', 'Weekly', 'Hourly']], ['CRN_VAPain2', ['UNK']], ['PA_VAOns', ['UNK', 'Within last week', 'Within last month', '> one month', 'Within last 24 hours']], ['PA_ChestOns', ['UNK', '> one month', 'Within last month', 'Within last week', 'Within last 24 hours']], ['PA_ExcPain', ['UNK', 'Cognitive barrier', 'Language barrier']], ['CRN_VAAVGAne', ['UNK', 'Red', 'Firm and swollen', 'Tender']], ['PA_OthDuration', ['UNK', 'A few minutes', '> 24 hours', 'A few hours', '> 12 hours', 'A few seconds']], ['PA_OtherFreq', ['UNK', 'Daily', 'On-going', 'Weekly', 'Hourly', 'Monthly']], ['PA_NeckFreq', ['UNK', 'Weekly', 'Daily', 'On-going', 'Hourly', 'Monthly']], ['PA_NeckDuration', ['UNK', 'A few minutes', '> 24 hours', '> 12 hours', 'A few hours', 'A few seconds']], ['CRN_PDPain1', ['UNK']], ['PA_MusDuration', ['UNK', 'A few minutes', 'A few hours', 'A few seconds', '> 24 hours', '> 12 hours']], ['PA_MuscleFreq', ['UNK', 'Monthly', 'Weekly', 'On-going', 'Hourly', 'Daily']], ['PA_AbdDuration', ['UNK', 'A few hours', '> 24 hours', 'A few minutes', '> 12 hours', 'A few seconds']], ['PA_AbdFreq', ['UNK', 'On-going', 'Weekly', 'Daily', 'Hourly', 'Monthly']], ['PA_UpDuration', ['UNK', 'A few hours', '> 24 hours', 'A few minutes', '> 12 hours', 'A few seconds']], ['PA_UpperFreq', ['UNK', 'Daily', 'On-going', 'Hourly', 'Weekly', 'Monthly']], ['PA_OtherOns', ['UNK', '> one month', 'Within last 24 hours', 'Within last month', 'Within last week']], ['PA_NeckOns', ['UNK', '> one month', 'Within last week', 'Within last month', 'Within last 24 hours']], ['CRN_VAProb2', ['UNK', 'Sudden onset', 'Chronic', 'Recurrent']], ['PA_MuscleOns', ['UNK', '> one month', 'Within last week', 'Within last month', 'Within last 24 hours']], ['PA_AbdOns', ['UNK', '> one month', 'Within last month', 'Within last 24 hours', 'Within last week']], ['PA_UpperOns', ['UNK', 'Within last month', '> one month', 'Within last 24 hours', 'Within last week']], ['PA_ExtFreq', ['UNK', 'On-going', 'Daily', 'Weekly', 'Hourly', 'Monthly']], ['PA_ExtDuration', ['UNK', 'A few minutes', 'A few hours', '> 24 hours', '> 12 hours', 'A few seconds']], ['CRN_RArmPainscal', ['UNK']], ['CRN_LArmPainscal', ['UNK']], ['PA_ExtOns', ['UNK', '> one month', 'Within last week', 'Within last 24 hours', 'Within last month']], ['CRN_RArmLocation', ['UNK']], ['PA_HeadacheFreq', ['UNK', 'Daily', 'Weekly', 'On-going', 'Monthly', 'Hourly']], ['PA_HeadDuration', ['UNK', 'A few hours', 'A few minutes', '> 12 hours', '> 24 hours', 'A few seconds']], ['CRN_LArmLocation', ['UNK']], ['PA_JointFreq', ['UNK', 'On-going', 'Weekly', 'Daily', 'Monthly', 'Hourly']], ['PA_JointDuration', ['UNK', '> 24 hours', 'A few hours', 'A few minutes', '> 12 hours', 'A few seconds']], ['CRN_PDProb1', ['UNK', 'Sudden onset', 'Recurrent', 'Chronic']], ['PA_HeadacheOns', ['UNK', 'Within last week', '> one month', 'Within last month', 'Within last 24 hours']], ['PA_JointOns', ['UNK', '> one month', 'Within last week', 'Within last 24 hours', 'Within last month']], ['PA_LowerFreq', ['UNK', 'On-going', 'Daily', 'Weekly', 'Monthly', 'Hourly']], ['PA_LowDuration', ['UNK', '> 24 hours', '> 12 hours', 'A few hours', 'A few minutes', 'A few seconds']], ['PA_LowerOns', ['UNK', '> one month', 'Within last month', 'Within last 24 hours', 'Within last week']], ['CRN_LLegLocation', ['UNK']], ['CRN_LLegPainscal', ['UNK']], ['CRN_RLegLocation', ['UNK']], ['CRN_RLegPainscal', ['UNK']], ['PA_BackFreq', ['UNK', 'On-going', 'Daily', 'Weekly', 'Hourly', 'Monthly']], ['PA_BackDuration', ['UNK', '> 24 hours', '> 12 hours', 'A few hours', 'A few minutes', 'A few seconds']], ['CRN_VAAVFAne', ['UNK', 'Firm and swollen', 'Tender', 'Red']], ['PA_BackOns', ['UNK', '> one month', 'Within last 24 hours', 'Within last week', 'Within last month']], ['FA_Site2', ['UNK', 'Jugular-Right', 'Above Elbow-Left', 'Above Elbow-Right', 'Subclavian-Right', 'Leg-Right', 'Subclavian-Left', 'Jugular-Left', 'Leg-Left', 'Other-Right', 'Below Elbow-Right', 'Below Elbow-Left', 'Other-Left', 'Upper arm-Left']], ['CRN_CardioDur', ['UNK']], ['CRN_VAPain1', ['UNK']], ['CRN_GastAlert', ['UNK']], ['FA_Type2', ['UNK', 'Catheter-Tunneled', 'AV Graft-Standard (PTFE)', 'AV Fistula-Standard', 'Catheter-Non-tunneled', 'Catheter-Unknown', 'AV Graft-Unknown', 'AV Graft-HeRO', 'AV Fistula-Unknown', 'AV Graft-GORE ACUSEAL', 'AV Graft-Other', 'AV Graft-Bovine', 'AV Fistula-Transposed', 'AVFistula standard']], ['CRN_Cardioalph', ['UNK']], ['FRD15_PCRFSCR', ['UNK']], ['CRN_CMCPainsc', ['UNK']], ['CRN_BackPainsc', ['UNK']], ['CRN_InfPainsc', ['UNK']], ['CRN_AbdLocation', ['UNK']], ['CRN_CardNkPainsc', ['UNK']], ['CRN_CardioPainsc', ['UNK']], ['CRN_VAProb1', ['UNK', 'Recurrent', 'Sudden onset', 'Chronic']], ['CRN_GeniPainscal', ['UNK']], ['CRN_CardioAsAIrr', ['UNK', 'Bradycardia < 60', 'Tachycardia > 100']], ['CRN_AbdPainscale', ['UNK']], ['CRN_Ambstatus', ['UNK', 'WNL (within normal limits)', 'Amputation', 'Increased weakness', 'Neuropathy', 'Joint pain', 'Prior injury', 'Loss of balance', 'Prior fall', 'Other', 'Pain', 'Surgical wound', 'Dizziness']], ['CRN_CardioAsRIrr', ['UNK', 'Bradycardia < 60', 'Tachycardia > 100']], ['PD_ExitSite1', ['UNK', 'Right Upper Quadrant', 'Left Lower Quadrant', 'Left Upper Quadrant', 'Right Lower Quadrant', 'Pre-sternal']], ['CRN_HeadPainscal', ['UNK']], ['CRN_CMCProbType', ['UNK']], ['CRN_LArmProbType', ['UNK']], ['CRN_RArmProbType', ['UNK']], ['CRN_LLegProbType', ['UNK']], ['CRN_BackProbType', ['UNK']], ['CRN_RLegProbType', ['UNK']], ['CRN_SkinPainscal', ['UNK']], ['CRN_RespPainscle', ['UNK']], ['CRN_AmbAstDev', ['UNK', 'Quad cane', 'Straight cane', 'Wheelchair', 'Stretcher', 'Walker', 'Other']], ['CRN_MusculPainsc', ['UNK']], ['FA_Site1', ['UNK', 'Above Elbow-Left', 'Leg-Right', 'Below Elbow-Left', 'Above Elbow-Right', 'Jugular-Right', 'Leg-Left', 'Below Elbow-Right', 'Subclavian-Right', 'Jugular-Left', 'Subclavian-Left', 'Other-Right', 'Other-Left', 'Other-N/A', 'Upper arm-Left', 'Thigh-Left', 'Upper arm-Right', 'Wrist/Forearm-Left', 'Wrist/Forearm-Right', 'Above Elbow-N/A', 'Wrist/forearm-Left', 'Upper arm-INFORMATION NOT AVAILABLE', 'Internal jugular-Right']], ['CRN_AmbPainscle', ['UNK']], ['CRN_GastPainscal', ['UNK']], ['FA_Status2', ['UNK', 'Active', 'Maturing', 'Waiting for Removal']], ['CRN_NeuroDizzi', ['UNK', 'N/A', 'From sitting to standing position', 'Immediately following last dialysis', 'When up walking around', 'When sitting or lying', 'Slurred speech or abnormal speech pattern']], ['FA_Type1', ['UNK', 'AV Graft-Standard (PTFE)', 'AV Graft-Unknown', 'AV Fistula-Standard', 'Catheter-Tunneled', 'AV Fistula-Transposed', 'AV Fistula-Unknown', 'AV Graft-Bovine', 'Catheter-Unknown', 'Catheter-Non-tunneled', 'AV Graft-GORE ACUSEAL', 'AV Graft-HeRO', 'AV Graft-Other', 'AVFistula standard', 'AVGraft PTFE', 'AV Graft-Flixene', 'AVGraft other', 'AVFistula transposed', 'Tunneled catheter-Permanent', 'Non-tunneled catheter-Temporary']], ['CMD_DlDoseGl', ['UNK', 'spKt/V => 1.2 (HD)', 'Kt/V => 1.7 / Week (PD)', 'Other']], ['CRN_AmbAsmt', ['UNK', 'Ambulates with assistive device', 'Ambulates with assistance from 1 or more staff members', 'Ambulates without assistance', 'Has assistive device but does not use']], ['PD_Type1', ['UNK', 'PD Catheter-Double Cuff', 'PD Catheter-Single Cuff']], ['CRN_PDPresInf', ['UNK', 'N/A', 'Peritonitis', 'Tunnel', 'Exit site']], ['PA_ExpPain', ['UNK', 'No    (No follow-up plan required)', 'Yes  (Documentation of at least one pain area is required)', 'Yes (Documentation of at least one pain area is required)']], ['CMD_CalciumGl', ['UNK', '8.5 - 10.0', 'Other']], ['PD_Status1', ['UNK', 'Active']], ['CRN_VAASMethod', ['UNK', 'Physical findings', 'Intra-access flow method', 'Venous pressure monitoring', 'Arterial pressure monitoring', 'Recirculation studies', 'Duplex ultrasound', 'Static pressure method']], ['CRN_RespLung', ['UNK', 'Clear', 'Decreased breath sounds', 'Rales', 'Wheezing', 'Other']], ['CRN_InitialCIA', ['UNK', 'Initial CIA', 'Annual CIA', '90 Day CIA', 'Monthly CIA (unstable)', 'Change in Modality', 'Potential involuntary discharge']], ['CRN_HeadNeuroFnd', ['UNK', 'N/A', 'Numbness', 'Other', 'Gait changes', 'Decreased sensation', 'Paralysis']], ['CRN_CardioPit', ['UNK', 'N/A', '1+', '2+', '3+', '4+']], ['CRN_MusculProbTy', ['UNK']], ['FA_DiabMeds', ['UNK', 'Not applicable', 'Uses as prescribed', 'Does not use as prescribed']], ['CRN_AmbProbType', ['UNK', 'Chronic', 'No problems ambulating', 'N/A - Does not ambulate', 'Sudden onset', 'Recurrent']], ['CRN_AbdProbType', ['UNK']], ['CRN_NeckProbType', ['UNK']], ['CRN_CardioProb', ['UNK']], ['CRN_HeadProbType', ['UNK']]]
    data_cats2 = [['CMD_URRGl', ['UNK', '>/=65', 'N/A']], ['CMD_TSatGl', ['UNK', '30 - 50%', 'Other']], ['CMD_AnemiaGl', ['UNK', 'Target HGB 10.0 - 11.0 g/dL', 'Other']], ['FA_Status1', ['UNK', 'Active', 'Maturing', 'Waiting for Removal']], ['CRN_CardNeckLoc', ['UNK', 'Right arm', 'Left arm', 'Right leg', 'Left leg']], ['CRN_SkinProbType', ['UNK', 'N/A', 'Recurrent', 'Chronic', 'Sudden onset']], ['CRN_GeniProbType', ['UNK', 'N/A', 'Chronic', 'Sudden onset', 'Recurrent']], ['CRN_NeuroType', ['UNK', 'N/A', 'Chronic', 'Recurrent', 'Sudden onset']], ['CRN_GastProbType', ['UNK', 'N/A', 'Recurrent', 'Chronic', 'Sudden onset']], ['CRN_RespProbType', ['UNK', 'N/A', 'Chronic', 'Recurrent', 'Sudden onset']], ['CRN_InfProbType', ['UNK', 'N/A', 'Recurrent', 'Chronic', 'Sudden onset']], ['FA_AmpLegAtHip', ['UNK', 'Neither', 'Left', 'Both', 'Right']], ['FA_AmpArmElbow', ['UNK', 'Neither', 'Left', 'Both', 'Right']], ['FA_AmpPartHand', ['UNK', 'Neither', 'Right', 'Both', 'Left']], ['FA_AmpPtFoot', ['UNK', 'Neither', 'Right', 'Both', 'Left']], ['FA_AmpArmShlder', ['UNK', 'Neither', 'Left', 'Right', 'Both']], ['FA_AmpToes', ['UNK', 'Neither', 'Right', 'Both', 'Left']], ['FA_AmpLegBeKnee', ['UNK', 'Neither', 'Left', 'Both', 'Right']], ['FA_AmpHand', ['UNK', 'Neither', 'Right', 'Left', 'Both']], ['FA_AmpLegAbvKnee', ['UNK', 'Neither', 'Both', 'Left', 'Right']], ['FA_AmpFoot', ['UNK', 'Neither', 'Right', 'Left', 'Both']], ['FA_AmpAbArmElbow', ['UNK', 'Neither', 'Right', 'Left', 'Both']], ['FA_AmpFingers', ['UNK', 'Neither', 'Both', 'Left', 'Right']], ['CRN_BPVUrineOut', ['UNK', 'None', 'Yes', '>500 ml']], ['CRN_VACanMethod', ['UNK', 'Site rotation', 'N/A', 'Buttonhole']], ['CRN_HSGood', ['UNK', 'Good', 'Fair', 'Poor']], ['CMD_MinMetGl', ['UNK', 'Phos 3.0 - 5.5', 'Other']], ['CMD_PTHGl', ['UNK', '150 - 600', 'Other']], ['CRN_CardioAsAReg', ['UNK', 'Regular', 'Irregular']], ['CRN_CardioAsRReg', ['UNK', 'Regular', 'Irregular']], ['CRN_CardNeckType', ['UNK', 'Sitting', 'Standing']]]
    
    data_cats = data_cats1 + data_cats2          
    cols_cats = [c[0] for c in data_cats]               
    
    # check required columns are there
    check_schema(df,cols_cats)

    df_cats_all = make_dummies(df,data_cats[0][0],data_cats[0][1])
    
    for ii in range(1,len(data_cats)):
        df_cats = make_dummies(df,data_cats[ii][0],data_cats[ii][1])
        df_cats_all = pd.concat([df_cats_all, df_cats],axis = 1)
    
    cols_cats = list(df_cats_all.columns)
    # add on the columns
    df = pd.concat([df,df_cats_all],axis = 1)
    
    # fill missing columns
    for c in cols_cats:
        df[c] = df[c].fillna(0)

    
    return df
def split_checkboxes_CRN(df):
    
    data_boxes = [['CRN_AuditProb', ['UNK', 'Deaf', 'Tinnitus', 'Wears hearing assist device', 'N/A', 'Some hearing loss']], ['CRN_MusculPTDesc', ['UNK', 'Sharp', 'Other', 'Radiating', 'Aching', 'Relieved with medication', 'Dull']], ['CRN_NeuroVisual', ['UNK', 'Retinopathy', 'Loss of peripheral vision', 'Double vision', 'Vision loss', 'N/A', 'Wears glasses/contacts', 'Blurred vision', 'Glaucoma']], ['CRN_PDDesc1', ['UNK', 'New lesion', 'Swollen', 'Other', 'Red', 'Do not believe it is working', 'Painful', 'Bruised']], ['CRN_VAIntType', ['UNK', 'Access removal', 'Angioplasty', 'Other', 'Declotting', 'Surgical revision']], ['PA_AbdDesc', ['UNK', 'Burning.', 'Radiating.', 'Aching.', 'Cramping.', 'Dull.', 'Sharp.']], ['PA_AbdLoc', ['UNK', 'LLQ.', 'LUQ.', 'RLQ.', 'RUQ.', 'Diffuse.']], ['PA_HeadacheLoc', ['UNK', 'Right side.', 'Left side.', 'Ocular.', 'Back.', 'Top.', 'Frontal.']], ['PA_MuscleDesc', ['UNK', 'Abdomen.', 'Foot.', 'Leg.', 'Hand.', 'Back.', 'Arm.', 'Finger.']], ['CRN_BackPTDesc', ['UNK', 'Sharp', 'Lower back', 'Upper back', 'Relieved with medication', 'Dull']], ['CRN_GastDesc', ['UNK', 'Constipation', 'Loss of appetite', 'Nausea', 'Blood in stool', 'Vomiting blood', 'Vomiting', 'Indigestion', 'Diarrhea']], ['CRN_PDAsmtDesc', ['UNK', 'Patent', 'Product damage (ex. torn)', 'Painful', 'Poor flow']], ['CRN_CardioPTDesc', ['UNK', 'Sharp', 'Precordial pressure (angina)', 'Required NTG for relief', 'Radiating', 'Exacerbation with exercise', 'Dull']], ['CRN_PDDesc2', ['UNK', 'Swollen', 'Other', 'Red', 'Do not believe it is working', 'Painful']], ['CRN_SkinAssmt', ['UNK', 'Jaundiced', 'Tender', 'Pale', 'Inflammation', 'Cyanotic', 'Rash', 'Excoriated', 'Abscess', 'Open sores/broken skin', 'N/A', 'Redness']], ['PA_NeckDesc', ['UNK', 'Burning.', 'Radiating.', 'Aching.', 'Dull.', 'Sharp.']], ['CRN_VAEntryDesc', ['UNK', 'If patient has CVC, initiate HD vascular access plan', 'Swollen', 'If patient has CVC and refuses permanent access address in Plan of Care', 'Tender', 'Indurated area', 'Rash', 'Other', 'Inflamed', 'Red', 'Hematoma-large', 'Hematoma-small', 'Exudate']], ['PA_BackDesc', ['UNK', 'Burning.', 'Radiating.', 'Aching.', 'Dull.', 'Sharp.']], ['PA_LowerLoc', ['UNK', 'Right.', 'Left.']], ['CRN_NeuroAssmt', ['UNK', 'Leg/arm paralysis', 'Agitated', 'Altered consciousness', 'Psychotic', 'Lethargic', 'Slurred speech', 'Other', 'Bizarre behavior', 'Combative', 'Depressed', 'N/A', 'Facial drooping', 'Confused']], ['CRN_RespAsmt', ['UNK', 'Cyanotic', 'Dyspnea on exertion', 'Dyspnea at rest', 'No complaints', 'Orthopnea', 'Labored breathing']], ['CRN_VACanAssmt', ['UNK', 'Other', 'Difficulties with cannulation', 'No difficulties with cannulation', 'Significant hematomas']], ['PA_PDCathLoc', ['UNK', 'Right.', 'Left.', 'Middle.']], ['PA_UpperDesc', ['UNK', 'Hand.', 'Arm.', 'Finger.']], ['PA_VALoc', ['UNK', 'Left arm.', 'Right arm.', 'Chest.', 'Right groin.', 'Subclavian.', 'Left groin.', 'Other.', 'IJ.']], ['CRN_RArmAssmt', ['UNK', 'Joint swelling', 'Bruising', 'Tender', 'Soft tissue swelling', 'Lesion', 'Other', 'Evidence of trauma']], ['PA_MuscleLoc', ['UNK', 'Right.', 'Left.']], ['PA_UrinDesc', ['UNK', 'Radiating.', 'Burning.', 'Sharp.']], ['CRN_AbdDesc', ['UNK', 'Non-menstrual', 'Sharp', 'Menstrual', 'Colic', 'Radiating', 'Cramping', 'Dull']], ['CRN_VACathDes', ['UNK', 'Product damage (ex. Torn)', 'Poor flows', 'Clotted']], ['PA_ExtLoc', ['UNK', 'Legs.', 'Arms.', 'Fingers.', 'Toes.']], ['CRN_BPSymptoms', ['UNK', 'Cramping', 'Hypotension', 'Hypertension']], ['CRN_GastAssmt', ['UNK', 'Hernia', 'Rebound to direct touch', 'Ascites', 'Colostomy', 'Blood in stool', 'Other', 'Blood in vomitus', 'Feeling of fullness (PD patients)', 'Mass', 'Distended abdomen', 'N/A', 'Incontinent of bowel', 'Tender abdomen']], ['PA_ChestLoc', ['UNK', 'Sternum.', 'Right.', 'Left.']], ['CRN_HeadPTDesc', ['UNK', 'Posterior', 'Frontal', 'Sharp', 'Dental pain', 'Relieved with medications', 'Migraine', 'Diffuse (scattered/spread)', 'Ocular', 'Dull']], ['CRN_MusculAsmt', ['UNK', 'Joint swelling', 'Bruising', 'Tender', 'Soft tissue swelling', 'Lesion', 'Gait changes', 'Ulcerated area', 'Other', 'Inflamed', 'Decreased sensation', 'N/A', 'Evidence of trauma']], ['PA_FollowPlan', ['UNK', 'Pharmacologic or educational intervention.', 'Treatment is contraindicated.', 'Initial treatment plan is still in effect.', 'Notification to other care provider.', 'No follow-up plan required.', 'Planned follow-up appointment or referral.']], ['CRN_CardNeckAsmt', ['UNK', 'Diaphoric', 'Palpitations', 'Neck vein distention @ 45 degree elevation', 'Cyanotic', 'Other', 'Neck vein distention', 'Diaphoretic', 'N/A', 'Appears anxious']], ['PA_JointLoc', ['UNK', 'Right.', 'Left.']], ['PA_UpperLoc', ['UNK', 'Right.', 'Left.']], ['CRN_GeniAssmt', ['UNK', 'Incontinent of urine', 'Urine cloudy', 'Blood in urine', 'No problems', 'Other', 'Urine clear']], ['CRN_PDCathEnt', ['UNK', 'Swollen', 'Tender', 'Indurated area', 'Inflamed', 'Red', 'N/A', 'Exudate']], ['CRN_VAAVFDes', ['UNK', 'Swollen', 'No blood flashback on cannulation', 'Tender', 'Rash', 'Leaking needle site', 'Inderated', 'Hematoma-large', 'Ulcer', 'Indurated', 'Hematoma-small', 'Exudate', 'Clot returned on cannulation and aspiration']], ['CRN_VADesc1', ['UNK', 'New lesion', 'Swollen', 'Other', 'Do not believe it is working', 'Red', 'Painful', 'Bruised']], ['CRN_VADesc2', ['UNK', 'New lesion', 'Swollen', 'Other', 'Do not believe it is working', 'Red', 'Painful', 'Bruised']], ['PA_PDCathDesc', ['UNK', 'Burning.', 'Radiating.', 'Aching.', 'Dull.', 'Sharp.']], ['CRN_MusculCramp', ['UNK', 'N/A', 'Abdomen/back', 'Arms/hands', 'Feet/legs']], ['CRN_RLegAssmt', ['UNK', 'Joint swelling', 'Bruising', 'Tender', 'Soft tissue swelling', 'Lesion', 'Ulcer on foot', 'Other', 'Ulcer on toe', 'Evidence of trauma']], ['CRN_CMCDesc', ['UNK', 'Abdomen/back', 'Arms/hands', 'Feet/legs']], ['CRN_NeuroDesc', ['UNK', 'Depressed feeling', 'Insomnia', 'Alert and oriented x3', 'Anxious', 'Sleepy']], ['CRN_RespDesc', ['UNK', 'Sleep apnea', 'Asthma attack', 'Wheezing', 'Exposure to second hand smoke', 'Pleuritic chest pain', 'Productive', 'Cough', 'Short of breath', 'History of smoking', 'Runny nose or "cold symptoms"']], ['CRN_VADesc3', ['UNK', 'New lesion', 'Swollen', 'Other', 'Do not believe it is working', 'Red', 'Painful', 'Bruised']], ['FA_DiabDiet', ['UNK', 'Other', 'No conc sweets', 'CHO controlled']], ['PA_LowerDesc', ['UNK', 'Toe.', 'Leg.', 'Foot.']], ['PA_BackLoc', ['UNK', 'Mid.', 'Lower.', 'Upper.', 'Flank.']], ['PA_HeadacheDesc', ['UNK', 'Radiating.', 'Sharp.', 'Dull.']], ['PA_NeckJawLoc', ['UNK', 'Both.', 'Right.', 'Left.']], ['PA_VADesc', ['UNK', 'Burning.', 'Radiating.', 'Aching.', 'Dull.', 'Sharp.']], ['CRN_CarNeckDesc', ['UNK', 'Other', 'Sharp', 'Radiating', 'Dull']], ['CRN_GeniPTDesc', ['UNK', 'Difficulty urinating', 'Burning on urination', 'Suprapubic pain (complete pain assessment)', 'Frequency of urination', 'Suprapubic pain', 'Burning on urination (complete pain assessment)', 'Other', 'Painful urination', 'Urgency of urination', 'Painful urination (complete pain assessment)']], ['CRN_InfDesc', ['UNK', 'Malaise (generally "feeling bad")', 'With chills', 'No fever', 'Intermittent', 'Did not check with thermometer', 'Persistent']], ['CRN_LArmAssmt', ['UNK', 'Joint swelling', 'Bruising', 'Tender', 'Soft tissue swelling', 'Lesion', 'Other', 'Evidence of trauma']], ['CRN_LLegAssmt', ['UNK', 'Joint swelling', 'Bruising', 'Tender', 'Soft tissue swelling', 'Lesion', 'Ulcer on foot', 'Other', 'Ulcer on toe', 'Evidence of trauma']], ['PA_ExtDesc', ['UNK', 'Burning.', 'Radiating.', 'Dull.', 'Tingling.', 'Sharp.']], ['PA_NeckJawDesc', ['UNK', 'Burning.', 'Radiating.', 'Aching.', 'Dull.', 'Sharp.']], ['PA_UrinLoc', ['UNK', 'Flank.', 'Suprapubic.', 'With urination.']], ['CRN_PDDesc3', ['UNK', 'Other', 'Red', 'Painful', 'Do not believe it is working']], ['CRN_SkinPTDesc', ['UNK', 'Tender', 'Rash', 'Itching', 'Dry', 'Red']], ['CRN_VAAVGDes', ['UNK', 'Swollen', 'Tender', 'No blood flashback on cannulation', 'Rash', 'No thrill', 'Ulcer', 'No pulse', 'Red', 'Inflamed', 'Leaking needle site', 'No bruit', 'Hematoma-large', 'Inderated', 'Indurated', 'Hematoma-small', 'Clot returned on cannulation and aspiration']], ['PA_ChestDesc', ['UNK', 'Burning.', 'Radiating.', 'Aching.', 'Dull.', 'Sharp.']], ['PA_JointDesc', ['UNK', 'Toe.', 'Shoulder.', 'Wrist.', 'Hip.', 'Ankle.', 'Foot.', 'Knee.', 'Leg.', 'Thumb.', 'Elbow.', 'Finger.']], ['PA_NeckLoc', ['UNK', 'Right.', 'Front.', 'Left.', 'Back.']]]
    cols_boxes = [c[0] for c in data_boxes]       

    
    
    # check_schema
    check_schema(df,cols_boxes)
    
    df_checkboxes_all = split_checkbox(df,data_boxes[0][0],data_boxes[0][1])
    for ii in range(1,len(data_boxes)):
        df_checkboxes = make_dummies(df,data_boxes[ii][0],data_boxes[ii][1])
        df_checkboxes_all = pd.concat([df_checkboxes_all, df_checkboxes],axis = 1)

    cols_checkboxes = list(df_checkboxes_all.columns)
    # add on the columns
    df = pd.concat([df,df_checkboxes_all],axis = 1)
    # fill missing columns
    for c in cols_checkboxes:
        df[c] = df[c].fillna(0)
    
    return df


def add_feats_CRN(df):
    
    df = clean_CRN(df)
    df = add_CRN_cats(df)
    df = split_checkboxes_CRN(df)
    
    return df
def process_CRN(df_samples, df_data, cols_samples, date_samples):
    # This function processes the patient info
        
    # merge data on samples
    df_data = df_data.drop_duplicates()
    date_data= 'AX_ENTER_DT'
    
    df_data = df_data.sort_values(['MRN','AX_ENTER_DT','COLLECTED_DT'], ascending = False)
    df_data = df_data.drop_duplicates(subset = ['MRN','AX_ENTER_DT'], keep = 'first')
    
    #df_CRN_samples = merge_keep_last(df_samples[cols_samples], df_data, \
    #                                 date_samples, date_data, ['MRN'],cols_samples, use_equal = 1)
    
    df_samples = df_samples.sort_values(date_samples).reset_index(drop = True)
    df_data = df_data.sort_values(date_data).reset_index(drop = True)

    df_CRN_samples = pd.merge_asof(df_samples, 
                      df_data,
                 left_on = date_samples,
                 right_on = date_data,
                 by = 'MRN',
                 direction  = 'backward')
    
    df_CRN_samples = df_CRN_samples.sort_values(cols_samples).reset_index(drop = True)
    
    df_CRN_samples = add_feats_CRN(df_CRN_samples)
    
    df_CRN_samples['days_since_CRN'] = (df_CRN_samples[date_samples] - df_CRN_samples['AX_ENTER_DT']).dt.days
    
    # drop unnecessary columns & add days since
    
    return df_CRN_samples

def clean_HTPN(df):
    # converts Yes/No columns into 1,0,-1 (no value)
    
    cols_yn = ['HRN_AbdNormal', 'HRN_AbdPain', 'HRN_AccCmp_IntTr', 'HRN_AdhTrtmtComp', 'HRN_AdhWaterRec', 'HRN_Alert',
 'HRN_AnemPrescrib', 'HRN_AnemSelfAdm', 'HRN_AppetiteNorm', 'HRN_BackPain', 'HRN_BowelsNorm', 'HRN_BreathDiff',
 'HRN_ChangAmbStat', 'HRN_ChangEENT', 'HRN_ChestPain', 'HRN_Cooperative', 'HRN_CVPtHadIssue', 'HRN_ExitSiteNorm',
 'HRN_ExtremPain', 'HRN_ExtremPainT1', 'HRN_ExtremPainT2', 'HRN_Fever', 'HRN_FeverTrig2', 'HRN_GenCom_IntTr', 'HRN_GoodCathFl',
 'HRN_HeadPain', 'HRN_LowExtrPain', 'HRN_LungsClear', 'HRN_Malaise', 'HRN_MuscleCramp', 'HRN_NauseaVom', 'HRN_Orientted',
 'HRN_PDMod_Trig', 'HRN_ProduceUrine', 'HRN_ShortBreath', 'HRN_SkinColor', 'HRN_SleepNorm', 'HRN_SSEdemaNeck', 'HRN_SummRNEval',
 'HRN_Swelling', 'HRN_SymPeriton', 'HRN_UppExtrPain', 'HT_HeartRateNorm', 'HT_HospContact', 'HT_Peritonitis', 'HT_RespirationOK', 'HT_SchedVisit']

    
    cols_num = [  'HRN_VSWghtCombo',  'PM_Weight',
        'PM_Height']
    
    # convert all yes/no
    check_schema(df,cols_yn + cols_num)
    df = convert_all_yes_no(df,cols_yn)
    
    # convert numerical to numbers
    for c in cols_num:    
        df[c] = pd.to_numeric(df[c],errors = 'coerce')
    
    df['HRN_VSPtRepWgt'] = df['HRN_VSPtRepWgt'].fillna('').str.replace('/','')
    df['HRN_VSPtRepWgt'] = pd.to_numeric(df['HRN_VSPtRepWgt'],errors = 'coerce')
    
    return df


def add_HTPN_cats(df):
    # create one hot encoding for each column specified below and combine them
    
    data_cats = [['HRN_AbdPainBeg', ['UNK', 'Other', 'Within the last week', 'Since my last clinic visit', 'Within past 24 hours']], ['HRN_AbdPainLast', ['UNK', '>24 hours', 'A few minutes', 'On-going', 'All day', 'A couple of hours']], ['HRN_AdqTransport', ['UNK', 'High average', 'Low average', 'High', 'Low']], ['HRN_CVSympBegin', ['UNK', 'Since my last clinic visit', 'Other', 'Within the last week', 'Within past 24 hour']], ['HRN_CVSympLast', ['UNK', 'A few minutes', 'On-going', '> 24 hours', 'A couple of hours', 'All day']], ['HRN_FeverBegin', ['UNK', 'Within the last week', 'Within past 24 hours', 'Other', 'Since my last clinic Visit']], ['HRN_FeverPresent', ['UNK', 'On-going', '>24 hours', 'A couple of hours', 'All day', 'A few minutes']], ['HRN_GISymptBeg', ['UNK', 'Other', 'Since my last clinic visit', 'Within the last week', 'Within past 24 hours']], ['HRN_GISymptLast', ['UNK', 'On-going', '>24 hours', 'All day', 'A few minutes', 'A couple of hours']], ['HRN_GUSumpLast', ['UNK', 'On-going', '>24 hours', 'A few minutes', 'A couple of hours', 'All day']], ['HRN_GUSympBegin', ['UNK', 'Other', 'Within the last week', 'Since my last clinic visit', 'Within past 24 hours']], ['HRN_HeadacheLast', ['UNK', 'On-going', 'All day', 'A couple of hours', '>24 hours', 'A few minutes']], ['HRN_HeadachePain', ['UNK', 'Within past 24 hours', 'Other', 'Within the last week', 'Since my last clinic Visit']], ['HRN_HeadacheSev', ['UNK', '0 No hurt', '4 Hurts Little More', '8 Hurts Whole Lot', '2 Hurts Little Bit', '6 Hurts Even More', '10 Hurts Worst']], ['HRN_MalaiseBegin', ['UNK', 'Since my last clinic Visit', 'Within the last week', 'Other', 'Within past 24 hours']], ['HRN_MalaiseSympt', ['UNK', 'On-going', '>24 hours', 'All day', 'A few minutes', 'A couple of hours']], ['HRN_RespSympBeg', ['UNK', 'Other', 'Within the last week', 'Within past 24 hours', 'Since my last clinic visit']], ['HRN_RespSympLast', ['UNK', '> 24 hours', 'On-going', 'A few minutes', 'A couple of hours', 'All day']], ['HRN_SHNPnBegin', ['UNK', 'Other', 'Since my last clinic visit', 'Within the last week', 'Within past 24 hours']], ['HRN_SHNPnLast', ['UNK', 'On-going', '> 24 hours', 'A few minutes', 'All day', 'A couple of hours']], ['HRN_SS_SwellHowL', ['UNK', '> 24 hours', 'A couple of hours', 'On-going', 'All day', 'A few minutes']], ['HRN_SS_SwellStar', ['UNK', 'Other', 'Within past 24 hours', 'Since my last clinic visit', 'Within the last week']], ['HRN_SSBegin', ['UNK', 'Other', 'Within the last week', 'Within past 24 hours', 'Since my last clinic visit']], ['HRN_SSEdemaSev', ['UNK', '2+ Mild pitting', '1+ Slight', '3+ Pitting', '4+ Severe pitting']], ['HRN_SSLast', ['UNK', '> 24 hours', 'On-going', 'A few minutes', 'A couple of hours', 'All day']], ['HT_SchedVisitTr', ['UNK', 'Yes', '2']]]
     
    cols_cats = [c[0] for c in data_cats]               
    
    # check required columns are there
    check_schema(df,cols_cats)

    df_cats_all = make_dummies(df,data_cats[0][0],data_cats[0][1])
    
    for ii in range(1,len(data_cats)):
        df_cats = make_dummies(df,data_cats[ii][0],data_cats[ii][1])
        df_cats_all = pd.concat([df_cats_all, df_cats],axis = 1)
    
    cols_cats = list(df_cats_all.columns)
    # add on the columns
    df = pd.concat([df,df_cats_all],axis = 1)
    
    # fill missing columns
    for c in cols_cats:
        df[c] = df[c].fillna(0)

    
    return df


def split_checkboxes_HTPN(df):
    
    data_boxes = [['HRN_AbdPainDescr',
  ['UNK',
   'Menstrual cramping',
   'RLQ',
   'Colic',
   'LLQ',
   'Diffuse',
   'Sharp',
   'Non-menstrual cramping',
   'RUQ',
   'Dull',
   'LUQ',
   'Other']],
 ['HRN_AbdPainFind',
  ['UNK',
   'Distended abdomen',
   'Rebound to direct touch',
   'Tender abdomen - RLQ',
   'Tender abdomen - LLQ',
   'Tender abdomen - LUQ',
   'Tender abdomen - RUQ',
   'Mass',
   'Other',
   'Hernia',
   'Ascites',
   'Blood in stool']],
 ['HRN_AccessComp',
  ['UNK',
   'Inadequate flow',
   'Inability to cannulate',
   'Suspected infection',
   'Prolonged bleeding',
   'New/pseudo or true aneurysm',
   'None',
   'Other',
   'Thrombosed',
   'Severe infiltration']],
 ['HRN_AccessExEv',
  ['UNK',
   'Redness',
   'Swelling',
   'Crusty/granulation',
   'Other',
   'Hernia',
   'Cuff extrusion',
   'Purulent drainage',
   'Tenderness']],
 ['HRN_AccessPDEv',
  ['UNK',
   'Constipation',
   'Fibrin in catheter',
   'Problems upon draining',
   'Problems upon infusing',
   'Other']],
 ['HRN_AdhConcernHD',
  ['UNK',
   'Frequent inadequate documentation in logs',
   'Missed treatments as compared to prescription',
   'Other',
   'Failure to bring treatment logs / run sheets to appointment',
   'Lack of prescription comprehension / knowledge',
   'Lack of prescription comprehensi',
   'Caregiver issues',
   'Failure to bring equipment/water logs to appointment']],
 ['HRN_AdhConcernPD',
  ['UNK',
   'Missed treatments/exchanges as compared to prescription',
   'Frequent inadequate documentation in logs',
   'Other',
   'Failure to bring treatment logs / run sheets to appointment',
   'Lack of prescription comprehension / knowledge',
   'Caregiver issues']],
 ['HRN_CVFindings',
  ['UNK', 'Diaphoretic', 'Anxious', 'In acute distress', 'Other']],
 ['HRN_CVPtComplain', ['UNK', 'Chest pain only', 'Palpitations', 'Other']],
 ['HRN_CVPtDescribe',
  ['UNK',
   'Pleuritic',
   'Relief with NTG',
   'Exacerbation with exercise',
   'Sharp',
   'Dull',
   'Other',
   'Radiating',
   'Precordial pressure (typical angina)']],
 ['HRN_FeverFinding',
  ['UNK',
   'Possibly related to an access infection (peritoneal)',
   'Possibly related to an access infection (catheter)',
   'Possibly related to a urinary tract infection',
   'Possibly related to an access infection (fistula/graft)',
   'Lesion (please record site in note section)',
   'Chills or Rigors',
   'Fever of unknown origin',
   'Other',
   'Cough',
   'Possibly related to an infection (wound/abscess)']],
 ['HRN_GenAppCompl',
  ['UNK',
   'Confusion',
   'Feelings of anxiety',
   'Feelings of depression',
   'Fatigue',
   'Other',
   'Irritability']],
 ['HRN_GIComplaint',
  ['UNK',
   'Vomiting blood',
   'Constipation',
   'Nausea',
   'Vomiting',
   'Black tarry stool',
   'Mild upper gastric pain',
   'Dysphagia (difficulty swallowing)',
   'Hiccups',
   'Diarrhea',
   'Indigestion',
   'Other',
   'Bright red blood in stool',
   'Loss of appetite',
   'Taste alterations']],
 ['HRN_GUPtComplain',
  ['UNK',
   'Decrease in urine output',
   'Blood in urine',
   'No complaints',
   'Strong odor',
   'Other',
   'Urgency',
   'Pain on urination',
   'Increase in urine output',
   'Sexual dysfunction',
   'Increased frequency',
   'Incontinence',
   'Heavy menses',
   'Cloudy urine']],
 ['HRN_Headache',
  ['UNK',
   'Dental lesion causing headache',
   'Posterior',
   'Frontal',
   'Sharp',
   'Ocular',
   'Dull',
   'Migraine like',
   'Other',
   'Relieved with medication',
   'Sinus',
   'Diffuse (scattered/spread)']],
 ['HRN_IntervenPlan',
  ['UNK',
   'Culture and sensitivity with antibiotics',
   'Hospitalization >24 hours',
   'Observation hospital <24 hours',
   'Observe',
   'Antibiotics w/out culture and sensitivity',
   'Other']],
 ['HRN_NewUrineSymp',
  ['UNK',
   'Dysuria',
   'Urgency',
   'Incontinence',
   'Other',
   'Frequency',
   'Hematuria']],
 ['HRN_PsychCompl',
  ['UNK',
   'Difficulty staying asleep',
   'Slurred speech or abnormal speech pattern',
   'Unable to return to sleep after waking',
   'Unable to follow instructions',
   'Paralysis (describe site in note)',
   'Sleep apnea',
   'Sleep walking',
   'Numbness (describe site in note)',
   'Requires sleep aids/medications (describe in note)',
   'Difficulty expressing oneself',
   'Difficulty getting to sleep',
   'Other',
   'Insomnia',
   'Waking early']],
 ['HRN_PtComplains',
  ['UNK',
   'Chills',
   'Other',
   'Intermittent Fever',
   'Patient took temperature',
   'Persistent Fever']],
 ['HRN_RespBrSounds', ['UNK', 'LLL', 'RUL', 'LUL', 'RLL']],
 ['HRN_RespFindings',
  ['UNK',
   'Breath sounds: clear',
   'Breath sounds: decreased breath sounds or no breath sounds',
   'Pink sputum',
   'Appears anxious',
   'Labored breathing (dyspnea)',
   'Breath sounds: rales/crackling',
   'Dyspneic',
   'Diaphoretic',
   'Shallow breathing',
   'Other',
   'Rapid breathing (tachypnea)',
   'Cyanotic',
   'Breath sounds: wheezing']],
 ['HRN_RespPtComp',
  ['UNK',
   'Pleurisy',
   'Other',
   'Dry cough',
   'Patient has recent chest x-ray',
   'Short of breath',
   'Productive cough, sputum characteristics, purulent',
   'Runny nose or cold symptoms',
   'Wheezing',
   'Shallow breathing',
   'Productive cough, sputum characteristics, bloody']],
 ['HRN_SHNComplain',
  ['UNK',
   'Diaphoresis (excessive sweating cold, clammy)',
   'Other',
   'Dry skin',
   'Itching',
   'Redness of skin',
   'Tenderness']],
 ['HRN_SHNPnFind',
  ['UNK',
   'Open sores/broken skin',
   'Abscess (non-access)',
   'Cold, clammy skin',
   'Pale',
   'Excoriation',
   'Jaundiced',
   'Redness of skin (describe site in note)',
   'Hematoma (non-access)',
   'Other',
   'Bruising',
   'Rash (describe site in note)',
   'Cyanotic']],
 ['HRN_SS_SwellLoc',
  ['UNK',
   'Legs',
   'Feet',
   'Other',
   'Abdomen',
   'Face',
   'Eyes',
   'Ankles',
   'Arms',
   'Lower back']],
 ['HRN_SSEdemaLoc',
  ['UNK',
   'Upper extremities',
   'Periorbital',
   'Lower extremities',
   'Abdominal',
   'Facial',
   'Other',
   'Sacral']],
 ['HRN_SSFindings',
  ['UNK',
   'Neck vein distention @ 45 elevation',
   'Dyspneic',
   'Appears anxious',
   'Pink sputum',
   'Diaphoretic',
   'Other',
   'Cyanotic']],
 ['HRN_SSPtComplain',
  ['UNK',
   'Shortness of breath at rest',
   'Shortness of breath on exertion',
   'Shortness of breath at night that makes the patient sit up',
   'Other',
   'Shortness of breath when lying down']],
 ['HRN_SummSendAler',
  ['UNK',
   'Clinical manager',
   'Home program manager',
   'Social worker',
   'Physician',
   'Dietitian']],
 ['HRN_SummServices',
  ['UNK',
   'Vaccinations',
   'PD transfer line changed today',
   'Other',
   'Education',
   'Problem-based care']]]
    
    cols_boxes = [c[0] for c in data_boxes]       

    
    
    # check_schema
    check_schema(df,cols_boxes)
    
    df_checkboxes_all = split_checkbox(df,data_boxes[0][0],data_boxes[0][1])
    for ii in range(1,len(data_boxes)):
        df_checkboxes = make_dummies(df,data_boxes[ii][0],data_boxes[ii][1])
        df_checkboxes_all = pd.concat([df_checkboxes_all, df_checkboxes],axis = 1)

    cols_checkboxes = list(df_checkboxes_all.columns)
    # add on the columns
    df = pd.concat([df,df_checkboxes_all],axis = 1)
    # fill missing columns
    for c in cols_checkboxes:
        df[c] = df[c].fillna(0)
    
    return df


def add_feats_HTPN(df):
    
    df = clean_HTPN(df)
    df = add_HTPN_cats(df)
    df = split_checkboxes_HTPN(df)
    
    return df



def process_HTPN(df_samples, df_data, cols_samples, date_samples):
    # This function processes the patient info
        
    # merge data on samples
    df_data = df_data.drop_duplicates()
    date_data= 'AX_ENTER_DT'
    
    df_data = df_data.sort_values(['MRN','AX_ENTER_DT','COLLECTED_DT'], ascending = False)
    df_data = df_data.drop_duplicates(subset = ['MRN','AX_ENTER_DT'], keep = 'first')
    
    #df_HTPN_samples = merge_keep_last(df_samples[cols_samples], df_data, \
    #                                 date_samples, date_data, ['MRN'],cols_samples, use_equal = 1)
    
    df_samples = df_samples.sort_values(date_samples).reset_index(drop = True)
    df_data = df_data.sort_values(date_data).reset_index(drop = True)

    df_HTPN_samples = pd.merge_asof(df_samples, 
                      df_data,
                 left_on = date_samples,
                 right_on = date_data,
                 by = 'MRN',
                 direction  = 'backward')
    
    df_HTPN_samples = df_HTPN_samples.sort_values(cols_samples).reset_index(drop = True)
    
    df_HTPN_samples = add_feats_HTPN(df_HTPN_samples)
    
    df_HTPN_samples['days_since_HTPN'] = (df_HTPN_samples[date_samples] - df_HTPN_samples['AX_ENTER_DT']).dt.days
    
    # drop unnecessary columns & add days since
    
    return df_HTPN_samples