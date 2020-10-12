#Import required Python libraries
import pandas as pd
import numpy as np
import snowflake.connector
import datetime as dt
from datetime import timedelta
import matplotlib.pyplot as plt
from IPython.display import clear_output
import os
import sys
sys.path.append("..")
pd.options.display.float_format = '{:.2f}'.format
from datetime import datetime, timedelta
import snowflake.connector
from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine

conn = snowflake.connector.connect(
                user='XXXXX',
                password='XXXXXXXX$',
                account='zxventureseu.eu-central-1',
                database='ECOMMERCE',
                schema='UK_BEER_HAWK')

business = 'BeerHawk'
store = "uk_co_beerhawk" if business == 'BeerHawk' else         \
    ('com_emporio' if business == 'Emporio' else
     ('interdrinks' if business == 'Interdrinks' else
      ('ar_bevybar' if business == 'CraftSociety' else
       ('cl_casadelacerveza' if business == 'CasadelaCerveza' else
        ('mx_beerhouse' if business == 'BeerHouse' else
         ('uk_atom' if business == 'Atom' else 'courier_ze'))))))

raw_path = 'C:/Users/40100204/Desktop/ZX/Core/BeerHawk behavioural clusters/'

DATE_ = datetime.now().date() - timedelta(1)

path = raw_path + 'Datasets/{}_Orders_BS_{}.csv'.format(business, DATE_)

def raw_orders():
    """
    read the transaction data
    """
    path = raw_path + 'Datasets/{}_Orders_BS_{}.csv'.format(business, DATE_)
    if not os.path.isfile(path):
        raw_orders = pd.read_sql_query("""
        SELECT ORDER_SPK, ORDER_AK, BUSINESS_SPK, BUSINESS_NAME,
        ITEM_SKU, ITEM_NAME, PRODUCT_SPK, ORDER_DATE, ORDER_TIME, CUSTOMER_SPK, CURRENCY, UNIT_QUANTITY, 
        EXTENDED_UNIT_QUANTITY1, EXTENDED_UNIT_QUANTITY2, 
        UNIT_NET_REVENUE_LOCAL, UNIT_GROSS_REVENUE_LOCAL, UNIT_DISCOUNT_TAX_EXCL_USD,
        DISCOUNT_NAME, COUPON_CODE, ORDER_STATUS, ORDER_STATUS_TYPE, 
        ORDER_DAYS_AFTER_FIRST_ORDER, IS_FIRST_ORDER
        FROM ECOMMERCE.UK_BEER_HAWK.VW_FACT_ORDER_DETAILS
        WHERE ORDER_DATE>='2020-01-01';
        """, conn)

        if len(raw_orders) > 0:
            raw_orders.to_csv(path, index=False)
    else:
        raw_orders = pd.read_csv(path)

    path = raw_path + 'Datasets/{}_Sessions_BS_{}.csv'.format(business, DATE_)

    # print (raw_orders.head())
    return raw_orders

def raw_sessions():
    path = raw_path + 'Datasets/{}_Sessions_BS_{}.csv'.format(business, DATE_)

    if not os.path.isfile(path):
        raw_sessions = pd.read_sql_query("""
        SELECT ORDER_AK, USERTYPE, "SOURCE", MEDIUM, 
        KEYWORD, DEVICECATEGORY, REGION, CITY 
        FROM ECOMMERCE.UK_BEER_HAWK.VW_GA_TRANSACTIONS;
        """, conn)

        if len(raw_sessions) > 0:
            raw_sessions.to_csv(path, index=False)
    else:
        raw_sessions = pd.read_csv(path)

    raw_sessions.ORDER_AK = raw_sessions['ORDER_AK'].astype(str)
    # print(raw_sessions.head())

    return raw_sessions

def move_output_to_snowflake(df_to_move, table_name):

    #Establish Connection to GDW
    engine = create_engine(URL(
        account = 'zxventureseu.eu-central-1',
        user = 'XXXXX',
        password = 'XXXXX',
        database = 'ECOMMERCE',
        schema = 'UK_BEER_HAWK',
        warehouse = 'WH_WORKLOAD'
    ))
    connection = engine.connect()
    
    df_to_move.to_sql(table_name , engine, if_exists='replace', index=False, index_label=None, chunksize=15000)    