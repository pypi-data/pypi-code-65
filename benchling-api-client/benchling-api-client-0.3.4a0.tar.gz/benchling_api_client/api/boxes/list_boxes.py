from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.box_list import BoxList
from ...models.sort import Sort
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort] = Sort.MODIFIEDATDESC,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    empty_positions: Optional[int] = None,
    empty_positionsgte: Optional[int] = None,
    empty_containers: Optional[int] = None,
    empty_containersgte: Optional[int] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    storage_contents_ids: Optional[str] = None,
    archive_reason: Optional[str] = None,
) -> Dict[str, Any]:
    url = "{}/boxes".format(client.base_url)

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
    if empty_positions is not None:
        params["emptyPositions"] = empty_positions
    if empty_positionsgte is not None:
        params["emptyPositions.gte"] = empty_positionsgte
    if empty_containers is not None:
        params["emptyContainers"] = empty_containers
    if empty_containersgte is not None:
        params["emptyContainers.gte"] = empty_containersgte
    if ancestor_storage_id is not None:
        params["ancestorStorageId"] = ancestor_storage_id
    if storage_contents_id is not None:
        params["storageContentsId"] = storage_contents_id
    if storage_contents_ids is not None:
        params["storageContentsIds"] = storage_contents_ids
    if archive_reason is not None:
        params["archiveReason"] = archive_reason

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[BoxList, BadRequestError]]:
    if response.status_code == 200:
        return BoxList.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 400:
        return BadRequestError.from_dict(cast(Dict[str, Any], response.json()))
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[BoxList, BadRequestError]]:
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
    sort: Optional[Sort] = Sort.MODIFIEDATDESC,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    empty_positions: Optional[int] = None,
    empty_positionsgte: Optional[int] = None,
    empty_containers: Optional[int] = None,
    empty_containersgte: Optional[int] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    storage_contents_ids: Optional[str] = None,
    archive_reason: Optional[str] = None,
) -> Response[Union[BoxList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        modified_at=modified_at,
        name=name,
        empty_positions=empty_positions,
        empty_positionsgte=empty_positionsgte,
        empty_containers=empty_containers,
        empty_containersgte=empty_containersgte,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
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
    sort: Optional[Sort] = Sort.MODIFIEDATDESC,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    empty_positions: Optional[int] = None,
    empty_positionsgte: Optional[int] = None,
    empty_containers: Optional[int] = None,
    empty_containersgte: Optional[int] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    storage_contents_ids: Optional[str] = None,
    archive_reason: Optional[str] = None,
) -> Optional[Union[BoxList, BadRequestError]]:
    """ List boxes """

    return sync_detailed(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        modified_at=modified_at,
        name=name,
        empty_positions=empty_positions,
        empty_positionsgte=empty_positionsgte,
        empty_containers=empty_containers,
        empty_containersgte=empty_containersgte,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort] = Sort.MODIFIEDATDESC,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    empty_positions: Optional[int] = None,
    empty_positionsgte: Optional[int] = None,
    empty_containers: Optional[int] = None,
    empty_containersgte: Optional[int] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    storage_contents_ids: Optional[str] = None,
    archive_reason: Optional[str] = None,
) -> Response[Union[BoxList, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        page_size=page_size,
        next_token=next_token,
        sort=sort,
        schema_id=schema_id,
        modified_at=modified_at,
        name=name,
        empty_positions=empty_positions,
        empty_positionsgte=empty_positionsgte,
        empty_containers=empty_containers,
        empty_containersgte=empty_containersgte,
        ancestor_storage_id=ancestor_storage_id,
        storage_contents_id=storage_contents_id,
        storage_contents_ids=storage_contents_ids,
        archive_reason=archive_reason,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    page_size: Optional[int] = 50,
    next_token: Optional[str] = None,
    sort: Optional[Sort] = Sort.MODIFIEDATDESC,
    schema_id: Optional[str] = None,
    modified_at: Optional[str] = None,
    name: Optional[str] = None,
    empty_positions: Optional[int] = None,
    empty_positionsgte: Optional[int] = None,
    empty_containers: Optional[int] = None,
    empty_containersgte: Optional[int] = None,
    ancestor_storage_id: Optional[str] = None,
    storage_contents_id: Optional[str] = None,
    storage_contents_ids: Optional[str] = None,
    archive_reason: Optional[str] = None,
) -> Optional[Union[BoxList, BadRequestError]]:
    """ List boxes """

    return (
        await asyncio_detailed(
            client=client,
            page_size=page_size,
            next_token=next_token,
            sort=sort,
            schema_id=schema_id,
            modified_at=modified_at,
            name=name,
            empty_positions=empty_positions,
            empty_positionsgte=empty_positionsgte,
            empty_containers=empty_containers,
            empty_containersgte=empty_containersgte,
            ancestor_storage_id=ancestor_storage_id,
            storage_contents_id=storage_contents_id,
            storage_contents_ids=storage_contents_ids,
            archive_reason=archive_reason,
        )
    ).parsed
