"""The tests for the Paradox HD77 camera."""
import os
import pytest
from aiohttp import web
from yarl import URL

from pypdxapi.exceptions import ParadoxCameraError
from pypdxapi.camera.hd77 import ParadoxHD77


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures/hd77', filename)
    with open(path) as fptr:
        return fptr.read()


async def fake_hd77(request: web.Request) -> web.Response:
    content_type = 'application/json'

    payload = await request.json()
    response_data = None

    if 'SessionKey' not in payload:
        if request.path == '/app/login':
            if payload['UserCode'] == '010101' and payload['UserName'] == 'user001':
                response_data = load_fixture('login.json')
            else:
                response_data = load_fixture('invalid_username.json')
        if request.path == '/app/pingstatus':
            if payload['ServerPassword'] == 'paradox':
                response_data = load_fixture('pingstatus.json')
            else:
                response_data = load_fixture('invalid_server_password.json')
    else:
        if payload['SessionKey'] == 'qeQHCBgRXSEKUNEcbNMBxCt_Jeh67gLk':
            if request.path == '/app/getstatus':
                response_data = load_fixture('getstatus.json')
            if request.path == '/app/rod':
                response_data = load_fixture('rod.json')
            if request.path == '/app/areacontrol':
                response_data = load_fixture('areacontrol.json')
            if request.path == '/fil/getitemlist':
                response_data = load_fixture('getitemlist.json')
            if request.path == '/fil/deleteitem':
                if payload['ItemId'] == '45fcc296-2718-4519-a1e9-59d016c4ce8a':
                    response_data = load_fixture('deleteitem.json')
                else:
                    response_data = load_fixture('invalid_item_id.json')
            if request.path == '/fil/playback':
                if payload['ItemId'] == '45fcc296-2718-4519-a1e9-59d016c4ce8a':
                    response_data = load_fixture('playback.json')
                else:
                    response_data = load_fixture('invalid_item_id.json')
            if request.path == '/fil/getthumbnail':
                content_type = 'application/octet-stream'
                response_data = 'Image'
            if request.path == '/hls/vod':
                content_type = 'audio/x-mpegURL'
                response_data = 'm3u8'
        else:
            response_data = load_fixture('invalid_session_key.json')

    response = web.Response()
    response.content_type = content_type
    response.body = response_data

    return response


@pytest.fixture
def client_session(loop, aiohttp_client):
    app = web.Application()
    app.router.add_post('/app/login', fake_hd77)
    app.router.add_post('/app/pingstatus', fake_hd77)
    app.router.add_post('/app/getstatus', fake_hd77)
    app.router.add_post('/app/rod', fake_hd77)
    app.router.add_post('/app/areacontrol', fake_hd77)

    app.router.add_post('/fil/getitemlist', fake_hd77)
    app.router.add_post('/fil/deleteitem', fake_hd77)
    app.router.add_post('/fil/playback', fake_hd77)
    app.router.add_post('/fil/getthumbnail', fake_hd77)

    app.router.add_post('/hls/vod', fake_hd77)

    return loop.run_until_complete(aiohttp_client(app))


def get_camera(session, module_password: str = 'paradox', **kwargs):
    camera = ParadoxHD77(host='127.0.0.1', port=80, module_password=module_password,
                         client_session=session, **kwargs)
    camera._url = URL.build()

    return camera


async def test_login(client_session):
    hd77 = get_camera(client_session)

    assert not hd77.is_authenticated()

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    assert hd77.name == 'Camera 1'
    assert hd77.model == 'HD77'
    assert hd77.version == 'v1.25.7'
    assert hd77.serial == 'e0000002'
    assert hd77.session_key == 'qeQHCBgRXSEKUNEcbNMBxCt_Jeh67gLk'

    hd77.logout()
    assert not hd77.is_authenticated()

    hd77._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        await hd77.login(usercode='error', username='error')
        assert not hd77.is_authenticated()


async def test_pingstatus(client_session):
    hd77 = get_camera(client_session)

    data = await hd77.pingstatus()
    assert data['ResultStr'] == 'Ping status request successful'

    hd77 = get_camera(client_session, module_password='error')

    data = await hd77.pingstatus()
    assert data['ResultStr'] == 'Login refused, invalid server password'

    hd77._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        await hd77.pingstatus()


async def test_getstatus(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.getstatus(status_type=1)
    assert data['ResultStr'] == 'Get status request successful'


async def test_rod(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.rod()
    assert data['ResultStr'] == 'ROD request successful'


async def test_areacontrol(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.areacontrol([{"ForceZones": False, "AreaCommand": 6, "AreaID": 1}])
    assert data['Areas'][0]['OpResultCode'] == 34209792


async def test_getitemlist(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.getitemlist()
    assert data['ResultStr'] == 'Browse, request successful'


async def test_deleteitem(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.deleteitem('45fcc296-2718-4519-a1e9-59d016c4ce8a')
    assert data['ResultStr'] == 'Item delete, request successful'

    data = await hd77.deleteitem('error')
    assert data['ResultStr'] == 'Item play failed, invalid item id'

    hd77._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        await hd77.deleteitem('error')


async def test_playback(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.playback('45fcc296-2718-4519-a1e9-59d016c4ce8a')
    assert data['ResultStr'] == 'Item playback, request successful'

    data = await hd77.playback('error')
    assert data['ResultStr'] == 'Item play failed, invalid item id'

    hd77._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        await hd77.playback('error')


async def test_getthumbnail(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.getthumbnail()
    assert data == 'Image'

    hd77.logout()
    assert not hd77.is_authenticated()

    data = await hd77.getthumbnail()
    assert data['ResultStr'] == 'Request failed, invalid session key'

    hd77._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        await hd77.getthumbnail()


async def test_vod(client_session):
    hd77 = get_camera(client_session)

    await hd77.login(usercode='010101', username='user001')
    assert hd77.is_authenticated()

    data = await hd77.vod(action=1, channel_type='normal')
    assert data == 'm3u8'

    hd77.logout()
    assert not hd77.is_authenticated()

    data = await hd77.vod()
    assert data['ResultStr'] == 'Request failed, invalid session key'

    hd77._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        await hd77.vod()
