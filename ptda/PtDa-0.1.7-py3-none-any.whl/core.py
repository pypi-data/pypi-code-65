import pandas as pd
import numpy as np
import pandas.core.algorithms as algos
import scipy.stats.stats as stats

"""
cn_df is a function to check whether feature(s) in the dataframe is categorical or numeric variable.
The function has two arguments i.e. df for dataframe and threshold for maximum length of unique value for categorical variable.
"""
def cn_df(df, threshold=10):
    is_cat_flag = []
    is_num_flag = []
    features = []
    uniq_vals = []

    for i in df.dtypes.index:
        uniq_val = len(df[i].value_counts())
        if uniq_val > threshold:
            features.append(i)
            is_cat_flag.append(0)
            is_num_flag.append(1)
            uniq_vals.append(uniq_val)
        else:
            features.append(i)
            is_cat_flag.append(1)
            is_num_flag.append(0)
            uniq_vals.append(uniq_val)

    cat_num_df = pd.DataFrame({'feature': features,
                               'count_of_unique_values': uniq_vals,
                               'categorical_var': is_cat_flag,
                               'numeric_var': is_num_flag})
    del is_cat_flag, is_num_flag, features, uniq_vals
    return cat_num_df

"""
num_woe_iv is a function to calculate woe and iv based on numeric variable(s).
The function takes three arguments as follow:
1. X = features that we would like to explore
2. Y = the target variable, please bear in mind that you should rename your target variable into target
3. n_bin = bins that will be generated for each feature, the default is 20
"""
def num_woe_iv(X, Y):
    df1 = pd.DataFrame({"X": X, "Y": Y})
    miss = df1[['X', 'Y']][df1.X.isnull()]
    notmiss = df1[['X', 'Y']][df1.X.notnull()]
    r = 0
    while np.abs(r) < 1:
        try:
            d1 = pd.DataFrame({'X': notmiss.X, 'Y': notmiss.Y, 'bucket': pd.qcut(notmiss.X, n_bin)})
            d2 = d1.groupby('bucket', as_index=True)
            r, p = stats.spearmanr(d2.mean().X, d2.mean().Y)
            n_bin = n_bin - 1
        except Exception as e:
            n_bin = n_bin - 1

    if len(d2) == 1:
        n = 3
        bins = algos.quantile(notmiss.X, np.linspace(0, 1, n))
        if len(np.unique(bins)) == 2:
            bins = np.insert(bins, 0, 1)
            bins[1] = bins[1] - (bins[1] / 2)
        d1 = pd.DataFrame(
            {"X": notmiss.X, "Y": notmiss.Y, "bucket": pd.cut(notmiss.X, np.unique(bins), include_lowest=True)})
        d2 = d1.groupby('bucket', as_index=True)

    d3 = pd.DataFrame({}, index=[])
    d3['event'] = d2.sum().Y
    d3['non_event'] = d2.count().Y - d2.sum().Y
    d3['event_rate'] = d2.sum().Y / d2.count().Y
    d3['non_event_rate'] = (d2.count().Y - d2.sum().Y) / d2.count().Y
    d3 = d3.reset_index(drop=True)

    if len(miss.index) > 0:
        d4 = pd.DataFrame({'value': np.nan}, index=[0])
        d4["event"] = miss.sum().Y
        d4["non_event"] = miss.count().Y - miss.sum().Y
        d3 = d3.append(d4, ignore_index=True)

    d3['dist_event'] = d3.event / d3.sum().event
    d3['dist_non_event'] = d3.non_event / d3.sum().non_event
    d3['woe'] = np.log(d3.dist_event / d3.dist_non_event)
    d3['iv'] = (d3.dist_event - d3.dist_non_event) * np.log(d3.dist_event / d3.dist_non_event)

    counter = 0
    for k, v in d2:
        d3['feature'] = X.name
        d3['value'] = v.values[counter][2]
        counter = counter + 1

    return d3

"""
cat_woe_iv is a function to calculate woe and iv based on categorical variable(s).
The function takes two arguments as follow:
1. X = features that we would like to explore
2. Y = the target variable, please bear in mind that you should rename your target variable into target
"""
def cat_woe_iv(X, Y):
    df1 = pd.DataFrame({"X": X, "Y": Y})
    miss = df1[['X', 'Y']][df1.X.isnull()]
    notmiss = df1[['X', 'Y']][df1.X.notnull()]
    df2 = notmiss.groupby('X', as_index=True)

    d3 = pd.DataFrame({}, index=[])
    d3['event'] = df2.sum().Y
    d3['non_event'] = df2.count().Y - df2.sum().Y

    if len(miss.index) > 0:
        d4 = pd.DataFrame({'value': np.nan}, index=[0])
        d4["event"] = miss.sum().Y
        d4["non_event"] = miss.count().Y - miss.sum().Y
        d3 = d3.append(d4, ignore_index=True)

    d3['event_rate'] = df2.sum().Y / df2.count().Y
    d3['non_event_rate'] = (df2.count().Y - df2.sum().Y) / df2.count().Y
    d3['dist_event'] = d3.event / d3.sum().event
    d3['dist_non_event'] = d3.non_event / d3.sum().non_event
    d3['woe'] = np.log(d3.dist_event / d3.dist_non_event)
    d3['iv'] = round((d3.dist_event - d3.dist_non_event) * np.log(d3.dist_event / d3.dist_non_event), 6)

    d3 = d3.reset_index(drop=True)

    d3['feature'] = X.name
    d3['value'] = X.unique().tolist()

    return d3

"""
woe_iv is a function to generate dataframe which contains WOE and IV for each feature (numeric and/or categorical).
The function has four arguments:
1. df = your input dataframe (Mandatory)
2. df_target = your target variable (Mandatory)
3. threshold = threshold for maximum length of unique value for categorical variable (Optional)
4. n_bin = initial bins that will be used for monotic binning (Optional)
"""
def woe_iv(df, df_target, threshold=10, n_bin=20):
    cn_df_data = cn_df(df, threshold)
    num_var = cn_df_data[cn_df_data['numerical_var'] == 1]['feature'].values.tolist()
    cat_var = cn_df_data[cn_df_data['categorical_var'] == 1]['feature'].values.tolist()
    final_df = pd.DataFrame({})

    if len(cat_var) > 0:
        for var in cat_var:
            cat_df = cat_woe_iv(df[var], df['target'])
            final_df = final_df.append(cat_df, ignore_index=True)

    if len(num_var) > 0:
        for var in num_var:
            num_df = num_woe_iv(df[var], df['target'], n_bin)
            final_df = final_df.append(num_df, ignore_index=True)

    final_df.replace([np.inf, -np.inf], 0, inplace=True)

    new_df = final_df.groupby(['feature'])[['feature', 'woe']].sum().reset_index()
    new_df.columns = ['feat', 'total_woe']
    final_df = pd.merge(final_df, new_df, how='left', left_on='feature', right_on='feat').drop('feat', axis=1)

    new_df2 = final_df.groupby(['feature'])[['feature', 'iv']].sum().reset_index()
    new_df2.columns = ['feat', 'total_iv']
    final_df = pd.merge(final_df, new_df2, how='left', left_on='feature', right_on='feat').drop('feat', axis=1)

    final_df = final_df[final_df['feature'] != 'target'].sort_values(['total_iv'], ascending=False)
    iv = pd.DataFrame({'IV': final_df.groupby('feature').total_iv.max()}).sort_values('IV', ascending=False)

    final_df2 = final_df[['feature', 'value', 'event', 'non_event', 'event_rate', 'non_event_rate', 'dist_event',
                          'dist_non_event', 'woe', 'iv', 'total_woe',
                          'total_iv']]

    del woe_iv_df, new_df, new_df2
    return final_df2, iv