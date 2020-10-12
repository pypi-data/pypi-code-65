# -*- coding: utf-8 -*-

class EngineFactory():
    def create_engine(self, engine_class):
        return engine_class()
    
    def __init__(self, engine_class):
        self._fetch_engine = self.create_engine(engine_class)
        
        
class GDOveriewFactory(EngineFactory):
    def result(self, codes, key=None, columns=None):
        return self._fetch_engine.gd_overview(codes=codes, key=key, 
                                              columns=columns)

class GDReviews(EngineFactory):
    def result(self, codes, key=None, begin_date=None, end_date=None,
               columns=None, freq=None,dates=None):
        return self._fetch_engine.gd_reviews(codes=codes, key=key, begin_date=begin_date, 
                                           end_date=end_date, columns=columns, freq=freq, 
                                           dates=dates)