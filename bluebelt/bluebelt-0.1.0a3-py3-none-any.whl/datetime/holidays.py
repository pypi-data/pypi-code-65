import datetime
import pandas as pd
import numpy as np

# nieuwjaarsdag: 1 januari (New Year's Day)
# goede vrijdag: 2 dagen voor 1e paasdag (Good Friday)
# 1e paasdag: berekenen (Easter)
# 2e paasdag: 1 dag na 1e paasdag (Easter Monday)
# hemelvaart: 39 dagen na 1e paasdag (Ascension Day)
# 1e pinksterdag :49 dagen na 1e paasdag (Pentecost)
# 2e pinksterdag: 50 dagen na 1e paasdag (Whit Monday)
# koningsdag: 27 april
# bevrijdingsdag: 5 mei iedere 5 jaar (Liberation Day)
# 1e kerstdag: 25 december (Christmas)
# 2e kerstdag: 26 december (Boxing Day)

def holidays(check_date, **kwargs):

    holidays = kwargs.get('holidays', {
        'new years day': True,
        'good friday': True,
        'easter': True,
        'easter monday': True,
        'ascension day': True,
        'pentecost': True,
        'whit monday': True,
        'christmas': True,
        'boxing day': True,
        'kings day': True,
        'liberation day': True,
        })

    #deal with datetimes
    check_date = pd.to_datetime(check_date).date()

    holiday_dates={'new years day': _new_years_day(check_date.year),
                   'good friday': _good_friday(check_date.year),
                   'easter': _easter(check_date.year),
                   'easter monday': _easter_monday(check_date.year),
                   'ascension day': _ascension_day(check_date.year),
                   'pentecost': _pentecost(check_date.year),
                   'whit monday': _whit_monday(check_date.year),
                   'christmas': _christmas(check_date.year),
                   'boxing day': _boxing_day(check_date.year),
                   'kings day': _kings_day(check_date.year),
                   'liberation day': _liberation_day(check_date.year)}

    for key, value in holidays.items():
        if value==True:
            if holiday_dates.get(key)==check_date:
                return True
    return False

def _new_years_day(year):
    return datetime.date(year, 1, 1)

def _easter(year):
    "Returns Easter as a date object."
    a = year % 19
    b = year // 100
    c = year % 100
    d = (19 * a + b - b // 4 - ((b - (b + 8) // 25 + 1) // 3) + 15) % 30
    e = (32 + 2 * (b % 4) + 2 * (c // 4) - d - (c % 4)) % 7
    f = d + e - 7 * ((a + 11 * d + 22 * e) // 451) + 114
    month = f // 31
    day = f % 31 + 1
    return datetime.date(year, month, day)

def _easter_monday(year):
    return _easter(year) + datetime.timedelta(days=1)

def _good_friday(year):
    return _easter(year) + datetime.timedelta(days=-2)

def _ascension_day(year):
    return _easter(year) + datetime.timedelta(days=39)

def _pentecost(year):
    return _easter(year) + datetime.timedelta(days=49)

def _whit_monday(year):
    return _easter(year) + datetime.timedelta(days=50)

def _christmas(year):
    return datetime.date(year, 12, 25)

def _boxing_day(year):
    return datetime.date(year, 12, 26)

def _kings_day(year):
    return datetime.date(year, 4, 27)

def _liberation_day(year, annually=False):
    if annually==True or year % 5 == 0:
        return datetime.date(year, 5, 5)
    else:
        return np.datetime64("NaT")
