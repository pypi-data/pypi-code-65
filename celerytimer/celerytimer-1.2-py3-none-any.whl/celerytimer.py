import functools
import datetime
import time
from celery import shared_task
from celerytimer.mysqldb import TimingTask
import pytz

base_obj = None


class BaseTask(object):

    def __init__(self, host, port, user, password, database):
        self.time_limit = 60  # N分钟任务没有执行，任务丢弃
        self.sql_obj = TimingTask(host, port, user, password, database)

    @staticmethod
    def filter_more_than_a_day(executed_data):
        """
        过滤掉执行任务大于一天的数据
        :param executed_data: 需要定时执行的数据
        """
        data = dict()
        now = datetime.datetime.now() + datetime.timedelta(days=1)
        now_dt = int(now.strptime(now, "%Y-%m-%d %H:%M:%S").timestamp())
        for time_stamp, executed_data_tmp in executed_data.items():
            if time_stamp < now_dt:
                data[time_stamp] = executed_data_tmp
        return data

    def check_executed_data(self, executed_data: dict, sql_unique: list):
        """校验执行数据和只获取一个小时内需要执行的任务，保证输入数据的严谨
        :param executed_data: 任务执行的数据 格式：{时间戳:[{},{},..],时间戳：[{},{},...],...}
        :param sql_unique: 任务的唯一索引，必须保证executed_data数据中包含sql_unique的所有字段
        """
        if not isinstance(executed_data, dict) or not isinstance(sql_unique, list):
            raise Exception("数据格式异常")

        executed_data_filter = {}
        for timestamp, data in executed_data.items():
            last_time = datetime.datetime.now() + datetime.timedelta(minutes=self.time_limit)
            pre_time = datetime.datetime.now() + datetime.timedelta(minutes=-self.time_limit)
            pre_timestamp = self.datetime_to_timestamp(pre_time)
            expires_timestamp = self.datetime_to_timestamp(last_time)
            if not int(pre_timestamp) < timestamp < int(expires_timestamp):
                continue
            for inner_data in data:
                res = set(inner_data.keys()) & set(sql_unique)
                if len(res) != len(sql_unique):
                    raise Exception("索引字段不在任务数据中")
            executed_data_filter[timestamp] = data
        return executed_data_filter

    @staticmethod
    def timestamp_to_datetime(timestamp):
        # 时间戳转datetime类型
        geijing = pytz.timezone("Asia/Shanghai")
        executed_time = datetime.datetime.fromtimestamp(timestamp).astimezone(geijing)
        return executed_time

    @staticmethod
    def datetime_to_timestamp(datetime_data):
        # datetime类型转时间戳
        timestamp_data = time.mktime(datetime_data.timetuple())
        return timestamp_data

    def filter_and_save_task_sql(self, task: str, task_name: str, flag: str, executed_data: dict, sql_unique: list,
                                 repeatable=False):
        """过滤旧任务，保存新任务，并返回新任务数据
        Keyword Arguments:
            ----
            task: 任务名称
            task_name: 任务名称
            executed_data: 执行任务的数据：{时间戳:[{},{},...],...}
            sql_unique: 任务数据的唯一索引
            flag: 任务标识
            repeatable: 是否执行旧任务
        return: 任务数据 {时间戳:[{},{},...],...}
        """
        filter_executed_data = self.sql_obj.filter_and_save_task(task, task_name, flag, executed_data, sql_unique,
                                                                 repeatable)
        return filter_executed_data

    def update_task_status_sql(self, task: str, flag: str, executed_data: dict, sql_unique: list, status: int):
        """过滤旧任务，保存新任务，并返回新任务数据
        Keyword Arguments:
            ----
            task: 任务名称
            task: 任务标识
            executed_data: 执行任务的数据：{时间戳:[{},{},...],...}
            sql_unique: 任务数据的唯一索引
            status: 任务状态
        return:
        """
        self.sql_obj.update_task_status(task, flag, executed_data, sql_unique, status)


class TimingTasks(object):
    """定时任务执行器
    """

    def __init__(self, host, port, user, password, database):
        global base_obj
        base_obj = BaseTask(host, port, user, password, database)
        self.base_obj = base_obj

    def pre_task_handle(self, task: str, task_name: str, flag: str, executed_data: dict, sql_unique: list,
                        repeatable: bool) -> dict:
        """数据检查校验
        Keyword Arguments:
            ----
            task: 任务名
            task_name: 任务昵称
            flag: 任务标识
            executed_data: 执行任务的数据 {时间戳:[{“account_id”:12,"channel_id":124},{},..],时间戳}
            sql_unique: 数据库唯一索引，从executed_data中获取该字段的值
            repeatable: 可以重复执行(默认False)，对应的是数据库
        """
        # 数据校验和时间校验
        executed_data = self.base_obj.check_executed_data(executed_data, sql_unique)
        # 过滤重复的任务，并保存新任务
        filter_executed_data = self.base_obj.filter_and_save_task_sql(task, task_name, flag, executed_data, sql_unique,
                                                                      repeatable)
        return filter_executed_data

    def registration_task(self, func: object, task: str, flag: str, executed_data: dict, sql_unique: list, *args,
                          **kwargs):
        """把任务注册到celery中
        Keyword Arguments:
            ----
            func：业务处理相关的函数
            task: 任务名
            flag: 任务标识
            executed_data: 执行任务的数据
            sql_unique: 数据库唯一索引，从executed_data中获取该字段的值
        """
        for time_stamp, data in executed_data.items():
            if not data:
                continue
            args_tmp = list(args)
            args_tmp.insert(0, {time_stamp: data})
            arg = tuple(args_tmp)
            callback_data = {time_stamp: data}
            executed_time = self.base_obj.timestamp_to_datetime(time_stamp)
            expires_executed_time = executed_time + datetime.timedelta(hours=1)
            func.apply_async(args=arg, kwargs=kwargs, eta=executed_time, expires=expires_executed_time,
                             link=success_callback.si(task, flag, callback_data, sql_unique),
                             link_error=error_callback.si(task, flag, callback_data, sql_unique))

    def executed_task(self, task: str, task_name: str, flag: str, sql_unique: list, repeatable=False):
        """任务装饰器，用于定时任务的执行
        Keyword Arguments:
            ----
            task: 任务名
            task_name: 任务昵称
            flag: 任务标识
            sql_unique: 数据库唯一索引，从executed_data中获取该字段的值
            repeatable: 可以重复执行(默认False)，对应的是数据库
        """

        def wrapper(func):
            @functools.wraps(func)
            def run(executed_data, *args, **kwargs):
                """任务装饰器，用于定时任务的执行
                Keyword Arguments:
                    ----
                    executed_data: 任务数据 {时间戳:[{},{},{},...]}
                """
                # 任务开始前的处理
                executed_data = self.pre_task_handle(task, task_name, flag, executed_data, sql_unique, repeatable)
                # 注册任务并在任务完成后进行回调操作
                self.registration_task(func, task, flag, executed_data, sql_unique, *args, **kwargs)

            return run

        return wrapper


@shared_task
def success_callback(task: str, flag: str, executed_data: dict, sql_unique: list):
    """任务执行成功回调
    Keyword Arguments:
        ----
        task: 任务名
        flag: 任务标识
        executed_data: 执行任务的数据
        sql_unique: 数据库唯一索引
    """
    # 更新数据库的任务状态
    if executed_data:
        base_obj.update_task_status_sql(task, flag, executed_data, sql_unique, status=1)


@shared_task
def error_callback(task: str, flag: str, executed_data: dict, sql_unique: list):
    """任务执行失败回调
    Keyword Arguments:
        ----
        task: 任务名
        flag: 任务标识
        executed_data: 执行任务的数据
        sql_unique: 任务唯一索引
    """
    # 更新数据库的任务状态
    if executed_data:
        base_obj.update_task_status_sql(task, flag, executed_data, sql_unique, status=2)
