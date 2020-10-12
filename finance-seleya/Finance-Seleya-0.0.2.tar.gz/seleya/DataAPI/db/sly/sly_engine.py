from .. fetch_engine import FetchEngine
from .... config.default_config import DB_URL
from .... utilities.singleton import Singleton
from sqlalchemy import select, and_, outerjoin, join, column
import six,pdb
import numpy as np
import pandas as pd

@six.add_metaclass(Singleton)
class FetchSLYEngine(FetchEngine):
    def __init__(self):
        super(FetchSLYEngine, self).__init__('sly', DB_URL['sly'])
    
    def default_dates(self, table,  dates, 
                      time_name='trade_date', codes=None, key=None):
       
        return and_(table.__dict__[time_name].in_(dates),
                    table.flag == 1) if key is None else and_(table.__dict__[time_name].in_(dates),
                    table.flag == 1, table.__dict__[key].in_(codes)) 
    
    def default_notdates(self, table, begin_date, end_date, 
                         time_name='trade_date',
                         codes=None, key=None):
        return and_(table.__dict__[time_name] >= begin_date, 
                               table.__dict__[time_name] <= end_date,
                               table.flag == 1) if key is None else and_(table.__dict__[time_name] >= begin_date, 
                               table.__dict__[time_name] <= end_date,
                               table.flag == 1, table.__dict__[key].in_(codes))
    
    def gd_overview(self, codes, key=None, columns=None):
        table = self._base.classes['overview']
        return self.base_notime(table=table, codes=codes, key=key, 
                                columns=columns, clause_list=None)
    
    def gd_reviews(self, codes=None, key=None, begin_date=None, end_date=None, 
               columns=None, freq=None, dates=None):
        table = self._base.classes['reviews']
        if dates is not None:
            clause_list = self.default_dates(table=table, dates=dates, 
                                             codes=codes, key=key, 
                                             time_name='reviewDateTime') 
        else:
            clause_list = self.default_notdates(table=table, begin_date=begin_date, 
                                                end_date=end_date, codes=codes, key=key,
                                                time_name='reviewDateTime')
        return self.base(table=table, begin_date=begin_date, end_date=end_date, 
                         codes=codes, key=key, columns=columns, freq=freq, 
                         dates=dates, clause_list=clause_list,time_name='reviewDateTime')