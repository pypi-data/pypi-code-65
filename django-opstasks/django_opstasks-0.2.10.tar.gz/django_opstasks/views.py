from django.contrib.auth.decorators import login_required
from celery.utils.log import get_task_logger
from django_opstasks.common.response import OpstasksResponse
from django_opstasks.common.response import AsyncResultResponse
# from django_opstasks.dashboard import OpstasksBroker, OpstasksBackend, PRE_DEFINED_QUEUES
from django_opstasks.dashboard import task_in_queues
from django_opstasks.dashboard import task_execution_trend
from django_opstasks.dashboard import queue_workers_in_queue
from django_opstasks.dashboard import queue_tasks_exe_count_in_queue

LOGGER = get_task_logger('django')


# Create opstasks-api views here.
## test error task
def error_test(request):
    if request.method == "GET":
        from django_opstasks.tasks import error
        result = error.apply_async()
        if result.get():
            return AsyncResultResponse(result)
    return OpstasksResponse('Method Not Allowed', 405)


## sync task to database
def sync_task_to_database(request):
    if request.method == "GET":
        from django_opstasks.tasks import sync_task_to_database as task
        result = task.apply_async()
        return AsyncResultResponse(result)
    return OpstasksResponse('Method Not Allowed', 405)


# Create tasks dashboard views here.
@login_required
def dashboard_task_in_queues(request):
    if request.method == "GET":
        data = task_in_queues()
        return OpstasksResponse(data, 200)
    return OpstasksResponse('Method Not Allowed', 405)


## task execution trend last `REDIS_RECORD_TTL` seconds, return a list
@login_required
def dashboard_task_execution_trend(request):
    if request.method == "GET":
        data = task_execution_trend()
        return OpstasksResponse(data, 200)
    return OpstasksResponse('Method Not Allowed', 405)


@login_required
def dashboard_queue_workers_in_queue(request):
    if request.method == "GET":
        data = queue_workers_in_queue()
        return OpstasksResponse(data, 200)
    return OpstasksResponse('Method Not Allowed', 405)


@login_required
def dashboard_queue_tasks_exe_count_in_queue(request):
    if request.method == "GET":
        data = queue_tasks_exe_count_in_queue()
        return OpstasksResponse(data, 200)
    return OpstasksResponse('Method Not Allowed', 405)
