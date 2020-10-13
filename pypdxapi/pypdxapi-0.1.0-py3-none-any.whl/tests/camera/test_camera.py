import pytest
import asyncio
import json
from aiohttp import web, ClientResponseError
from yarl import URL
from datetime import datetime

from pypdxapi.camera.camera import ParadoxCamera
from pypdxapi.exceptions import ParadoxCameraError


async def fake_camera(request: web.Request) -> web.Response:
    content_type = None
    response_data = None

    if request.path == '/timeout':
        await asyncio.sleep(2)
    if request.path == '/audio':
        content_type = 'audio/x-mpegURL'
        response_data = b'm3u8'
    if request.path == '/json':
        content_type = 'application/json'
        payload = await request.json()
        response_data = json.dumps(
            {
                "ResultCode": 1,
                "ResultStr": payload['ResultStr']
            }
        )

    response = web.Response()
    response.content_type = content_type
    response.body = response_data

    return response


@pytest.fixture
def client_session(loop, aiohttp_client):
    app = web.Application()
    app.router.add_post('/timeout', fake_camera)
    app.router.add_post('/audio', fake_camera)
    app.router.add_post('/json', fake_camera)

    return loop.run_until_complete(aiohttp_client(app))


def get_camera(session, module_password: str = 'paradox', **kwargs):
    camera = ParadoxCamera(host='127.0.0.1', port=80, module_password=module_password,
                           client_session=session, **kwargs)
    camera._url = URL.build()

    return camera


async def test_is_authenticated():
    camera = get_camera(None)

    assert not camera.is_authenticated()

    camera._session_key = '_session_key'
    assert not camera.is_authenticated()

    camera._last_api_call = datetime.now()
    assert camera.is_authenticated()

    await asyncio.sleep(2)
    assert not camera.is_authenticated(timeout=1)


async def test_async_api_request_404(client_session):
    camera = get_camera(client_session)

    with pytest.raises(ClientResponseError):
        await camera.api_request(method='POST', endpoint='/404', payload={})


async def test_async_api_request_timeout(client_session):
    camera = get_camera(client_session, request_timeout=1)

    with pytest.raises(asyncio.TimeoutError):
        await camera.api_request(method='POST', endpoint='/timeout', payload={})


async def test_async_api_request_audio(client_session):
    camera = get_camera(client_session)

    response = await camera.api_request(method='POST', endpoint='/audio', payload={})
    assert response == 'm3u8'


async def test_async_api_request_json(client_session):
    camera = get_camera(client_session)

    payload = {
        "ResultStr": 'Success'
    }
    response = await camera.api_request(method='POST', endpoint='/json', payload=payload)
    assert response['ResultCode'] == 1
    assert response['ResultStr'] == payload['ResultStr']


def test_parse_response():
    camera = get_camera(None)

    response = {
        "ResultCode": 1,
        "ResultStr": 'Success'
    }

    data = camera._parse_response(response, None)
    assert data['ResultCode'] == 1
    assert data['ResultStr'] == 'Success'

    data = camera._parse_response(response, 1)
    assert data['ResultCode'] == 1
    assert data['ResultStr'] == 'Success'

    response.pop('ResultCode')
    data = camera._parse_response(response, 1)
    assert data['ResultCode'] == -1
    assert data['ResultStr'] == 'Unknown error occurred while communicating with Paradox camera.'

    camera._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        camera._parse_response(response, 1)
