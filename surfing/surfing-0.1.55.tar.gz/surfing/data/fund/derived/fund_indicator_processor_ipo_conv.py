
import pandas as pd
import numpy as np
import datetime
import traceback
from functools import partial
from sklearn.metrics import r2_score
import concurrent.futures
from multiprocessing import Pool
from ...manager.manager_fund import FundDataManager
from ...manager.score import FundScoreManager
from ...wrapper.mysql import DerivedDatabaseConnector
from ...view.derived_models import FundIndicatorIPOConv
from .derived_data_helper import DerivedDataHelper
from ...api.basic import BasicDataApi

class FundIndicatorProcessorIPOConv(object):

    TRADING_DAYS_PER_YEAR = 242
    NATURAL_DAYS_PER_YEAR = 365
    MIN_TIME_SPAN = int(TRADING_DAYS_PER_YEAR / 4)#为了延长基金回测范围，评分最低年限3个月
    RISK_FEE_RATE = 0.025
    RISK_FEE_RATE_PER_DAY = RISK_FEE_RATE / TRADING_DAYS_PER_YEAR

    def __init__(self, data_helper):
        self._data_helper = data_helper
        self._basic_data_api = BasicDataApi()

    def init(self, start_date='20040101', end_date='20200630', dm=None):
        if dm is None:
            self._dm = FundDataManager(start_time='20200601', end_time='20200630', score_manager=FundScoreManager())
            self._dm.init(score_pre_calc=False)
        else:
            self._dm = dm    
        
        self.start_date = datetime.datetime.strptime(start_date, '%Y%m%d').date()
        self.end_date = datetime.datetime.strptime(end_date, '%Y%m%d').date()
        self.fund_info = self._dm.dts.fund_info
        self.fund_list = self._dm.dts.fund_ipo_list.union(self._dm.dts.fund_conv_list)
        self.fund_nav = self._basic_data_api.get_fund_nav_with_date(self.start_date, self.end_date, self.fund_list)
        self.index_price = self._basic_data_api.get_index_price(['national_debt'])
        self.trading_day = self._basic_data_api.get_trading_day_list()

        self.fund_nav = self.fund_nav.pivot_table(index='datetime', columns='fund_id', values='adjusted_net_value').dropna(axis=1, how='all').fillna(method='ffill')
        self.trading_day = self.trading_day.set_index('datetime').loc[self.start_date:self.end_date].index.tolist()
        self.fund_nav = self.fund_nav.reindex(self.trading_day)
        self.index_price = self.index_price.pivot_table(index='datetime', columns='index_id', values='close').dropna(axis=1, how='all').fillna(method='ffill')
        self.index_price = self.index_price.reindex(self.trading_day)

        fund_to_enddate_dict = self.fund_info[['fund_id', 'end_date']].set_index('fund_id').to_dict()['end_date']
        self.fund_to_index_dict = self.fund_info[['fund_id', 'index_id']].set_index('fund_id').to_dict()['index_id']
        # 超过基金终止日的基金净值赋空
        for fund_id in self.fund_nav.columns:
            fund_end_date = fund_to_enddate_dict[fund_id]
            if self.end_date > fund_end_date:
                self.fund_nav.loc[fund_end_date:,fund_id] = np.nan

        self.fund_ret = np.log(self.fund_nav / self.fund_nav.shift(1))
        self.fund_ret = self.fund_ret.stack().reset_index(level=[0,1]).rename(columns={0:'ret'})
        self.fund_ret = self.fund_ret.pivot_table(index='datetime',columns='fund_id',values='ret')    

        self.index_ret = np.log(self.index_price / self.index_price.shift(1))
        self.fund_to_index_dict = {fund_id:index_id for fund_id,index_id in self.fund_to_index_dict.items() if fund_id in self.fund_ret.columns}
        self.index_list = self.fund_info.index_id.dropna().unique().tolist()
        self.index_fund = { index_id : [fund_idx for fund_idx, index_idx in self.fund_to_index_dict.items() if index_idx == index_id] for index_id in self.index_list}
        self.start_date_dic = self.fund_info[['fund_id','start_date']].set_index('fund_id').to_dict()['start_date']

    def _rolling_alpha_beta_time_ret_r2(self, x, res, df):
        # 回归相关的都在这里
        df_i = df.loc[x[0]:x[-1],]
        return self._rolling_alpha_beta_time_ret_r2_base(res,df_i)

    def _rolling_alpha_beta_time_ret_r2_base(self, res, df_i):
        if sum(df_i.fund) == 0:
            res.append({'alpha':np.Inf,'beta':np.Inf,'time_ret':np.Inf})
            return 1
        else:
            ploy_res = np.polyfit(y=df_i.fund, x=df_i.benchmark,deg=1)
            p = np.poly1d(ploy_res)
            r2 = r2_score(df_i.fund, p(df_i.benchmark))
            beta = ploy_res[0]
            alpha = ploy_res[1] * self.TRADING_DAYS_PER_YEAR
            day_len = df_i.shape[0]
            bar_num = int( day_len / self.MIN_TIME_SPAN)

            _res = []
            for i in range(bar_num):
                start_i = - (i + 1) * self.MIN_TIME_SPAN
                end_i = - i * self.MIN_TIME_SPAN
                if end_i == 0:
                    dftmp = df_i.iloc[start_i:]
                else:
                    dftmp = df_i.iloc[start_i:end_i]
                _ploy_res = np.polyfit(y=dftmp.fund, x=dftmp.benchmark,deg=1)
                
                _res.append({'beta_i_no_whole_beta': _ploy_res[0] - beta,
                            'bench_r_no_risk': dftmp.benchmark.sum() - self.RISK_FEE_RATE_PER_DAY * day_len })
            time_ret = np.sum([ _['beta_i_no_whole_beta'] * _['bench_r_no_risk'] for _ in _res])
            res.append({'alpha': alpha, 
                        'beta': beta,
                        'time_ret':time_ret,
                        'r_square':r2})
            return 1

    def _rolling_mdd(self, x):
        x = pd.Series(x)
        return 1 - (x / x.cummax()).min()

    def _rolling_annual_ret(self, x):
        x = pd.Series(x).dropna()
        year = x.shape[0] / self.TRADING_DAYS_PER_YEAR
        return np.exp(np.log(x.values[-1]/x.values[0])/year) - 1

    def _process_fund_indicator_one(self, time_range, fund_ret, index_id, index_ret, fund_id):
        df = fund_ret[[fund_id]].join(index_ret).dropna()
        df = df.rename(columns={index_id:'benchmark',fund_id:'fund'}).reset_index()
        df['year_length'] = df['datetime'].map(lambda x: (x-self.start_date_dic[fund_id]).days / self.NATURAL_DAYS_PER_YEAR)
        res = []
        pd.Series(df.index).rolling(
            window=time_range,min_periods=self.MIN_TIME_SPAN).apply(
                partial(self._rolling_alpha_beta_time_ret_r2, res=res, df=df), raw=True)
        df = df.set_index('datetime')
        df = df.join(pd.DataFrame(res,index=df.index[-len(res):]))
        if 'alpha' not in df.columns:
            return None
        df['track_err'] = (df.fund - df.benchmark).rolling(window=time_range, min_periods=self.MIN_TIME_SPAN).std(ddof=1)* np.sqrt(self.TRADING_DAYS_PER_YEAR)
        df['fund_id'] = fund_id
        df['timespan'] = int(time_range / self.TRADING_DAYS_PER_YEAR)
        df['fee_rate'] = self.fund_fee[fund_id]
        df['info_ratio'] = df.alpha / df.track_err
        df['mean_ret'] = df[['fund']].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean()
        df['mean_ret_no_free_ret'] = df['mean_ret'] - self.RISK_FEE_RATE_PER_DAY
        df['treynor'] = df['mean_ret_no_free_ret'] * time_range / df.beta
        df['mdd'] = self.fund_nav[[fund_id]].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).apply(self._rolling_mdd, raw=True)
        df['down_risk'] = np.abs(np.minimum(df['fund'] - self.RISK_FEE_RATE_PER_DAY, 0))
        df['down_risk'] = df['down_risk'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean()* np.sqrt(self.TRADING_DAYS_PER_YEAR)
        df['ret_over_period'] = self.fund_nav[[fund_id]] / self.fund_nav[[fund_id]].fillna(method='bfill').shift(time_range) - 1
        df['annual_avg_daily_ret'] = df['fund'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean() * self.TRADING_DAYS_PER_YEAR 
        df['annual_ret'] = self.fund_nav[[fund_id]].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).apply(self._rolling_annual_ret, raw=True)
        df['annual_vol'] = df['fund'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        df['vol_benchmark'] = df['benchmark'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        df['mean_ret_benchmark'] = df[['benchmark']].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).mean()
        df['m_square'] = df['vol_benchmark'] / df['annual_vol'] * df['mean_ret_no_free_ret'] + self.RISK_FEE_RATE_PER_DAY - df['mean_ret_benchmark']
        df['var'] = df['fund'].rolling(window=time_range,min_periods=self.MIN_TIME_SPAN).quantile(0.05)
        df['var'] = np.minimum(df['var'], 0) * -1
        df['sharpe'] = (df.annual_ret - self.RISK_FEE_RATE) / df.annual_vol
        df = df.drop(['fund','benchmark','vol_benchmark','mean_ret_no_free_ret','mean_ret_benchmark','mean_ret'], axis=1)
        # build history insert
        df = df.replace({-np.Inf:None,np.Inf:None}).dropna(subset=['beta', 'alpha','track_err']).reset_index()
        #self._data_helper._upload_derived(df, FundIndicatorDev.__table__.name)
        return df

    def _process_fund_indicator_update(self, fund_id, time_range, fund_ret, index_id, index_ret):
        df = fund_ret[[fund_id]].join(index_ret).dropna()
        df = df.rename(columns={index_id:'benchmark',fund_id:'fund'}).reset_index()
        last_day = df.datetime.values[-1]
        year_length = (last_day-self.start_date_dic[fund_id]).days / self.NATURAL_DAYS_PER_YEAR
        df = df.iloc[-time_range:].dropna()
        if df.shape[0] < self.MIN_TIME_SPAN:
            return None
        res = []
        self._rolling_alpha_beta_time_ret_r2_base(res, df)
        fund_indicator_part1 = res[0]
        if fund_indicator_part1['alpha'] in [np.Inf, -np.Inf]:
            return None
        track_err = (df.fund - df.benchmark).std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        timespan = int(time_range / self.TRADING_DAYS_PER_YEAR)
        fee_rate = self.fund_fee[fund_id]
        info_ratio = fund_indicator_part1['alpha'] / track_err
        mean_ret = df.fund.mean()
        mean_ret_no_free_ret = mean_ret - self.RISK_FEE_RATE_PER_DAY
        treynor = mean_ret_no_free_ret * time_range / fund_indicator_part1['beta']
        if self.fund_nav[[fund_id]][-time_range:].dropna().shape[0] < self.MIN_TIME_SPAN:
            return None
        mdd = self.fund_nav[[fund_id]][-time_range:].apply(self._rolling_mdd, raw=True).values[0]
        down_risk = np.abs(np.minimum(df['fund'] - self.RISK_FEE_RATE_PER_DAY, 0)).mean()* np.sqrt(self.TRADING_DAYS_PER_YEAR)
        ret_over_period = self.fund_nav[fund_id][-1] / self.fund_nav[fund_id].fillna(method='bfill')[-time_range-1] - 1
        annual_avg_daily_ret = df['fund'].mean() * self.TRADING_DAYS_PER_YEAR 
        annual_ret = self.fund_nav[[fund_id]][-time_range:].apply(self._rolling_annual_ret, raw=True)[0]
        annual_vol = df['fund'].std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        vol_benchmark = df['benchmark'].std(ddof=1) * np.sqrt(self.TRADING_DAYS_PER_YEAR)
        mean_ret_benchmark = df['benchmark'].mean()
        m_square = vol_benchmark / annual_vol * mean_ret_no_free_ret + self.RISK_FEE_RATE_PER_DAY - mean_ret_benchmark
        var = np.minimum(df['fund'].quantile(0.05), 0) * -1
        sharpe = (annual_ret - self.RISK_FEE_RATE) / annual_vol
        dic = {
            'fund_id':fund_id,
            'datetime':last_day,
            'beta':fund_indicator_part1['beta'],
            'alpha':fund_indicator_part1['alpha'],
            'time_ret':fund_indicator_part1['time_ret'],
            'r_square':fund_indicator_part1['r_square'],
            'track_err':track_err,
            'timespan':timespan,
            'fee_rate':fee_rate,
            'info_ratio':info_ratio,
            'treynor':treynor,
            'mdd':mdd,
            'down_risk':down_risk,
            'ret_over_period':ret_over_period,
            'annual_avg_daily_ret':annual_avg_daily_ret,
            'annual_ret':annual_ret,
            'annual_vol':annual_vol,
            'm_square':m_square,
            'var':var,
            'sharpe':sharpe,
            'year_length':year_length}
        return dic
    
    def calculate_history(self):
        self.fund_fee = self.fund_info[['fund_id','manage_fee','trustee_fee']].set_index('fund_id').fillna(0).sum(axis = 1)
        index_id = 'national_debt'
        time_range = self.TRADING_DAYS_PER_YEAR
        fund_ret = self.fund_ret.copy()
        fund_list = self.fund_ret.columns.tolist()
        index_ret = self.index_ret[[index_id]]
        p = Pool()
        res = [i for i in p.imap_unordered(partial(self._process_fund_indicator_one, time_range, fund_ret, index_id, index_ret), fund_list, 256) if i is not None]
        p.close()
        p.join()
        self.result = pd.concat(res, axis=0, sort=True)
        self._data_helper._upload_derived(self.result, FundIndicatorIPOConv.__table__.name)

    def calculate_update(self):
        self.fund_fee = self.fund_info[['fund_id','manage_fee','trustee_fee']].set_index('fund_id').fillna(0).sum(axis = 1)
        index_id = 'national_debt'
        time_range = self.TRADING_DAYS_PER_YEAR
        fund_ret = self.fund_ret.copy()
        fund_list = self.fund_ret.columns.tolist()
        index_ret = self.index_ret[[index_id]]
        result = []
        for fund_id in fund_list:
            result.append(self._process_fund_indicator_update(fund_id, time_range, fund_ret, index_id, index_ret))
        result = [ _ for _ in result if not _ is None]
        self.result = pd.DataFrame(result)
        self.result = self.result.replace({-np.Inf:None,np.Inf:None}).dropna(subset=['beta', 'alpha','track_err'])

    def process(self, start_date, end_date):
        failed_tasks = []
        try:
            start_date_dt = datetime.datetime.strptime(start_date, '%Y%m%d').date()
            end_date_dt = datetime.datetime.strptime(end_date, '%Y%m%d').date()

            start_date = start_date_dt - datetime.timedelta(days = 1150) #3年历史保险起见，多取几天 3*365=1095 
            start_date = datetime.datetime.strftime(start_date, '%Y%m%d')

            self.init(start_date=start_date, end_date=end_date)
            self.calculate_update()
            df = self.result[self.result['datetime'] == end_date_dt]
            self._data_helper._upload_derived(df, FundIndicatorIPOConv.__table__.name)
        except Exception as e:
            print(e)
            traceback.print_exc()
            failed_tasks.append('fund_indicator_ipo_conv')

        return failed_tasks