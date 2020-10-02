from typing import Any, Dict, Optional, cast

import httpx

from ...client import Client
from ...models.folder_list import FolderList
from ...models.sort import Sort
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    next_token: Optional[str] = None,
    page_size: Optional[int] = 50,
    sort: Optional[Sort] = Sort.NAME,
    archive_reason: Optional[str] = None,
    name_includes: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Dict[str, Any]:
    url = "{}/folders".format(client.base_url)

    headers: Dict[str, Any] = client.get_headers()

    json_sort = sort.value if sort else None

    params: Dict[str, Any] = {}
    if next_token is not None:
        params["nextToken"] = next_token
    if page_size is not None:
        params["pageSize"] = page_size
    if sort is not None:
        params["sort"] = json_sort
    if archive_reason is not None:
        params["archiveReason"] = archive_reason
    if name_includes is not None:
        params["nameIncludes"] = name_includes
    if parent_folder_id is not None:
        params["parentFolderId"] = parent_folder_id
    if project_id is not None:
        params["projectId"] = project_id

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "params": params,
    }


def _parse_response(*, response: httpx.Response) -> Optional[FolderList]:
    if response.status_code == 200:
        return FolderList.from_dict(cast(Dict[str, Any], response.json()))
    return None


def _build_response(*, response: httpx.Response) -> Response[FolderList]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    next_token: Optional[str] = None,
    page_size: Optional[int] = 50,
    sort: Optional[Sort] = Sort.NAME,
    archive_reason: Optional[str] = None,
    name_includes: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Response[FolderList]:
    kwargs = _get_kwargs(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        archive_reason=archive_reason,
        name_includes=name_includes,
        parent_folder_id=parent_folder_id,
        project_id=project_id,
    )

    response = httpx.get(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    next_token: Optional[str] = None,
    page_size: Optional[int] = 50,
    sort: Optional[Sort] = Sort.NAME,
    archive_reason: Optional[str] = None,
    name_includes: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Optional[FolderList]:
    """  """

    return sync_detailed(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        archive_reason=archive_reason,
        name_includes=name_includes,
        parent_folder_id=parent_folder_id,
        project_id=project_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    next_token: Optional[str] = None,
    page_size: Optional[int] = 50,
    sort: Optional[Sort] = Sort.NAME,
    archive_reason: Optional[str] = None,
    name_includes: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Response[FolderList]:
    kwargs = _get_kwargs(
        client=client,
        next_token=next_token,
        page_size=page_size,
        sort=sort,
        archive_reason=archive_reason,
        name_includes=name_includes,
        parent_folder_id=parent_folder_id,
        project_id=project_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.get(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    next_token: Optional[str] = None,
    page_size: Optional[int] = 50,
    sort: Optional[Sort] = Sort.NAME,
    archive_reason: Optional[str] = None,
    name_includes: Optional[str] = None,
    parent_folder_id: Optional[str] = None,
    project_id: Optional[str] = None,
) -> Optional[FolderList]:
    """  """

    return (
        await asyncio_detailed(
            client=client,
            next_token=next_token,
            page_size=page_size,
            sort=sort,
            archive_reason=archive_reason,
            name_includes=name_includes,
            parent_folder_id=parent_folder_id,
            project_id=project_id,
        )
    ).parsed
