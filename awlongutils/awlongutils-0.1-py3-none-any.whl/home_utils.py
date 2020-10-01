
import pandas as pd
from .common_utils import (load_df_file, check_schema)


def load_HT_dashboard(csv_filename, yaml_filename, encoding):
    # load the treatment table and convert dates
    
    df = load_df_file(csv_filename, yaml_filename, encoding)

    # check required columns are there
    check_schema(df,['RPTPERIOD','INSERTED_DT','HT_ADM_DATE','HT_DISCH_DATE'])


    # convert to dates
    df['RPTPERIOD']= pd.to_datetime(df['RPTPERIOD'], format='%Y-%m-%d', errors = 'coerce')
    df['INSERTED_DT']= pd.to_datetime(df['INSERTED_DT'], format='%Y-%m-%d', errors = 'coerce').dt.normalize()
    df['HT_ADM_DATE']= pd.to_datetime(df['HT_ADM_DATE'], format='%Y-%m-%d', errors = 'coerce')
    df['HT_DISCH_DATE']= pd.to_datetime(df['HT_DISCH_DATE'], format='%Y-%m-%d', errors = 'coerce')

    # drop duplicates
    df = df.drop_duplicates()  
    assert df.duplicated().sum() == 0,'duplicated rows'
    return df

