#!/usr/bin/env python
# coding: utf-8

# #### Misc.

# In[1]:


def make_names(string):
    clean_string = string.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    return(clean_string)


# #### Kmeans Automation

# In[2]:


def find_optimal_kmeans_label(b_id, df, col_names):
    print(b_id)
#     print(df)
    dt = df[col_names].copy()
#     print(dt)
    no_unique_depth = len(dt['duration'].unique())
    
    int_cols = np.sum(np.logical_or(dt.dtypes == np.int64 ,dt.dtypes == np.float64))
    tot_rows,tot_cols = dt.shape
    
    if(int_cols != tot_cols):
        raise ValueError('use only numeric fields.')

    if(no_unique_depth == 1):
#         print('inside')
        dt.drop(['duration'], axis = 1, inplace= True)
    
#     print(dt)
    # standardization (z-score)
    dt_norm = scale(dt)
    
    # find optimal k
    k_optimal = find_optimal_k(dt_norm)
    print(k_optimal)
    
    k_means_model = KMeans(n_clusters=k_optimal).fit(dt_norm)
    
    #add level to original dt
    df['k_means_label'] = k_means_model.labels_
    return(df)


# In[3]:


def find_optimal_k(norm_df):    
    dist_points_from_cluster_center = []
    K = range(1,10)
    for no_of_clusters in K:
        k_model = KMeans(n_clusters=no_of_clusters)
        k_model.fit(norm_df)
        dist_points_from_cluster_center.append(k_model.inertia_)
  
    a = dist_points_from_cluster_center[0] - dist_points_from_cluster_center[8]
    b = K[8] - K[0]
    c1 = K[0] * dist_points_from_cluster_center[8]
    c2 = K[8] * dist_points_from_cluster_center[0]
    c = c1 - c2
  
  
    distance_of_points_from_line = []
    for k in range(9):
        distance_of_points_from_line.append(calc_distance(K[k], dist_points_from_cluster_center[k], a, b, c))
  
    optimial_k = distance_of_points_from_line.index(max(distance_of_points_from_line)) + 1 
  
    return(optimial_k)


# In[4]:


# Function to find distance
# https://www.geeksforgeeks.org/perpendicular-distance-
# between-a-point-and-a-line-in-2-d/
def calc_distance(x1, y1, a, b, c):
    d = abs((a * x1 + b * y1 + c)) / (math.sqrt(a * a + b * b))
    return d


# #### Anomaly detection: Automated

# In[5]:


def scale_numeric_data(df, col_names):
    dt = df[col_names]
    # normalization
    x = scale(dt)
    return(x)


# In[6]:


def detect_outlier(b_id, enable_grid_search = False):
    print("business_id: {}, time_stamp: {}".format(b_id, datetime.now()))
    
    x = bp_scaled_data_dict.get(b_id)
    # tune grid
    tuneGrid = {'n_estimators':[70,80], 'max_samples':['auto'],
     'contamination':[0.05,0.1], 'max_features':[1],
     'bootstrap':[True],
     'random_state':[42], 'warm_start':[True]}
    
    if(enable_grid_search):
        isolation_forest = GridSearchCV(IsolationForest(), tuneGrid, scoring=scorer_f)
        isolation_forest.fit(x)
        best_param = isolation_forest.best_params_
        # print best param
        print('best_param= {}'.format(best_param))
        return(best_param, isolation_forest)
    else:
        best_param = iForest_tune_grid_dict.get(b_id)
        isolation_forest = IsolationForest(**best_param)
        isolation_forest.fit(x)
        # print best param
        print('best_param= {}'.format(isolation_forest.get_params()))
        return(best_param, isolation_forest)
    
    
#     df['outlier_flag'] = isolation_forest.predict(x)


# In[7]:


# def detect_outlier(b_id, df, col_names):
#     print("business_id: {}, time_stamp: {}".format(b_id, datetime.now()))
#     dt = df[col_names]
#     # normalization
#     x = scale(dt)
    
#     # tune grid
#     tuneGrid = {'n_estimators':[70,80], 'max_samples':['auto'],
#      'contamination':[0.05,0.1], 'max_features':[1],
#      'bootstrap':[True], 'n_jobs':[None,1,2],
#      'random_state':[None,1,], 'warm_start':[True]}
    
#     isolation_forest = GridSearchCV(IsolationForest(), tuneGrid, scoring=scorer_f)
#     model = isolation_forest.fit(x)
#     # print best param
#     print('best_param= {}'.format(isolation_forest.best_params_))
#     df['outlier_flag'] = model.predict(x)
#     return df


# In[8]:


def scorer_f(estimator, X):   #your own scorer
          return np.mean(estimator.score_samples(X))


# #### Modelling

# In[9]:


# Response Transformation function
def func(x):
    return np.log(x)
def inverse_func(x):
    return np.exp(x)


# In[10]:


def pre_process(column_to_process = ["depth_perc","bl_sales_vol"]):
    # Preprocessing
    columns_to_encode = ["cluster"]
    columns_to_scale = column_to_process
    encoder = OneHotEncoder(handle_unknown='ignore')
    scaler = StandardScaler()
    preproc = ColumnTransformer(
        transformers=[
            ("encoder", Pipeline([("OneHotEncoder", encoder)]), columns_to_encode),
            ("scaler", Pipeline([("StandardScaler", scaler)]), columns_to_scale)
        ]
    )
    
    return(preproc)


# In[11]:


def ols_fit_pipe(business_id, df):
    # track time
    print("business_id= {}, time_stamp= {}".format(business_id, datetime.now()))
    
    preproc = pre_process()
    # Model
    # Linear Forest Regressor
    myLMRegressor = LinearRegression()

    myTransformedLMRegressor = TransformedTargetRegressor(regressor=myLMRegressor,
                                      func=func,
                                      inverse_func=inverse_func)

    pipeline_list = [
        ('preproc', preproc),
        ('clf', myTransformedLMRegressor)
    ]

    pipe = Pipeline(pipeline_list, verbose= True)
    
    # LM fit
    X = df.drop(columns=["sales_vol"])
    y = df["sales_vol"]
#     pipe_dict[business_id].fit(X,y)
    print(X.columns)
    return(pipe.fit(X,y))
    


# In[12]:


# def rf_fit_pipe(business_id, df, enable_grid_search = False):
#     # track time
#     print("business_id= {}, time_stamp= {}".format(business_id, datetime.now()))
    
#     # pre process
#     preproc = pre_process()
    
#     # Model    
#     # tune grid
#     tune_grid = {'n_estimators':[300,350,400,450,500], 'max_depth':[6,8,10],
#      'min_samples_split':[4,6,8], 'max_features':['auto','sqrt'],
#      'bootstrap':[True], 'oob_score':[True], 'random_state':[42]}
    
#     # initialize
#     best_param = {}
        
#     if(enable_grid_search):
#         # Grid Search rf
#         myRFRegressor = GridSearchCV(RandomForestRegressor(), tune_grid, refit = True, scoring = 'r2')
#     else: 
#         # best param
#         best_param = rf_tune_grid_dict.get(business_id)
#         myRFRegressor = RandomForestRegressor(**best_param)
    
    
#     # response transformation
#     myTransformedRFRegressor = TransformedTargetRegressor(regressor=myRFRegressor,
#                                       func=func,
#                                       inverse_func=inverse_func)
#     # pipeline
#     pipeline_list = [
#         ('preproc', preproc),
#         ('clf', myTransformedRFRegressor)
#     ]

#     pipe = Pipeline(pipeline_list, verbose= True)
    
#     # RF fit
#     X = df.drop(columns=["sales_vol"])
#     y = df["sales_vol"]
#     pipe.fit(X,y)
    
#     # get best param
#     if(enable_grid_search):
#         best_param = myTransformedRFRegressor.regressor_.best_params_
    
#     #print best param
#     print('best_param= {}'.format(best_param))
    
#     return(best_param, pipe)    


# In[13]:


def rf_fit_pipe(business_id, df, enable_grid_search = False):
    # track time
    print("business_id= {}, time_stamp= {}".format(business_id, datetime.now()))
    
    # pre process
    preproc = pre_process()
    
    # Model    
    # tune grid
    tune_grid = {'n_estimators':[300,350,400,450,500], 'max_depth':[6,8,10],
     'min_samples_split':[4,6,8], 'max_features':['auto','sqrt'],
     'bootstrap':[True], 'oob_score':[True], 'random_state':[42]}
    
    # initialize
    best_param = {}
        
    if(enable_grid_search):
        # Grid Search rf
        myRFRegressor = GridSearchCV(RandomForestRegressor(), tune_grid, refit = True, scoring = 'r2')
    else: 
        # best param
        best_param = rf_tune_grid_dict.get(business_id)
        myRFRegressor = RandomForestRegressor(**best_param)
    
    # pipeline
    pipeline_list = [
        ('preproc', preproc),
        ('clf', myRFRegressor)
    ]

    pipe = Pipeline(pipeline_list, verbose= True)
    
    # response transformation
    rf_model = TransformedTargetRegressor(regressor=pipe,
                                      func=func,
                                      inverse_func=inverse_func)
    
    
    # RF fit
    X = df.drop(columns=["sales_vol"])
    y = df["sales_vol"]
    rf_model.fit(X,y)
    
    # get best param
    if(enable_grid_search):
        best_param = myTransformedRFRegressor.regressor_.best_params_
    
    print('best_param= {}'.format(best_param))
    
    return(best_param, rf_model)    


# In[14]:


def lgb_fit_pipe(business_id, df):
    # track time
    print("business_id= {}, time_stamp= {}".format(business_id, datetime.now()))
    
    preproc = pre_process()
    # Model
    # LightGBM Regressor
    myLightGBMRegressor = LGBMRegressor(objective='regression', 
                             learning_rate=0.01, 
                             n_estimators=500,
                             max_bin=200, 
                             bagging_fraction=0.8)

    myTransformedLightGBMRegressor = TransformedTargetRegressor(regressor=myLightGBMRegressor,
                                      func=func,
                                      inverse_func=inverse_func)

    pipeline_list = [
        ('preproc', preproc),
        ('clf', myTransformedLightGBMRegressor)
    ]

    pipe = Pipeline(pipeline_list, verbose= True)
    
    # LightGBM fit
    X = df.drop(columns=["sales_vol"])
    y = df["sales_vol"]
#     pipe_dict[business_id].fit(X,y)
    print(X.columns)
    return(pipe.fit(X,y))


# In[15]:


def mean_absolute_percentage_error(y_true, y_pred): 
    y_true, y_pred = np.array(y_true), np.array(y_pred)
    return np.mean(np.abs((y_true - y_pred) / y_true)) * 100


# In[16]:


# def build_sample(key,cluster, bl_sales_vol,depth_perc):
#     """build dataframe with data available at business_id, moc, cluster level"""
#     print('key:{}, cluster:{}, bl_sales_vol:{}, depth_perc:{}'.format(key, cluster, bl_sales_vol, depth_perc))
# #     print('TYPE = key:{}, cluster:{}, bl_sales_vol:{}, depth_perc:{}'.format(type(key), type(cluster), type(bl_sales_vol),
# #                                                                             type(depth_perc)))
#     r = bl_sales_vol.shape
#     if(r[0]==0):
#         print('F*ck!')
#         bl_sales_vol = 0.0
#     sample = pd.DataFrame({
#         'cluster' : [cluster],
#         'bl_sales_vol': [bl_sales_vol] if isinstance(bl_sales_vol,(int, float)) else bl_sales_vol,
#         'depth_perc' : [depth_perc]
#     }) 
# #     print(sample)
#     return sample


# #### Model Insights

# In[17]:


# prep variable for feature_imp
def def_feat_imp_vars(df, cols = ['depth_perc','bl_sales_vol','cluster']):
    temp_df = df[cols]
    num_X = temp_df.select_dtypes(include = [np.number])
    cat_X = temp_df.select_dtypes(include = ['object'])
    # ohe
    enc = OneHotEncoder(handle_unknown='ignore')
    enc_op_arr = enc.fit_transform(cat_X).toarray()
    ohe_cat_X = pd.DataFrame(enc_op_arr, columns = enc.get_feature_names())
    
    # scale
    scalar = StandardScaler()
    scalar_op_arr = scalar.fit_transform(num_X)
    scalar_num_X = pd.DataFrame(scalar_op_arr, columns = num_X.columns)
    
    transformed_df = pd.concat([scalar_num_X, ohe_cat_X], axis = 1)
    return(transformed_df) 


# In[18]:


def get_feat_imp(basepack):
    # track time
    print("business_id= {}, time_stamp= {}".format(basepack, datetime.now()))
    
    # train data set
    tr_df = df_basepack_dict.get(basepack).copy()
    tr_X = def_feat_imp_vars(tr_df)
    tr_y = tr_df["sales_vol"]
    
    # val data set
    val_df = df_basepack_dict_te.get(basepack)
    val_X = def_feat_imp_vars(val_df)
    val_y = val_df['sales_vol']
    
    # fit regressor
    best_param = rf_tune_grid_dict.get(basepack)
    rf = RandomForestRegressor(**best_param)
    rf_fit = rf.fit(tr_X, tr_y)   
  
    
#     # permutation imp or feat imp
#     perm_imp = PermutationImportance(rf_fit, random_state = 1).fit(val_X, val_y)
    
#     # store weights to html
#     html_file = eli5.show_weights(perm_imp, feature_names = val_X.columns.tolist())
    
#     # Write HTML String to file.html
#     file_path = business_id_path.get(basepack)
# #     abs_file_path = os.path.abspath(file_path)
#     file_name = file_path + '/' + basepack + '_feat_imp.html'
#     with open(file_name, "w") as file:
#         file.write(html_file.data)
        
    # write to excel
    file_path = business_id_path.get(basepack)
    excel_file_name = file_path + '/' + basepack + '_feat_imp.xlsx'
#     feat_imp_df = pd.DataFrame(perm_imp.feature_importances_,index = val_X.columns, columns=['Weight']).reset_index()
    feat_imp_df = pd.DataFrame(rf_fit.feature_importances_,index = tr_X.columns, columns=['Weight']).reset_index()
    feat_imp_df.rename(columns = {'index':'Feature'}).sort_values('Weight',ascending = False).to_excel(excel_file_name, index = False)


# #### Optimizer

# In[19]:


def build_sample(cluster, bl_sales_vol,depth_perc):
    """build dataframe with data available at business_id, moc, cluster level"""
#     print(type(bl_sales_vol))
    sample = pd.DataFrame({
        'cluster' : [cluster],
        'bl_sales_vol': [bl_sales_vol] if isinstance(bl_sales_vol,(int, float)) else bl_sales_vol,
        'depth_perc' : [depth_perc]
    }) 
#     print(sample)
    return sample


# In[20]:


def extract_dict_str(param_list):
    param_string = str(param_list)
    str_len = len(param_string)
    start_index = 2
    end_index = str_len - 2
    return param_string[start_index:end_index]

