from datetime import datetime, timedelta
from json import loads
from logging import getLogger
from django.conf import settings
from redis import ConnectionPool, Redis
from django_opstasks.models import TaskResult


LOGGER = getLogger('django')

CONSUL_CONFIGS = settings.CONSUL_CONFIGS
CONSUL_SECRETS = settings.CONSUL_SECRETS

PRE_DEFINED_QUEUES = CONSUL_CONFIGS.get('PRE_DEFINED_QUEUES', ['BJ', 'IN', 'ID', 'SG', 'PHI'])

REDIS_OPSTASKS_CONNECTION_POOL = ConnectionPool(
    host=CONSUL_CONFIGS.get('REDIS_HOST', 'opstasks-redis.devops.svc.cluster.local'),
    port=CONSUL_CONFIGS.get('REDIS_PORT', 6379),
    db=CONSUL_CONFIGS.get('REDIS_OPSTASKS_DB', 0)
)

REDIS_RECORD_CONNECTION_POOL = ConnectionPool(
    host=CONSUL_CONFIGS.get('REDIS_HOST', 'opstasks-redis.devops.svc.cluster.local'),
    port=CONSUL_CONFIGS.get('REDIS_PORT', 6379),
    db=CONSUL_CONFIGS.get('REDIS_RECORD_DB', 2)
)


# 从redis中获取各队列中正在排队的任务, 返回字典, 包含以下内容
## list: 包含datetime、任务名称、队列名称的列表
## count: 每个队列中排队的任务数量
## total: 正在排队的任务总数
def task_in_queues():
    """
    Get tasks waiting in the queue, return a dict
    """
    redis_connection = Redis(connection_pool=REDIS_OPSTASKS_CONNECTION_POOL)
    tasks_list = []
    count = []
    total = 0
    tasks = lambda queue: redis_connection.lrange(queue, 0, -1)
    for queue in PRE_DEFINED_QUEUES:
        count.append(f'{queue}: {len(tasks(queue))}')
        total += len(tasks(queue))
        for task in tasks(queue):
            task = loads(task)
            tasks_list.append({
                "datetime": "2020-09-25 21:07:00",
                "task": task['headers']['task'],
                "queue": task['properties']['delivery_info']['routing_key']
            })
    return {"list": tasks_list, "count": ',  '.join(count), "total": total}


# 每天执行的任务数量, 返回一个列表
## 格式为: [['2019-10-10', 200], ['2019-10-11', 400], ['2019-10-12', 650]
def task_execution_trend():
    """
    [['2019-10-10', 200], ['2019-10-11', 400], ['2019-10-12', 650]
    """
    # Get a list of dates within `REDIS_RECORD_TTL` seconds
    redis_record_ttl = CONSUL_CONFIGS.get('REDIS_RECORD_TTL', 5184000)
    LOGGER.info('Get a list of date within %s seconds', redis_record_ttl)
    current_datetime = datetime.now()
    start_datetime = current_datetime - timedelta(seconds=redis_record_ttl)
    dates = [start_datetime.strftime('%Y-%m-%d'),]
    while start_datetime < current_datetime:
        start_datetime += timedelta(days=1)
        dates.append(start_datetime.strftime('%Y-%m-%d'))
    # Get the task count for each date in the dates from redis
    LOGGER.info('Get the count of tasks executed for each date from redis')
    redis_connection = Redis(connection_pool=REDIS_RECORD_CONNECTION_POOL)
    result = lambda date: [date, len(redis_connection.keys(f'{date}/*'))]
    return [result(date) for date in dates]


# TODO # 每个队列中包含的worker数量, 返回一个列表
## 格式如 __doc__
def queue_workers_in_queue():
    """
    Get the number of workers in each queue, return a list such as
      [
        {"value": 0, "name": 'BJ'}, {"value": 0, "name": 'SG'},
        {"value": 0, "name": 'IN'}, {"value": 0, "name": 'ID'}
      ]
    """
    return [
        {"value": 2, "name": 'BJ'},
        {"value": 2, "name": 'SG'},
        {"value": 2, "name": 'IN'},
        {"value": 2, "name": 'ID'},
        {"value": 2, "name": 'PHI'}
    ]


# 每个队列中累计执行任务数量, 返回一个列表
## 格式如 __doc__
def queue_tasks_exe_count_in_queue():
    """
    Get the total count of tasks executed by each queue, return a list such as
        [
        {"value": 90, "name": 'BJ'}, {"value": 30, "name": 'SG'},
        {"value": 10, "name": 'IN'}, {"value": 20, "name": 'ID'},
        ]
    """
    count = lambda queue: TaskResult.objects.filter(queue=queue).count()
    results = [{"value": count(queue), "name": queue} for queue in PRE_DEFINED_QUEUES]
    return results


# 累计执行任务数量, 返回int类型
def tasks_total_count_with_all():
    return TaskResult.objects.all().count()


# worker节点数量, 返回int类型
def workers_count():
    """
    Get workers from OpstasksBroker, return a int number
    """
    redis_connection = Redis(connection_pool=REDIS_OPSTASKS_CONNECTION_POOL)
    LOGGER.info('Get workers from OpstasksBroker')
    workers = redis_connection.smembers('_kombu.binding.celery.pidbox')
    return len(workers)
