import json
import aiohttp
import asyncio
from .config import *


async def test_dataset_async(dataset, server=SERVER, key=KEY):
    async def fetch(session, data):
        req = {
            'key': key
        }
        req.update(data)
        try:
            async with session.put(server, data=json.dumps(req),
                                   headers={"Content-Type": "application/json"}) as response:
                json_response = await response.json()
                data["solution"] = json_response
        except Exception as err:
            data["status"] = f'error: server request, {err}'

    async with aiohttp.ClientSession() as session:
        tasks = []
        for data in dataset:
            tasks.append(fetch(session, data))
        await asyncio.gather(*tasks)


def optimize_dataset(dataset, login):
    asyncio.run(test_dataset_async(dataset, login))
