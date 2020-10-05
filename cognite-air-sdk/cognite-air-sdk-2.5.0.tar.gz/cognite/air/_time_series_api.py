from time import sleep

from cognite.air._api import BaseAPIClient
from cognite.air.constants import (
    AIR_TS_FIELD_ASSET_ID,
    AIR_TS_FIELD_DATASET,
    AIR_TS_FIELD_METADATA,
    AIR_TS_META_KEY_MODEL_VERSION,
)
from cognite.air.utils import strip_patch_from_version
from cognite.client.data_classes import TimeSeries


class AIRTimeSeriesAPI(BaseAPIClient):
    RESERVED_AIR_TS_KWARGS = set([AIR_TS_FIELD_DATASET, AIR_TS_FIELD_ASSET_ID])
    RESERVED_AIR_TS_META_KEYS = set([AIR_TS_META_KEY_MODEL_VERSION])

    def _verify_valid_air_time_series_query(self, query_dct):
        illegal_params = self.RESERVED_AIR_TS_KWARGS.intersection(query_dct)
        if illegal_params:
            raise ValueError(f"Got one or more parameters reserved for AIR: {illegal_params}")

        metadata = query_dct.get(AIR_TS_FIELD_METADATA, {})
        illegal_meta_keys = self.RESERVED_AIR_TS_META_KEYS.intersection(metadata)
        if illegal_meta_keys:
            raise ValueError(
                f"'{AIR_TS_FIELD_METADATA}' contained one or more keys reserved for AIR: {illegal_meta_keys}"
            )

    def retrieve(self, ts_ext_id: str, **kwargs) -> TimeSeries:
        self._verify_valid_air_time_series_query(kwargs)
        curr_ts = self.client.time_series.retrieve(external_id=ts_ext_id)
        if curr_ts and curr_ts.asset_id != self._config.schedule_asset_id:
            raise ValueError(
                "Time series external ID already in use in another context."
                f"TS with external_id: {ts_ext_id} is related to asset with id : {curr_ts.asset_id}"
            )
        curr_ts_version = None
        if curr_ts:
            curr_ts_version = strip_patch_from_version(curr_ts.metadata[AIR_TS_META_KEY_MODEL_VERSION])

        if curr_ts_version == strip_patch_from_version(self._config.model_version):
            return curr_ts

        new_ts = TimeSeries(
            external_id=ts_ext_id,
            metadata={
                **kwargs.pop(AIR_TS_FIELD_METADATA, {}),
                AIR_TS_META_KEY_MODEL_VERSION: self._config.model_version,
            },
            asset_id=self._config.schedule_asset_id,
            data_set_id=self._config.data_set_id,
            **kwargs,
        )
        if curr_ts:
            # Current version is actually not the latest, so we deprecate the time series:
            curr_ts.external_id = f"{curr_ts.external_id}:v.{curr_ts_version}"
            self.client.time_series.update(curr_ts)
            sleep(3)

        return self.client.time_series.create(new_ts)
