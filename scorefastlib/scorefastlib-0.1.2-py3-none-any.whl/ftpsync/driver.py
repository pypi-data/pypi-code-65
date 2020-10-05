"""
FTP Driver
"""

import os
import time
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from fluent import sender

from ftpsync.constants import Common
from ftpsync.ftp_transfer import FTPTransfer

# for remote fluent
sender.setup(Common.logger_app_name.value, host='localhost', port=24224)


def minute():
    """Run job at every 15 minutes"""
    FTPTransfer.process(Common.interval_minute.value)


def hour():
    """Run job on every hour"""
    FTPTransfer.process(Common.interval_hourly.value)


def day():
    """Run job once in a day at 1 o'clock"""
    FTPTransfer.process(Common.interval_daily.value)


def week():
    """Run job on every Monday at 2 o'clock"""
    FTPTransfer.process(Common.interval_weekly.value)


def month():
    """Run job on every month's 1st at 3 o'clock """
    FTPTransfer.process(Common.interval_monthly.value)


if __name__ == '__main__':

    print(datetime.now())
    scheduler = BackgroundScheduler()
    scheduler.add_job(minute, 'interval', id='min', minutes=15, next_run_time=datetime.now())
    scheduler.add_job(hour, 'cron', id='hour', hour='*/1')
    scheduler.add_job(day, 'cron', id='day', hour='1')
    scheduler.add_job(week, 'cron', id='week', day_of_week='mon', hour=2)
    scheduler.add_job(month, 'cron', id='month', day='1', hour=3)

    scheduler.start()
    print('Press Ctrl+{0} to exit'.format('Break' if os.name == 'nt' else 'C'))

    try:
        # This is here to simulate application activity (which keeps the main thread alive).
        while True:
            time.sleep(2)
    except (KeyboardInterrupt, SystemExit):
        # Not strictly necessary if daemonic mode is enabled but should be done if possible
        scheduler.shutdown()
