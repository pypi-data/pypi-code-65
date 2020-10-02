from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import Client
from ...models.container import Container
from ...models.not_found_error import NotFoundError
from ...models.sort1 import Sort1
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort1] = Sort1.MODIFIEDAT,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    archive_reason: Optional[str] = None,
    parent_storage_schema_id: Optional[str] = None,
    assay_run_id: Optional[str] = None,
    checkout_status: Optional[str] = None,
) -> Dict[str, Any]:
    url = "{}/containers".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_sort = sort.value if sort else None

    params: Dict[str, Any] = {}
    if page_size is not None:
        params["pageSize"] = page_size
    if next_token is not None:
        params["nextToken"] = next_token
    if sort is not None:
        params["sort"] = json_sort
    if schema_id is not None:
        params["schemaId"] = schema_id
    if modified_at is not None:
        params["modifiedAt"] = modified_at
    if name is not None:
        params["name"] = name
    if ancestor_storage_id is not None:
        params["ancestorStorageId"] = ancestor_storage_id
    if storage_contents_id is not None:
        params["storageContentsId"] = storage_contents_id
    if archive_reason is not None:
        params["archiveReason"] = archive_reason
    if parent_storage_schema_id is not None:
        params["parentStorageSchemaId"] = parent_storage_schema_id
    if assay_run_id is not None:
        params["assayRunId"] = assay_run_id
    if checkout_status is not None:
        params["checkoutStatus"] = checkout_status

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[Container, None, NotFoundError]]:
    if response.status_code == 200:
        return Container.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 400:
        return None
    if response.status_code == 404:
        return NotFoundError.from_dict(cast(Dict[str, Any], response.json()))
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[Container, None, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort1] = Sort1.MODIFIEDAT,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    archive_reason: Optional[str] = None,
    parent_storage_schema_id: Optional[str] = None,
    assay_run_id: Optional[str] = None,
    checkout_status: Optional[str] = None,
) -> Response[Union[Container, None, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        modified_at=modified_at,
        name=name,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        archive_reason=archive_reason,
        parent_storage_schema_id=parent_storage_schema_id,
        assay_run_id=assay_run_id,
        checkout_status=checkout_status,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort1] = Sort1.MODIFIEDAT,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    archive_reason: Optional[str] = None,
    parent_storage_schema_id: Optional[str] = None,
    assay_run_id: Optional[str] = None,
    checkout_status: Optional[str] = None,
) -> Optional[Union[Container, None, NotFoundError]]:
    """ get a list of containers """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        modified_at=modified_at,
        name=name,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        archive_reason=archive_reason,
        parent_storage_schema_id=parent_storage_schema_id,
        assay_run_id=assay_run_id,
        checkout_status=checkout_status,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort1] = Sort1.MODIFIEDAT,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    archive_reason: Optional[str] = None,
    parent_storage_schema_id: Optional[str] = None,
    assay_run_id: Optional[str] = None,
    checkout_status: Optional[str] = None,
) -> Response[Union[Container, None, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        modified_at=modified_at,
        name=name,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        archive_reason=archive_reason,
        parent_storage_schema_id=parent_storage_schema_id,
        assay_run_id=assay_run_id,
        checkout_status=checkout_status,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort1] = Sort1.MODIFIEDAT,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    archive_reason: Optional[str] = None,
    parent_storage_schema_id: Optional[str] = None,
    assay_run_id: Optional[str] = None,
    checkout_status: Optional[str] = None,
) -> Optional[Union[Container, None, NotFoundError]]:
    """ get a list of containers """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            schema_id=schema_id,
            modified_at=modified_at,
            name=name,
            ancestor_storage_id=ancestor_storage_id,
            storage_contents_id=storage_contents_id,
            archive_reason=archive_reason,
            parent_storage_schema_id=parent_storage_schema_id,
            assay_run_id=assay_run_id,
            checkout_status=checkout_status,
        )
    ).parsed
