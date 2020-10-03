from typing import Iterable, List, Optional, Protocol

from benchling_api_client.api.custom_entities import (
    archive_custom_entities,
    bulk_create_custom_entities,
    bulk_get_custom_entities,
    bulk_update_custom_entities,
    create_custom_entity,
    get_custom_entity,
    list_custom_entities,
    unarchive_custom_entities,
    update_custom_entity,
)
from benchling_api_client.client import Client
from benchling_api_client.models.async_task import AsyncTask
from benchling_api_client.models.async_task_link import AsyncTaskLink
from benchling_api_client.models.custom_entity import CustomEntity
from benchling_api_client.models.custom_entity_archival_change import CustomEntityArchivalChange
from benchling_api_client.models.custom_entity_archive_request import CustomEntityArchiveRequest
from benchling_api_client.models.custom_entity_base_request import CustomEntityBaseRequest
from benchling_api_client.models.custom_entity_bulk_create import CustomEntityBulkCreate
from benchling_api_client.models.custom_entity_bulk_update import CustomEntityBulkUpdate
from benchling_api_client.models.custom_entity_bulk_update_request import CustomEntityBulkUpdateRequest
from benchling_api_client.models.custom_entity_create import CustomEntityCreate
from benchling_api_client.models.custom_entity_list import CustomEntityList
from benchling_api_client.models.custom_entity_patch import CustomEntityPatch
from benchling_api_client.models.custom_entity_unarchive_request import CustomEntityUnarchiveRequest
from benchling_api_client.models.reason1 import Reason1
from benchling_api_client.models.sort import Sort
from benchling_api_client.models.status1 import Status1
from benchling_api_client.types import Response

from benchling_sdk.errors import RegistrationError
from benchling_sdk.helpers.decorators import api_method
from benchling_sdk.helpers.pagination_helpers import NextToken, PageIterator
from benchling_sdk.helpers.response_helpers import model_from_detailed
from benchling_sdk.helpers.retry_helpers import RetryStrategy
from benchling_sdk.services.base_service import BaseService
from benchling_sdk.services.registry_service import RegistryService
from benchling_sdk.services.task_service import TaskService


class OnRegistrationFailure(Protocol):
    def __call__(
        self, service: "CustomEntityService", created_entity: CustomEntity, registration_task: AsyncTask
    ) -> None:
        ...


def _default_on_registration_failure(
    service: "CustomEntityService", created_entity: CustomEntity, registration_task: AsyncTask
) -> None:
    service.archive(entity_ids=[created_entity.id], reason=Reason1.OTHER)


class CustomEntityService(BaseService):
    _registry_service: RegistryService
    _task_service: TaskService

    def __init__(
        self,
        client: Client,
        retry_strategy: RetryStrategy,
        registry_service: RegistryService,
        task_service: TaskService,
    ):
        super().__init__(client, retry_strategy)
        self._registry_service = registry_service
        self._task_service = task_service

    @api_method
    def get_by_id(self, entity_id: str) -> CustomEntity:
        response = get_custom_entity.sync_detailed(client=self.client, custom_entity_id=entity_id)
        return model_from_detailed(response)

    @api_method
    def custom_entities_page(
        self,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        sort: Optional[Sort] = None,
        page_size: Optional[int] = None,
        next_token: NextToken = None,
    ) -> Response[CustomEntityList]:
        return list_custom_entities.sync_detailed(  # type: ignore
            client=self.client,
            schema_id=schema_id,
            modified_at=modified_at,
            name=name,
            name_includes=name_includes,
            folder_id=folder_id,
            mentioned_in=mentioned_in,
            project_id=project_id,
            registry_id=registry_id,
            archive_reason=archive_reason,
            mentions=mentions,
            sort=sort,
            page_size=page_size,
            next_token=next_token,
        )

    def list(
        self,
        schema_id: Optional[str] = None,
        modified_at: Optional[str] = None,
        name: Optional[str] = None,
        name_includes: Optional[str] = None,
        folder_id: Optional[str] = None,
        mentioned_in: Optional[List[str]] = None,
        project_id: Optional[str] = None,
        registry_id: Optional[str] = None,
        archive_reason: Optional[str] = None,
        mentions: Optional[List[str]] = None,
        sort: Optional[Sort] = None,
        page_size: Optional[int] = None,
    ) -> PageIterator[CustomEntity]:
        def api_call(next_token: NextToken) -> Response[CustomEntityList]:
            return self.custom_entities_page(
                schema_id=schema_id,
                modified_at=modified_at,
                name=name,
                name_includes=name_includes,
                folder_id=folder_id,
                mentioned_in=mentioned_in,
                project_id=project_id,
                registry_id=registry_id,
                archive_reason=archive_reason,
                mentions=mentions,
                sort=sort,
                page_size=page_size,
                next_token=next_token,
            )

        def results_extractor(body: CustomEntityList) -> Optional[List[CustomEntity]]:
            return body.custom_entities

        return PageIterator(api_call, results_extractor)

    @api_method
    def create(self, entity: CustomEntityCreate) -> CustomEntity:
        response = create_custom_entity.sync_detailed(client=self.client, json_body=entity)
        return model_from_detailed(response)

    @api_method
    def update(self, entity_id: str, entity: CustomEntityPatch) -> CustomEntity:
        response = update_custom_entity.sync_detailed(
            client=self.client, custom_entity_id=entity_id, json_body=entity
        )
        return model_from_detailed(response)

    @api_method
    def create_and_register(
        self,
        entity: CustomEntityCreate,
        registry_id: str,
        on_failed_registration: OnRegistrationFailure = _default_on_registration_failure,
    ) -> CustomEntity:
        created_entity = self.create(entity)
        task = self._registry_service.register(entity_ids=[created_entity.id], registry_id=registry_id)
        completed_task = self._task_service.wait_for_task(task_id=task.task_id)
        if completed_task.status != Status1.SUCCEEDED:
            on_failed_registration(
                service=self, created_entity=created_entity, registration_task=completed_task
            )
            raise RegistrationError.from_task(completed_task)
        registered_entity = self.get_by_id(created_entity.id)
        return registered_entity

    @api_method
    def archive(self, entity_ids: Iterable[str], reason: Reason1) -> CustomEntityArchivalChange:
        archive_request = CustomEntityArchiveRequest(reason=reason, custom_entity_ids=list(entity_ids))
        response = archive_custom_entities.sync_detailed(client=self.client, json_body=archive_request)
        return model_from_detailed(response)

    @api_method
    def unarchive(self, entity_ids: Iterable[str]) -> CustomEntityArchivalChange:
        unarchive_request = CustomEntityUnarchiveRequest(custom_entity_ids=list(entity_ids))
        response = unarchive_custom_entities.sync_detailed(client=self.client, json_body=unarchive_request)
        return model_from_detailed(response)

    @api_method
    def bulk_get(self, entity_ids: Iterable[str]) -> Optional[List[CustomEntity]]:
        entity_id_string = ",".join(entity_ids)
        response = bulk_get_custom_entities.sync_detailed(
            client=self.client, custom_entity_ids=entity_id_string
        )
        custom_entities = model_from_detailed(response)
        return custom_entities.custom_entities

    @api_method
    def bulk_create(self, entities: Iterable[CustomEntityBaseRequest]) -> AsyncTaskLink:
        # TODO There is a problem with CustomEntityBaseRequest and empty custom_fields.
        # It sends None which causes a bad request on post
        body = CustomEntityBulkCreate(list(entities))
        response = bulk_create_custom_entities.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)

    @api_method
    def bulk_update(self, entities: Iterable[CustomEntityBulkUpdateRequest]) -> AsyncTaskLink:
        body = CustomEntityBulkUpdate(list(entities))
        response = bulk_update_custom_entities.sync_detailed(client=self.client, json_body=body)
        return model_from_detailed(response)
