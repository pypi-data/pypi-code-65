from typing import Any, Dict, List, Optional

from cognite.air._api import AIRClientError
from cognite.air._backfilling_api import AIRBackfillingAPI, NoBackfillAPI
from cognite.air._config import AIRClientConfig
from cognite.air._events_api import AIREventsAPI
from cognite.air._time_series_api import AIRTimeSeriesAPI
from cognite.air.constants import MA_FIELD_META_FIELDS, MA_FIELD_META_MODELVERSION, SA_EXT_ID, SA_FIELD_META_DATA
from cognite.air.utils import is_string_truthy, parse_json_if_json
from cognite.client import CogniteClient


class AIRClient:
    def __init__(self, data: Dict[str, Any], client: CogniteClient, secrets: Dict[str, Any], debug: bool = False):
        del secrets  # Unused for now (required in function signature)
        sa_ext_id = self._extract_and_validate_sa_ext_id(data)
        schedule_asset = self._retrieve_and_verify_schedule_asset(client, sa_ext_id)
        model_asset = self._retrieve_and_verify_model_asset(client, schedule_asset.parent_external_id)
        model_version = model_asset.metadata[MA_FIELD_META_MODELVERSION]
        # Retrieve backfilling asset if the model uses backfilling:
        backfilling_asset = None
        if is_string_truthy(model_asset.metadata.get("backfill")):
            backfilling_asset = self._retrieve_and_verify_backfill_asset(client, sa_ext_id, model_version)

        self._config = AIRClientConfig(
            client=client,
            data_set_id=schedule_asset.data_set_id,
            schedule_asset=schedule_asset,
            schedule_asset_id=schedule_asset.id,
            schedule_asset_ext_id=sa_ext_id,
            data_fields=parse_json_if_json(schedule_asset.metadata.get(SA_FIELD_META_DATA)) or {},
            data_fields_defs=self.create_data_field_dct(model_asset.metadata.get(MA_FIELD_META_FIELDS)),
            model_name=model_asset.name,
            model_version=model_version,
        )
        self.events = AIREventsAPI(self._config)
        self.time_series = AIRTimeSeriesAPI(self._config)
        self.backfilling = NoBackfillAPI()
        if backfilling_asset:
            backfilling = AIRBackfillingAPI(self._config, backfilling_asset)
            if backfilling.in_progress:
                self.backfilling = backfilling  # type: ignore

        if debug:
            print(
                f"Tenant: {client.config.project}\nSchedule asset ext. ID: {self._config.schedule_asset_ext_id}\n"
                f"Model name: {self._config.model_name}\nModel version: {self._config.model_version}\n"
                f"Backfilling in progress: {self.backfilling.in_progress}\n"
            )

    @property
    def config(self):
        return self._config

    @property
    def cognite_client(self):
        return self._config.client

    @property
    def schedule_asset_id(self):
        return self._config.schedule_asset_id

    @property
    def schedule_asset_ext_id(self):
        return self._config.schedule_asset_ext_id

    @property
    def model_name(self):
        return self._config.model_name

    @property
    def model_version(self):
        return self._config.model_version

    def retrieve_fields(self, field_names: List[str], ignore_unknown_field_names: bool = False) -> List[str]:
        if not isinstance(field_names, list) or not all(isinstance(s, str) for s in field_names):
            raise TypeError(f"Expected '{field_names}' to be a list of strings!")

        fields = list(map(self._config.data_fields.get, field_names))
        if not ignore_unknown_field_names and None in fields:
            err_field_names = [id for id, field in zip(field_names, fields) if field is None]
            raise ValueError(f"The following field names were not found: {err_field_names}")

        return_fields = []
        for id, field in zip(field_names, fields):
            field_type = self._config.data_fields_defs[id]["python-type"]
            ret_val = parse_json_if_json(field)
            if field_type is bool:  # NB: bool(string) is True for all non-empty strings...:
                return_fields.append(is_string_truthy(ret_val))
            elif isinstance(ret_val, list):  # this means multiple=True
                return_fields.append(list(map(field_type, ret_val)))
            else:
                return_fields.append(field_type(ret_val))
        return return_fields  # type: ignore

    def retrieve_field(self, field_name: str) -> str:
        if not isinstance(field_name, str):
            raise TypeError(f"Expected 'field_name' to be of type {str}, not {type(field_name)}")
        return self.retrieve_fields([field_name])[0]

    @staticmethod
    def convert_type_info(dct):
        legal_types = {
            "str": str,
            "int": int,
            "float": float,
            "bool": bool,
            "TimeSeries": str,
            "Asset": str,
        }
        dct["python-type"] = legal_types[dct["type"]]
        return dct

    def create_data_field_dct(self, json: Optional[str]):
        lst_of_field_defs = parse_json_if_json(json) or []
        return {dct.pop("id"): self.convert_type_info(dct) for dct in lst_of_field_defs}

    @staticmethod
    def _extract_and_validate_sa_ext_id(data):
        sa_ext_id = data.get(SA_EXT_ID)
        if sa_ext_id is None:
            raise KeyError(f"Missing required input field '{SA_EXT_ID}'")
        if not isinstance(sa_ext_id, str):
            raise TypeError(f"Expected field '{SA_EXT_ID}' to be of type {str}, not {type(sa_ext_id)}")
        return sa_ext_id

    @staticmethod
    def _retrieve_and_verify_schedule_asset(client, sa_ext_id):
        schedule_asset = client.assets.retrieve(external_id=sa_ext_id)
        if schedule_asset is None:
            raise AIRClientError(f"Asset not found: No 'schedule asset' with external_id: '{sa_ext_id}'")
        return schedule_asset

    @staticmethod
    def _retrieve_and_verify_model_asset(client, model_ext_id):
        model_asset = client.assets.retrieve(external_id=model_ext_id)
        if model_asset is None:
            raise AIRClientError(f"Asset not found: No 'model asset' with external_id: '{model_ext_id}'")
        return model_asset

    @staticmethod
    def _retrieve_and_verify_backfill_asset(client, sa_ext_id, model_version):
        backfill_asset_list = client.assets.list(parent_external_ids=[sa_ext_id], metadata={"version": model_version})
        if len(backfill_asset_list) == 1:
            return backfill_asset_list[0]
        raise AIRClientError(
            f"Found {len(backfill_asset_list)} backfilling asset(s). Expected exactly 1 backfilling asset"
        )
