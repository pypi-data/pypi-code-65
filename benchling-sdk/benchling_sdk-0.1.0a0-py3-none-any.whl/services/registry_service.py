from typing import Iterable

from benchling_api_client.api.registry import register_entities
from benchling_api_client.models.async_task_link import AsyncTaskLink
from benchling_api_client.models.naming_strategy import NamingStrategy

from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.services.base_service import BaseService


class RegistryService(BaseService):
    @api_method
    def register(
        self,
        registry_id: str,
        entity_ids: Iterable[str],
        naming_strategy: NamingStrategy = NamingStrategy.NEW_IDS,
    ) -> AsyncTaskLink:
        registration_body = {"entityIds": entity_ids, "namingStrategy": naming_strategy}
        response = register_entities.sync_detailed(
            client=self.client, registry_id=registry_id, json_body=registration_body
        )
        return model_from_detailed(response)
