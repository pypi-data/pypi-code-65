import asyncio
import os
import tempfile
import time

import gcsfs
import numpy as np
import pandas as pd
import pyarrow

import blocks


def time_assemble_gsutil(path):
    start = time.time()
    _ = blocks.assemble(path)
    s = "assemble_gsutil"
    print(f"  {s:>20} {time.time() - start}")


def time_assemble_native(path):
    start = time.time()
    _ = blocks.assemble(path, filesystem=blocks.filesystem.GCSNativeFileSystem())
    s = "assemble_native"
    print(f"  {s:>20} {time.time() - start}")


def time_gcsfs_sync(path):
    start = time.time()
    fs = gcsfs.GCSFileSystem()
    paths = fs.glob(path)
    dfs = []
    for p in paths:
        dfs.append(pyarrow.parquet.read_table(p, filesystem=fs).to_pandas())

    _ = pd.concat(dfs, axis=0).reset_index()
    s = "gcsfs_sync"
    print(f"  {s:>20} {time.time() - start}")


async def get_dataframe(path, fs):
    async with fs._open(path) as f:
        return pyarrow.parquet.read_table(f)


async def dataframes(paths, loop):
    fs = gcsfs.GCSFileSystem(asynchronous=True, loop=loop)
    await fs.set_session()
    return await asyncio.gather(*(get_dataframe(p, fs) for p in paths))


def time_gcsfs_async(path):
    start = time.time()
    paths = gcsfs.GCSFileSystem().glob(path)
    loop = asyncio.get_event_loop()
    dfs = loop.run_until_complete(dataframes(paths, loop))
    _ = pd.concat(dfs, axis=0).reset_index()
    s = "gcsfs_async"
    print(f"  {s:>20} {time.time() - start}")


def time_gcsfs_get(path):
    start = time.time()
    fs = gcsfs.GCSFileSystem()
    paths = fs.glob(path)
    with tempfile.TemporaryDirectory() as d:
        local = [os.path.join(d, p.split("/")[-1]) for p in paths]
        fs.get(paths, local)
        dfs = [pd.read_parquet(l) for l in local]
    _ = pd.concat(dfs, axis=0).reset_index()
    s = "gcsfs_async"
    print(f"  {s:>20} {time.time() - start}")


def test_suite(n_file, n_row_per_file, n_col=100):
    print(f"Test! n_file={n_file} n_row_per_file={n_row_per_file} n_col={n_col}")
    for i in range(n_file):
        df = pd.DataFrame(
            np.random.rand(n_row_per_file, n_col),
            columns=[f"c{k:03d}" for k in range(n_col)],
        )
        blocks.place(df, f"gs://sq-ds-capital-prod/testreads/test.{i:03d}.pq")

    try:
        time_gcsfs_get("gs://sq-ds-capital-prod/testreads/*.pq")
        time_gcsfs_sync("gs://sq-ds-capital-prod/testreads/*.pq")
        time_assemble_gsutil("gs://sq-ds-capital-prod/testreads/*.pq")
        time_assemble_native("gs://sq-ds-capital-prod/testreads/*.pq")
    finally:
        blocks.filesystem.GCSFileSystem().rm(
            "gs://sq-ds-capital-prod/testreads", recursive=True
        )


test_suite(30, 1000)
test_suite(30, 100000)
