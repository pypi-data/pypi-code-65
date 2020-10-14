import asyncio
import gcsfs
import pandas as pd
import numpy as np
import pyarrow


async def get_dataframe(path, loop=None):
    fs = gcsfs.GCSFileSystem(asynchronous=False)
    await fs.set_session()
    # result = await fs._ls(path)
    # async with fs.open(path) as f:
    #    result = f.read()
    #    pr
    await fs._get([path], ["./tmp.csv"])
    result = pd.read_csv("./tmp.csv")
    await fs.session.close()
    return result
    # return pyarrow.parquet.read_table(f)


fs = gcsfs.GCSFileSystem()
path = "gs://sq-ds-capital-prod/testreads/ex.pq"
with fs.open(path, "w") as f:
    df = pd.DataFrame(np.random.rand(100, 10), columns=[f"c{i}" for i in range(10)])
    df.to_csv(f)

# loop = asyncio.get_event_loop()
# df = loop.run_until_complete(get_dataframe(path, loop))
df = asyncio.run(get_dataframe(path))
print(df)
