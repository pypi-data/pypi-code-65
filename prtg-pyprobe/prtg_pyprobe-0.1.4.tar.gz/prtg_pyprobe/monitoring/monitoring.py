import asyncio
import itertools
import logging

from pysnmp.hlapi.asyncio import SnmpEngine


async def monitoring_listener(q: asyncio.Queue) -> dict:
    out = await q.get()
    q.task_done()
    return out


async def run_monitoring_tasks(
    sensors_avail: list,
    taskdata: list,
    snmp_engine: SnmpEngine,
    async_queue: asyncio.Queue,
) -> list:
    monitoring_task_list = []
    monitoring_listener_list = []
    for sensor, task in itertools.product(sensors_avail, taskdata):
        if task["kind"] == sensor.kind:
            if "mpsnmp" in task["kind"]:
                monitoring_task_list.append(
                    asyncio.create_task(sensor.work(task_data=task, q=async_queue, snmp_engine=snmp_engine))
                )
            else:
                monitoring_task_list.append(asyncio.create_task(sensor.work(task_data=task, q=async_queue)))
            monitoring_listener_list.append(asyncio.create_task(monitoring_listener(async_queue)))
    logging.info(f"Current Queue Size: {async_queue.qsize()}")

    logging.debug(f"Running Tasks in Event Loop (before join): {asyncio.all_tasks()}")
    results = await asyncio.gather(*monitoring_task_list, *monitoring_listener_list)
    [mt.cancel() for mt in monitoring_task_list]
    [ml.cancel() for ml in monitoring_listener_list]
    await async_queue.join()
    logging.debug(f"Running Tasks in Event Loop (after join): {asyncio.all_tasks()}")
    return list(filter(None.__ne__, results))


async def monitoring(
    tasks_list: list,
    sensor_objects: list,
    snmp_engine: SnmpEngine,
):
    logging.info("Initializing Queue")
    async_queue = asyncio.Queue()

    res = await run_monitoring_tasks(
        sensors_avail=sensor_objects,
        taskdata=tasks_list,
        snmp_engine=snmp_engine,
        async_queue=async_queue,
    )
    logging.debug(f"Running Tasks in Event Loop (after results): {asyncio.all_tasks()}")
    return res
