import json
import aiohttp
import asyncio
from .config import Server

async def optimize_dataset_async(dataset):
    async def fetch(session, data):
        req = {
            'key': Server.key
        }
        req.update(data)
        try:
            async with session.put(Server.url, data=json.dumps(req),
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


def optimize_dataset(dataset):
    asyncio.run(optimize_dataset_async(dataset))
