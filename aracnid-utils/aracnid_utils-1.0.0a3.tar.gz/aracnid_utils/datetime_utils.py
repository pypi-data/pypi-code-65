"""Provides additional datetime functions.
"""
import re

from datetime import datetime, timedelta
from dateutil import tz
from dateutil.parser import parse

START_MIN = datetime(2000, 1, 1, 0, 0).astimezone()

def timespan(**kwargs):
    """Calculates the endpoints of a timespan.

    The timespan is specified by a set of keyword arguments. Separate arguments
    are used to provide datetime objects or strings representing datetimes.
    The strings can be any parsable notation that results in a datetime object.
    This includes ISO Week Notation, e.g., "2020-W13".

    If the begin time is not specified, the minimum start time is used.
    If the thru time is not specified, the current time is used.
    If a week string is specified, the start time and the thru time will default
    to the week. The week string can be used in conjunction with either begin
    time or thru time.

    Args:
        begin: Datetime object representing the start of the timespan.
        begin_str: String representing the start of the timespan.
        thru: Datetime object representing the end of the timespan.
        thru_str: String representing the end of the timespan.
        week_str: String representing a single week.

    Returns:
        The start and end datetime objects that define the timespan.
    """
    begin_dt = kwargs.get('begin')
    thru_dt = kwargs.get('thru')
    begin_str = kwargs.get('begin_str') or kwargs.get('week_str')
    thru_str = kwargs.get('thru_str') or kwargs.get('week_str')

    # initialize week notation pattern
    pattern_isoweek = r'^\d{4}-W\d{2}$'

    # convert string arguments
    if not begin_dt and begin_str:
        # check iso week notation
        if re.search(pattern_isoweek, begin_str):
            year_num = int(begin_str[:4])
            week_num = int(begin_str[-2:])
            begin_dt = datetime.fromisocalendar(
                year_num, week_num, 1).astimezone()

        else:
            begin_dt = parse(begin_str).astimezone()
    if not thru_dt and thru_str:
        # check iso week notation
        if re.search(pattern_isoweek, thru_str):
            year_num = int(thru_str[:4])
            week_num = int(thru_str[-2:])
            thru_dt = datetime.fromisocalendar(
                year_num, week_num, 1).astimezone()
            thru_dt += timedelta(days=7)

        else:
            thru_dt = parse(thru_str).astimezone()

    # check missing bounds
    if not begin_dt:
        begin_dt = START_MIN
    if not thru_dt:
        thru_dt = datetime.now(tz.tzlocal())

    return begin_dt, thru_dt


if __name__ == '__main__':
    pass
