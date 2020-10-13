import bisect
from datetime import datetime
from datetime import timezone
from enum import Enum
from typing import Optional

import numpy as np
import pandas as pd


class LayerLevel(Enum):
    NONE = 0
    SECOND = 1
    MINUTE = 2
    HOUR = 3
    DAY = 4
    MONTH = 5
    QUARTER = 6
    YEAR = 7

    @classmethod
    def levels(cls):
        return {v.value: v for k, v in cls.__members__.items()}

    @classmethod
    def min(cls):
        levels = cls.levels()
        return levels[min(levels)]

    @classmethod
    def max(cls):
        levels = cls.levels()
        return levels[max(levels)]

    def get_deeper_level(self):
        return self.levels()[self.value - 1]

    def get_shallower_level(self):
        return self.levels()[self.value + 1]

    def transform(self, ts: datetime):
        transformer = self._transformers[self]
        if not transformer:
            return ts

        return transformer(ts)


LayerLevel._transformers = {
    LayerLevel.NONE: None,
    LayerLevel.SECOND: lambda t: t.replace(microsecond=0),
    LayerLevel.MINUTE: lambda t: t.replace(second=0, microsecond=0),
    LayerLevel.HOUR: lambda t: t.replace(minute=0, second=0, microsecond=0),
    LayerLevel.DAY: lambda t: t.replace(hour=0, minute=0, second=0, microsecond=0),
    LayerLevel.MONTH: lambda t: t.replace(
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ),
    LayerLevel.QUARTER: lambda t: t.replace(
        month={0: 1, 1: 4, 2: 7, 3: 10}[(t.month - 1) // 3],
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ),
    LayerLevel.YEAR: lambda t: t.replace(
        month=1,
        day=1,
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    ),
}


MIN_LAYER_LEVEL = LayerLevel.min()
MAX_LAYER_LEVEL = LayerLevel.max()


class Indexer:

    __instance = None
    __slots__ = [
        "_uri",
        "_min_level",
        "_max_level",
        "_layers",
        "_virtual_indexes",
        "_last_update",
    ]

    def __init__(
        self,
        uri: str,
        min_level: Optional[LayerLevel] = MIN_LAYER_LEVEL,
        max_level: Optional[LayerLevel] = MAX_LAYER_LEVEL,
    ):
        self._uri = uri
        self._min_level = min_level
        self._max_level = max_level
        self._layers = None
        self._virtual_indexes = None
        self._last_update = None

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def last_update(self) -> Optional[datetime]:
        return self._last_update

    async def load(self, items) -> None:
        raise NotImplementedError()

    async def add(self, item) -> None:
        raise NotImplementedError()

    async def get(self, date_from: datetime, date_to: datetime) -> np.ndarray:
        raise NotImplementedError()

    @staticmethod
    def _indexify(date: datetime) -> int:
        first_timestamp = datetime.utcfromtimestamp(0).replace(tzinfo=timezone.utc)
        # How many microseconds from `first_timestamp`?
        return int((date - first_timestamp).total_seconds())


class MemoryIndexer(Indexer):
    def __init__(
        self,
        min_level: Optional[LayerLevel] = MIN_LAYER_LEVEL,
        max_level: Optional[LayerLevel] = MAX_LAYER_LEVEL,
    ):
        super().__init__(":memory:", min_level=min_level, max_level=max_level)

    def get(self, date_from: datetime, date_to: datetime) -> np.ndarray:
        vi_index_from = self._indexify(date_from)
        vi_index_to = self._indexify(date_to)

        v = self._search_in_layer(self._max_level, vi_index_from, vi_index_to)
        return np.unique(v[np.flatnonzero(v)])

    def _search_in_layer(self, layer_level, vi_index_from, vi_index_to):
        index_from = bisect.bisect_left(
            self._virtual_indexes[layer_level],
            vi_index_from,
        )
        index_to = (
            bisect.bisect_left(self._virtual_indexes[layer_level], vi_index_to) - 1
        )

        if layer_level == self._min_level:
            index_to += 1
            if index_from >= index_to:
                return np.array([], dtype="object")

            postings_lists = self._layers[layer_level][index_from:index_to]
            return np.concatenate(postings_lists)

        if index_from >= index_to:
            return self._search_in_layer(
                layer_level.get_deeper_level(),
                vi_index_from,
                vi_index_to,
            )

        left = self._search_in_layer(
            layer_level.get_deeper_level(),
            vi_index_from,
            self._virtual_indexes[layer_level][index_from],
        )
        right = self._search_in_layer(
            layer_level.get_deeper_level(),
            self._virtual_indexes[layer_level][index_to],
            vi_index_to,
        )
        postings_lists = self._layers[layer_level][index_from:index_to]
        center = np.concatenate(postings_lists)
        return np.concatenate([left, center, right])

    async def load(self, items):
        def layer(df):
            return df["values"].to_numpy()

        def virtual_indexes(df):
            return df["timestamp"].apply(self._indexify).to_numpy().astype(np.uint32)

        def ts_col_name(layer_level):
            return f"timestamp_{layer_level.name.lower()}"

        df = pd.DataFrame(items)
        layers, v_indexes = {}, {}
        for ll in [
            LayerLevel.levels()[i]
            for i in range(self._min_level.value, self._max_level.value + 1)
        ]:
            ll_ts_col_name = ts_col_name(ll)

            df[ll_ts_col_name] = df["timestamp"].apply(ll.transform)
            df_level = df.groupby(ll_ts_col_name).agg({"values": sum}).reset_index()
            df_level["values"] = df_level["values"].apply(lambda l: list(set(l)))
            df_level = df_level.rename(columns={ll_ts_col_name: "timestamp"})

            layers[ll] = layer(df_level)
            v_indexes[ll] = virtual_indexes(df_level)
            v_indexes[ll] = virtual_indexes(df_level)

        # the memory could be further squeezed by storing list of numbers on each level
        # and remap them in the end so that the strings are stored once only
        self._layers = layers
        self._virtual_indexes = v_indexes
        self._last_update = datetime.utcnow().replace(tzinfo=timezone.utc)


class TestLoop:
    def __init__(self):
        async def cron(d):
            while True:
                await asyncio.sleep(1)
                d["count"] += 1
                print("cron")

        loop = asyncio.new_event_loop()
        self._d = {"count": 0}
        self._task = loop.create_task(cron(self._d))

    def cancel(self):
        self._task.cancel()
