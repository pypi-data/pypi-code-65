import pandas as pd
import numpy as np
import scipy.stats as stats


import bluebelt.datetime.dt

import bluebelt.statistics.standard_deviation

import bluebelt.analysis.patterns
import bluebelt.analysis.hypothesis_testing

import bluebelt.analysis.ppa

from bluebelt.helpers.exceptions import *


@pd.api.extensions.register_series_accessor('blue')
class SeriesToolkit():
    def __init__(self, pandas_obj):
        self._obj = pandas_obj
        self.dt = self.dt(self._obj)
        self.std = self.std(self._obj)
        self.patterns = self.patterns(self._obj)
        self.test = self.test(self._obj)
        self.ppa = self.ppa(self._obj)
        

    
    class dt():
        def __init__(self, pandas_obj):
            self._obj = pandas_obj
                
        # bluebelt.datetime.dt
        def year(self, **kwargs):
            return bluebelt.datetime.dt.year(self._obj, **kwargs)

        def quarter(self, **kwargs):
            return bluebelt.datetime.dt.year(self._obj, **kwargs)

        def month(self, **kwargs):
            return bluebelt.datetime.dt.quarter(self._obj, **kwargs)

        def day(self, **kwargs):
            return bluebelt.datetime.dt.day(self._obj, **kwargs)

        def weekday(self, **kwargs):
            return bluebelt.datetime.dt.weekday(self._obj, **kwargs)
        
        def day_name(self, **kwargs):
            return bluebelt.datetime.dt.day_name(self._obj, **kwargs)

        def is_holiday(self, **kwargs):
            return bluebelt.datetime.dt.is_holiday(self._obj, **kwargs)

        def is_weekend(self, **kwargs):
            return bluebelt.datetime.dt.is_weekend(self._obj, **kwargs)
        
        def iso_year(self, **kwargs):
            return bluebelt.datetime.dt.iso_year(self._obj, **kwargs)

        def iso_week(self, **kwargs):
            return bluebelt.datetime.dt.iso_week(self._obj, **kwargs)
        
        def week(self, **kwargs):
            return bluebelt.datetime.dt.week(self._obj, **kwargs)

        #def shift(self, shifts=None, **kwargs):

    
    class std():

        def __init__(self, pandas_obj):
            self._obj = pandas_obj
                
        # standard deviation
        def short_term_std(self, observations=2):
            return bluebelt.statistics.standard_deviation.short_term_std(self._obj, observations=observations)

        average_moving_range = short_term_std

    class patterns():

        def __init__(self, pandas_obj):
            self._obj = pandas_obj
                
        # patterns
        def polynomial(self, **kwargs):
            return bluebelt.analysis.patterns.polynomial(self._obj, **kwargs)

        def periodical(self, **kwargs):
            return bluebelt.analysis.patterns.periodical(self._obj, **kwargs)

    class test():
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        # hypothesis testing
        def normal_distribution(self, alpha=0.05, **kwargs):
            return bluebelt.analysis.hypothesis_testing.normal_distribution(self._obj, alpha=alpha)

    class ppa():
        def __init__(self, pandas_obj):
            self._obj = pandas_obj

        def control_chart(self, **kwargs):
            return bluebelt.analysis.ppa.ControlChart(self._obj, **kwargs)
            
        def run_chart(self, alpha=0.05, **kwargs):
            return bluebelt.analysis.ppa.RunChart(self._obj, alpha=alpha, **kwargs)
