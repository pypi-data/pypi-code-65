import asyncio
from tqdm import tqdm
from pyferno.exception import PromiseException


class Promise(object):
    @staticmethod
    async def _internal_worker(semaphore, task):
        """
        This is internal worker that uses semaphore to control concurrency
        :param semaphore:
        :param task:
        :return:
        """
        async with semaphore:
            return await task

    @staticmethod
    async def all(__tasks: list, concurrency: int = 10, progress: object = None) -> list:
        """
        Runs thru the list of tasks asynchronously by limiting the concurrency by using a semaphore
        :param __tasks: List of tasks
        :param concurrency: Concurrency of running tasks, integer. Defaults to 10
        :param progress: Progress bar message or boolean True to display default progress bar
        :return: Returns list with finished tasks (fulfilled promises)
        """
        try:
            semaphore = asyncio.Semaphore(concurrency)
            # re-schedule tasks
            re_tasks = list()
            for _task in __tasks:
                task = asyncio.ensure_future(Promise._internal_worker(semaphore, _task))
                re_tasks.append(task)

            if progress:
                progress_message = progress if isinstance(progress, str) else "Promise.all"
                results = [
                    await res for res in
                    tqdm(asyncio.as_completed(re_tasks),
                         desc=progress_message,
                         total=len(re_tasks))
                ]
            else:
                results = [await res for res in asyncio.as_completed(re_tasks)]
            return results

        except PromiseException as ex:
            print(ex)
            raise

    @staticmethod
    async def _internal_key_worker(semaphore, key, task, pbar=None):
        """
        This is internal worker that uses semaphore to control concurrency
        :param semaphore:
        :param task:
        :return:
        """
        async with semaphore:
            out = await task
            pbar.update(1)
            return key, out

    @staticmethod
    async def props(__props: dict, concurrency: int = 20, progress: object = None) -> dict:
        """
        Runs thru the dict of key,task asynchronously by limiting the concurrency b using a semaphore.
        Maps results back to the dictionary with same keys with all tasks fulfilled.
        It will fail if any task fails
        :param __tasks: Map (dict) with name:task pairs. Task is an async function
        :param concurrency: Concurrency of running tasks, integer. Defaults to 10
        :param progress: Progress bar message or boolean True to display default progress bar
        :return: Returns dict with name:<finished task> pairs.
        """
        try:
            progress_message = ""
            if progress:
                progress_message = progress if isinstance(progress, str) else "Promise.all"
            with tqdm(desc=progress_message) as pbar:
                semaphore = asyncio.Semaphore(concurrency)
                tasks = list()
                for _key, _task in __props.items():
                    task = Promise._internal_key_worker(semaphore, _key, _task, pbar)
                    tasks.append(task)

                out = {k: v for (k, v) in await asyncio.gather(*tasks)}
                return out

        except PromiseException as ex:
            print(ex)
            raise
