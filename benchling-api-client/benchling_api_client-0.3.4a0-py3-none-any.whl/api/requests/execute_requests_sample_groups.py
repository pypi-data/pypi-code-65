from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import Client
from ...models.bad_request_error import BadRequestError
from ...models.execute_sample_groups_response import ExecuteSampleGroupsResponse
from ...models.not_found_error import NotFoundError
from ...models.sample_groups_status_update import SampleGroupsStatusUpdate
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    request_id: str,
    json_body: SampleGroupsStatusUpdate,
) -> Dict[str, Any]:
    url = "{}/requests/{request_id}:execute-sample-groups".format(client.base_url, request_id=request_id)

    headers: Dict[str, Any] = client.get_headers()

    json_json_body = json_body.to_dict()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
        "json": json_json_body,
    }


def _parse_response(
    *, response: httpx.Response
) -> Optional[Union[ExecuteSampleGroupsResponse, BadRequestError, NotFoundError]]:
    if response.status_code == 200:
        return ExecuteSampleGroupsResponse.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 400:
        return BadRequestError.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 404:
        return NotFoundError.from_dict(cast(Dict[str, Any], response.json()))
    return None


def _build_response(
    *, response: httpx.Response
) -> Response[Union[ExecuteSampleGroupsResponse, BadRequestError, NotFoundError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    request_id: str,
    json_body: SampleGroupsStatusUpdate,
) -> Response[Union[ExecuteSampleGroupsResponse, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_id=request_id,
        json_body=json_body,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    request_id: str,
    json_body: SampleGroupsStatusUpdate,
) -> Optional[Union[ExecuteSampleGroupsResponse, BadRequestError, NotFoundError]]:
    """ Update the status of sample groups in a request """

    return sync_detailed(
        client=client,
        request_id=request_id,
        json_body=json_body,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    request_id: str,
    json_body: SampleGroupsStatusUpdate,
) -> Response[Union[ExecuteSampleGroupsResponse, BadRequestError, NotFoundError]]:
    kwargs = _get_kwargs(
        client=client,
        request_id=request_id,
        json_body=json_body,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    request_id: str,
    json_body: SampleGroupsStatusUpdate,
) -> Optional[Union[ExecuteSampleGroupsResponse, BadRequestError, NotFoundError]]:
    """ Update the status of sample groups in a request """

    return (
        await asyncio_detailed(
            client=client,
            request_id=request_id,
            json_body=json_body,
        )
    ).parsed
