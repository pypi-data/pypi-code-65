from typing import Any, Dict, Optional, Union, cast

import httpx

from ...client import Client
from ...models.async_task_link import AsyncTaskLink
from ...models.bad_request_error import BadRequestError
from ...types import Response


def _get_kwargs(
    *,
    client: Client,
    input_generator_id: str,
) -> Dict[str, Any]:
    url = "{}/automation-input-generators/{input_generator_id}:generate-input".format(
        client.base_url, input_generator_id=input_generator_id
    )

    headers: Dict[str, Any] = client.get_headers()

    return {
        "url": url,
        "headers": headers,
        "cookies": client.get_cookies(),
        "timeout": client.get_timeout(),
    }


def _parse_response(*, response: httpx.Response) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    if response.status_code == 200:
        return AsyncTaskLink.from_dict(cast(Dict[str, Any], response.json()))
    if response.status_code == 400:
        return BadRequestError.from_dict(cast(Dict[str, Any], response.json()))
    return None


def _build_response(*, response: httpx.Response) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    return Response(
        status_code=response.status_code,
        content=response.content,
        headers=response.headers,
        parsed=_parse_response(response=response),
    )


def sync_detailed(
    *,
    client: Client,
    input_generator_id: str,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        input_generator_id=input_generator_id,
    )

    response = httpx.post(
        **kwargs,
    )

    return _build_response(response=response)


def sync(
    *,
    client: Client,
    input_generator_id: str,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """  """

    return sync_detailed(
        client=client,
        input_generator_id=input_generator_id,
    ).parsed


async def asyncio_detailed(
    *,
    client: Client,
    input_generator_id: str,
) -> Response[Union[AsyncTaskLink, BadRequestError]]:
    kwargs = _get_kwargs(
        client=client,
        input_generator_id=input_generator_id,
    )

    async with httpx.AsyncClient() as _client:
        response = await _client.post(**kwargs)

    return _build_response(response=response)


async def asyncio(
    *,
    client: Client,
    input_generator_id: str,
) -> Optional[Union[AsyncTaskLink, BadRequestError]]:
    """  """

    return (
        await asyncio_detailed(
            client=client,
            input_generator_id=input_generator_id,
        )
    ).parsed
