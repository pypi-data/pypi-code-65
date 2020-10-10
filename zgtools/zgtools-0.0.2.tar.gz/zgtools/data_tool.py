import numpy as np
import numpy.linalg as la
import pandas as pd
from sklearn.metrics import *
from xgboost import XGBClassifier
from matplotlib import pyplot as plt
#from model.dl_model import *
from sklearn import linear_model
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler

def label_percent(df_factor, percent_select, sort_col='next_ret', class_num=2, delete=False):
    df_factor.loc[:,'bin'] = None
    df_factor.loc[df_factor[sort_col] > df_factor[sort_col].quantile(q=percent_select[0]), 'bin'] = 1

    if class_num == 2:
        df_factor.loc[df_factor[sort_col] <= df_factor[sort_col].quantile(q=percent_select[1]), 'bin'] = 0
    elif class_num == 3:
        df_factor.loc[df_factor[sort_col] <= df_factor[sort_col].quantile(q=percent_select[1]), 'bin'] = -1

    if delete:
        df_factor.dropna(subset=['bin'], inplace=True)
    else:
        df_factor.loc[:, 'bin'] = df_factor['bin'].fillna(0)

    return df_factor


def label_threshold(df_stk, threshold, sort_col='next_ret', class_num=2):
    if class_num == 2:
        df_stk['bin'] = df_stk[sort_col].apply(lambda x: 1 if x > threshold else 0)
    return df_stk


# alpha大于0的股票标1否则标0
def lable_alpha(df_stk, df_index, diff=False, percent_select=None, delete=True):
    df_stk = df_stk.groupby(level=1).apply(lambda df: get_alpha(df, df_index, diff=diff))
    if not percent_select:
        df_stk['bin'] = df_stk['alpha'].apply(lambda x: 1 if x > 0 else 0)
    else:
        label_percent(df_stk, percent_select, sort_col='alpha', delete=delete)
    return df_stk


def get_beta(stk_ret, index_ret):
    beta = np.cov(stk_ret, index_ret)[0][1] / np.var(index_ret)
    return beta


def get_alpha(df_stk, df_benchmark, diff=False):
    # 找到每只股票的交易时间
    dates = df_stk.index.get_level_values('date').drop_duplicates().astype(str).tolist()
    # 找到收益率
    stk_ret = df_stk['next_ret'].values
    index_ret = df_benchmark[df_benchmark.index.isin(dates)]['next_ret'].values
    # 判断是直接做差得到alpha还是通过线性回归得到alpha
    df_stk['alpha'] = None
    if diff:
        for trade_date in dates:
            diff = df_stk.loc[trade_date, 'next_ret'] - \
                   df_benchmark[df_benchmark.index == str(trade_date).split()[0]].next_ret.values[0]
            df_stk.loc[trade_date, ['alpha']] = diff.tolist()
    else:
        # 计算贝塔
        try:
            beta = get_beta(stk_ret, index_ret)
        except:
            print(df_stk.iloc[0], stk_ret.shape, index_ret.shape)
        # 得到alpha
        df_stk.loc[:, ['alpha']] = (stk_ret - beta * index_ret).tolist()
    return df_stk

#得到x列和y列
def get_x_y(df, no_x_cols, label_col):
    x = df[df.columns.difference(no_x_cols)]
    y = df[label_col]#.astype(int)
    return x,y

#按时序分割x,y
def split_x_y(x, y, train_ratio=0.8):
    train_len = int(train_ratio * len(x))

    x_train = x[:train_len]
    y_train = y[:train_len]

    x_test = x[train_len:]
    y_test = y[train_len:]

    return x_train, y_train, x_test, y_test

#按时序分割成df_train, df_test
def split_df(x, y, train_ratio=0.8):
    train_len = int(train_ratio * len(x))

    x_train = x[:train_len]
    y_train = y[:train_len]

    x_test = x[train_len:]
    y_test = y[train_len:]

    return x_train, y_train, x_test, y_test


# 行业中性化
def data_scale_neutral(data, feature_names, indu_col='industry'):
    # feature_names = get_feature_names(data)
    data_ = data.copy()
    industrys = data[indu_col]  # 获取所属申万一级行业代码
    data_med = pd.get_dummies(data, columns=[indu_col], drop_first=True)
    n = len(data[indu_col].unique())  # 确定产生虚拟变量个数
    X = np.array(data_med[data_med.columns[-(n - 1):]])  # 行业虚拟变量作为为自变量
    for name in feature_names:
        y = np.array(data_[name])
        if la.matrix_rank(X.T.dot(X)) == (n - 1):  # 当矩阵满秩时，估计回归参数
            beta_ols = la.inv(X.T.dot(X)).dot(X.T).dot(y)
            residual = y - X.dot(beta_ols)  # 计算残差，并将其作为剔除行业影响的因子值
        else:
            residual = y  # 如果逆不存在的话 则 用原值
        data_[name] = residual
    return data_


# 行业中性化
# def data_scale_neutral(data, feature_names):
#     # feature_names = get_feature_names(data)
#     data_ = data.copy()
#     industrys = data['INDUSTRY_SW']  # 获取所属申万一级行业代码
#     data_med = pd.get_dummies(data, columns=['INDUSTRY_SW'], drop_first=True)
#     n = len(data['INDUSTRY_SW'].unique())  # 确定产生虚拟变量个数
#     X = np.array(data_med[data_med.columns[-(n - 1):]])  # 行业虚拟变量作为为自变量
#     for name in feature_names:
#         y = np.array(data_[name])
#         if la.matrix_rank(X.T.dot(X)) == (n - 1):  # 当矩阵满秩时，估计回归参数
#             beta_ols = la.inv(X.T.dot(X)).dot(X.T).dot(y)
#             residual = y - X.dot(beta_ols)  # 计算残差，并将其作为剔除行业影响的因子值
#         else:
#             residual = y  # 如果逆不存在的话 则 用原值
#         data_[name] = residual
#     return data_

# 市值中性化
def data_scale_CAP(data, feature_names):
    # feature_names = get_feature_names(data)
    data_ = data.copy()
    cap_weight = data_["CAP"] / data_["CAP"].sum()
    for name in feature_names:
        avg = (data_[name] * cap_weight).sum()
        data_[name] = (data_[name] - avg) / data_[name].std()
    return data_

def filter_extreme_mad(series,n=5): # MAD:中位数去极值
  median = series.quantile(0.5)
  new_median = ((series - median).abs()).quantile(0.50)
  max_range = median + n*new_median
  min_range = median - n*new_median
  return np.clip(series,min_range,max_range)

def process_extreme_data(df, factor_cols, method='mad', extreme_num=5):
    # df_proc = df[factor_cols]
    if method == 'mad':
        df.loc[:, factor_cols] = df.loc[:, factor_cols].groupby(level=0).apply(lambda x:x.groupby(axis=1, level=0).apply(lambda y:filter_extreme_mad(y[y.columns[0]], extreme_num)))    
    #     df_proc = df_proc.groupby(level=0).apply(lambda x:x.groupby(axis=1, level=0).apply(lambda y:filter_extreme_mad(y[y.columns[0]], extreme_num)))
    # df.loc[:, factor_cols] = df_proc
    return df

#数据标准化
def data_scale(df, factor_cols, scaler = None):

    df_basic_cols = df[df.columns.difference(factor_cols)]
    index_ = df.index
    df_proc = df.loc[:, factor_cols]

    # 如果没有scaler，初始化一个，如果有，用已经fit过的
    if not scaler:
        scaler = StandardScaler()
        arr_proc = scaler.fit_transform(df[factor_cols])
    else:
        arr_proc = scaler.transform(df[factor_cols]) # 直接调用传入的scaler进行分布转换
    df_proc = pd.DataFrame(arr_proc, index = index_, columns = factor_cols)
    df = pd.concat([df_basic_cols, df_proc], axis=1)
    return df, scaler


def get_model():

    test_size = 0.2                # proportion of dataset to be used as test set
    cv_size = 0.2                  # proportion of dataset to be used as cross-validation set
    N = 3                         # for feature at day t, we use lags from t-1, t-2, ..., t-N as features

    n_estimators = 100             # Number of boosted trees to fit. default = 100
    max_depth = 4                  # Maximum tree depth for base learners. default = 3
    learning_rate = 0.1            # Boosting learning rate (xgb’s “eta”). default = 0.1
    min_child_weight = 3           # Minimum sum of instance weight(hessian) needed in a child. default = 1
    subsample = 1                  # Subsample ratio of the training instance. default = 1
    colsample_bytree = 0.9          # Subsample ratio of columns when constructing each tree. default = 1
    colsample_bylevel = 1          # Subsample ratio of columns for each split, in each level. default = 1
    gamma = 0.1                      # Minimum loss reduction required to make a further partition on a leaf node of the tree. default=0
    objective='binary:logistic'
    model_seed = 100

    ############################
    # Create the model
    model = XGBClassifier(seed=model_seed,
                         objective = objective,
                         max_depth=max_depth,
                         learning_rate=learning_rate,
                         min_child_weight=min_child_weight,
                         subsample=subsample,
                         colsample_bytree=colsample_bytree,
                         colsample_bylevel=colsample_bylevel,
                         gamma=gamma,
                         tree_method='gpu_hist',
                         gpu_id=0,
                        verbosity=2)

    return model

def select_factors(x, model, threshold=0.8, method='xgb_importance', num=20):
    if method == 'xgb_importance':
        df_score = pd.DataFrame({'importance':list(model.feature_importances_), 'name':x.columns.tolist()})
        df_score.sort_values('importance', ascending=False, inplace=True)
    #如果规定了因子数量优先采用数量筛选
    if num:
        df_important = df_score.iloc[:20]
    else:
        df_important = df_score[df_score.importance >= df_score.importance.quantile(threshold)]
    selected_factors = df_important.name.tolist()
    return selected_factors

def get_IR(series):
    yieldRate = series.iat[-1]
    IR = yieldRate/series.std()
    return IR

def get_maxdraw(series):
    series += 1
    max_draw_down = 0
    temp_max_value = 0
    for i in range(1, len(series)):
        temp_max_value = max(temp_max_value, series.iat[i - 1])
        # temp_max_value=max(series[:i])
        max_draw_down = min(max_draw_down, (series.iat[i] / temp_max_value) - 1)
    return max_draw_down

def get_calmar(series):
    max_draw_down = get_maxdraw(series)
    calmar = (series.iat[-1] - 1) / max_draw_down
    return calmar

def group_share_calmar(df_item):
    df_item['rise_ratio'] = df_item.close.iloc[0]
    df_item.rise_ratio = df_item.close / df_item.rise_ratio - 1
    series = df_item.rise_ratio
    sharpe = get_IR(series)
    calmar = get_calmar(series)
    df_item.iloc[-1, -3] = sharpe
    df_item.iloc[-1, -2] = calmar
    return df_item

def factor_ret(df, Y):
    X = df.iloc[:, 0]
    rlm_model = sm.RLM(Y, X, M=sm.robust.norms.HuberT()).fit()
    factor_ret = rlm_model.params
    factor_ret = factor_ret.values[0]
    return factor_ret

def group_factor_ret(df, ret_type='normal'):
    Y = df.next_ret
    df = df[factor_cols]
    if ret_type == 'rank':
        df = df.rank(ascending=True, method='dense')
        df_ret = df.groupby(axis=1, level=0).apply(
            lambda x: sm.RLM(Y, x.iloc[:, 0], M=sm.robust.norms.HuberT()).fit().params.values[0])
    elif ret_type == 'normal':
         df_ret = df.groupby(axis=1, level=0).apply(
            lambda x: sm.RLM(Y, x.iloc[:, 0], M=sm.robust.norms.HuberT()).fit().params.values[0])
    return df_ret


if __name__ == '__main__':
    #from factor_stat import FactorRetStat

    df_factor = pd.read_csv(r'D:\work\ZNC\reinforced\test_data\df_factor_test.csv', index_col=['date', 'code'], parse_dates=['date'])
    # 非X列
    no_x_columns = ['codes', 'date', 'next_ret', 'bin', 'end_date', 'alpha', 'MKT_CAP_ASHARE', 'sharpe', 'calmar', 'IR']
    # 得到特征列
    factor_cols = list(df_factor.columns.difference(no_x_columns))
    
    df_factor.loc[:, factor_cols] = df_factor.loc[:, factor_cols].groupby(level=0).apply(lambda x:x.groupby(axis=1, level=0).apply(lambda y:filter_extreme_mad(y[y.columns[0]], 5)))    
    
    hxx = x_train.groupby(axis=1, level=0).apply(lambda df1: mutual_info_score(y_train, df1.iloc[:,0]))
    hxx.sort_values(inplace=True)
    # dates = df_factor.index.get_level_values('date').drop_duplicates()
    # df_factor.sort_index(inplace=True)
    # df_factor = df_factor.loc[:dates[-1]]
    # financial = FactorRetStat()
    # df_factor_ret = df_factor.groupby(level=0).apply(financial.group_factor_ret)
    # data = financial.data_concat(df_factor[factor_cols], df_factor_ret)

    # data.columns = map(lambda x:str(x), data.columns)
    # x = data[data.columns.difference(['Y'])]
    # y = data['Y'].apply(lambda x: 1 if x>0 else 0)
    # x_train, y_train, x_test, y_test = split_x_y(x, y)

    # model = get_model()
    # model.fit(x_train.values, y_train.values)
    # pred = model.predict(x_test.values)
    # pred_proba = model.predict_proba(x_test.values)[:, 1]
    # index_ = np.argwhere(pred_proba >= np.percentile(pred_proba, 80))#.reshape(1,-1).tolist()[0]
    # index_ = np.argwhere(pred == 1).reshape(1,-1).tolist()[0]
    # auc = roc_auc_score(y_test.values, pred)
    # acc = accuracy_score(y_test.values, pred)
    # select_factors = x_test.iloc[index_].index.get_level_values(1).tolist()

    #df_factor_ret = df.groupby(level=0).apply(group_factor_ret)
    #df_factor_basic  = df.reset_index().pivot(index='date', columns=df.columns)
    #df_factor_basic = df.groupby(level=0).apply(lambda x:x.transpose())
    # df_tmp = df.loc[dates[0]]#.transpose()
    # seri_next_ret = df_tmp.next_ret
    #
    # Y = df_tmp.next_ret
    # df_tmp = df_tmp[factor_cols]
    # seri_col_g = [df for i,df in df_tmp.groupby(axis=1, level=0)]
    # df_facter_test = seri_col_g[0]
    # df_facter_test.sort_values(df_facter_test.columns[0], ascending=False, inplace=True)

    #df_test2 = df_test.reset_index(col_level=0)

    #df_facter_test = df_facter_test.rank(ascending=True, method='dense')

    # X = df_facter_test.iloc[:, 0]#.rank(ascending=True, method='dense')
    # # df_facter_test = df_tmp.groupby(axis=1, level=0).apply(lambda x: x.rank(ascending=True, method='dense'))
    # # X = df_facter_test.drop(['end_date', 'next_ret'], axis=1)
    # rlm_model = sm.RLM(Y, X, M=sm.robust.norms.HuberT()).fit()
    # factor_ret = rlm_model.params


    # 计算IR
    # df_basic = pd.read_csv(r'D:\work\ZNC\reinforced\test_data/df_basic.csv',index_col=['date', 'code'], parse_dates=['date'])
    # df_benchmark = pd.read_csv(r'D:\work\ZNC\reinforced\test_data/df_benchmark.csv', index_col='date')
    #
    # df_basic = df_basic.loc[df_benchmark.index[0]:df_benchmark.index[-1]]
    #
    # df_list = [df for i,df in df_basic.groupby(level=1)]
    #
    # df_stk = df_list[0]
    #
    # dates = df_stk.index.get_level_values('date').drop_duplicates().astype(str).tolist()
    #
    # df_stk['rise_ratio'] = df_stk.close.iloc[0]
    # df_stk.rise_ratio = df_stk.close / df_stk.rise_ratio
    #
    # df_benchmark_tmp = df_benchmark[df_benchmark.index.isin(dates)]
    # df_benchmark_tmp['rise_ratio'] = df_benchmark_tmp.close/df_benchmark_tmp.close.iat[0]
    # seri_extra_yield = pd.Series(df_stk['rise_ratio'].values - df_benchmark_tmp['rise_ratio'].values)
    #
    # # IR = get_IR(seri_extra_yield)
    # calmar = get_calmar(seri_extra_yield)

    
    # df = pd.read_csv(r'D:\work\ZNC\reinforced\test_data\df_factor.csv', index_col=['date', 'code'])
    # df_y = pd.read_csv(r'D:\work\ZNC\reinforced\database\夏普calmar月度数据.csv', index_col=['date', 'code'])
    # df['sharpe'] = df_y['sharpe']
    # df['calmar'] =  df_y['calmar']
    # df.dropna(axis=0, inplace=True)
    # no_x_columns = ['codes', 'date', 'next_ret', 'bin', 'end_date', 'alpha', 'MKT_CAP_ASHARE']
    # factor_cols = df.columns.difference(no_x_columns)

    # x = df[factor_cols]
    # # df['bin_ret'] = df['next_ret'].apply(lambda x: 1 if x>0 else 0)
    # # df['bin_sharpe'] = df['sharpe'].apply(lambda x: 1 if x>0 else 0)
    # # df['bin_calmar'] = df['calmar'].apply(lambda x: 1 if x>0 else 0)
    
    
    # y_ret = df['next_ret'].apply(lambda x: 1 if x>0 else 0)
    # y_sharpe = df['sharpe'].apply(lambda x: 1 if x>0 else 0)
    # y_calmar = df['calmar'].apply(lambda x: 1 if x>0 else 0)


    # x_train, y_ret_train, x_test, y_ret_test = split_x_y(x, y_ret)
    # y_sharpe_train, y_calmar_train, y_sharpe_test, y_calmar_test = split_x_y(y_sharpe, y_calmar)
    

    #第一轮训练
    # from xgboost import plot_importance
    # model1 = get_model()
    # model1.fit(x_train, y_ret_train)
    # x1 = model1.predict_proba(x_train)[:, 1]
    # x1_test = model1.predict_proba(x_test)[:, 1]
    # y_pred1 = model1.predict(x_test)
    # auc1 = roc_auc_score(y_ret_test, y_pred1)

    # model2 = get_model()
    # model2.fit(x_train, y_sharpe_train)
    # x2 = model2.predict_proba(x_train)[:, 1]
    # x2_test = model2.predict_proba(x_test)[:, 1]
    # y_pred2 = model2.predict(x_test)
    # auc2 = roc_auc_score(y_ret_test, y_pred2)
    
    # model3 = get_model()
    # model3.fit(x_train, y_calmar_train)
    # x3 = model3.predict_proba(x_train)[:, 1]
    # x3_test = model3.predict_proba(x_test)[:, 1]
    # y_pred3 = model3.predict(x_test)
    # auc3 = roc_auc_score(y_ret_test, y_pred3)

    # x_train_final = np.r_[x1, x2, x3].reshape(-1,1)
    # y_train_final = np.r_[y_ret_train, y_sharpe_train, y_calmar_train].reshape(-1,1)
    # #x_train_final = np.array([x1, x2, x3])#.T
    # #y_train_final = np.array([y_ret_train, y_sharpe_train, y_calmar_train])
    # x_test_final = np.r_[x1_test, x2_test, x3_test]

    # ln_model = linear_model.LogisticRegression()
    # ln_model.fit(x_train_final, y_train_final)
    # y_pred = ln_model.predict(x_test_final)
    # auc = roc_auc_score(y_ret_test, y_pred)      
    
    # proba_sum = (x1_test + x2_test + x3_test) / 3
    # sum_flag = [1 if x>0.5 else 0 for x in proba_sum]
    # auc_sum = roc_auc_score(y_ret_test, sum_flag)


    # 算出隐藏层
    # input_dim = x.shape[1]
    # first_hidden_units = input_dim * 4
    # floor_num = 4
    # HiddenLayer = list(range(first_hidden_units, 0, -int(first_hidden_units / floor_num)))
    # HiddenDropout = [0.2] * len(HiddenLayer)   
    
    # model = auto_encoder(input_dim, HiddenLayer, HiddenDropout)
    # model.fit(x, x, epochs=30, batch_size=1024, verbose=True)

    # model.fit(x_train,y_train)
    #
    # # 使用模型预测
    # y_pred = model.predict(x_test)
    #
    # accuracy = accuracy_score(y_test, y_pred)
    # auc = roc_auc_score(y_test, y_pred)
    #
    # ### plot feature importance
    # # fig,ax = plt.subplots(figsize=(15,15))
    # #
    # # plot_importance(model,
    # #                 height=0.5,
    # #                 ax=ax,
    # #                 max_num_features=20)
    # # fig.show()
    #
    # #特征重要性筛选
    # selected_factors = select_factors(x_train, model, threshold=0.65, method='xgb_importance')
    # model.fit(x_train.loc[:,selected_factors], y_train)
    # # 使用模型预测
    # y_pred = model.predict(x_test.loc[:,selected_factors])
    # accuracy2 = accuracy_score(y_test, y_pred)
    # auc2 = roc_auc_score(y_test, y_pred)
    #
    # # #互信息筛选
    # # hxx = x_train.groupby(axis=1, level=0).apply(lambda df1: mutual_info_score(y_train, df1.iloc[:,0]))
    # # hxx.sort_values(inplace=True)
    # # selected_factors = hxx[hxx >= hxx.quantile(0.3)].index.tolist()
    # # model.fit(x_train.loc[:,selected_factors], y_train)
    # # # 使用模型预测
    # # y_pred = model.predict(x_test.loc[:,selected_factors])
    # # accuracy3 = accuracy_score(y_test, y_pred)
    # # auc3 = roc_auc_score(y_test, y_pred)
    #
    # # #train上面表现增强否
    # # y_pred = model.predict(x_train.loc[:,selected_factors])
    # # accuracy4 = accuracy_score(y_train, y_pred)
    # # auc4 = roc_auc_score(y_train, y_pred)