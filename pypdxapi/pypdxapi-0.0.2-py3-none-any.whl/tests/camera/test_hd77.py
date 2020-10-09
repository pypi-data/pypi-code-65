"""The tests for the Paradox HD77 camera."""
import os
import pytest
import requests
import requests_mock

from pypdxapi.exceptions import ParadoxCameraError
from pypdxapi.camera.hd77 import ParadoxHD77


def load_fixture(filename):
    """Load a fixture."""
    path = os.path.join(os.path.dirname(__file__), 'fixtures/hd77', filename)
    with open(path) as fptr:
        return fptr.read()


def fake_api(request, context):
    if request.path == '/get':
        context.status_code = 200
        return 'Success'
    if request.path == '/post' and request.json() == {'a': 'b'}:
        context.status_code = 200
        return 'Success'

    return 'Error'


def fake_hd77cam(request, context):
    content_type = 'application/json'
    status_code = 200

    json = request.json()
    data = None

    if 'SessionKey' in json:
        if json['SessionKey'] == 'qeQHCBgRXSEKUNEcbNMBxCt_Jeh67gLk':
            if request.path == '/app/getstatus':
                data = load_fixture('getstatus.json')
            if request.path == '/app/rod':
                data = load_fixture('rod.json')
            if request.path == '/app/areacontrol':
                data = load_fixture('areacontrol.json')
            if request.path == '/fil/getitemlist':
                data = load_fixture('getitemlist.json')
            if request.path == '/fil/deleteitem':
                if json['ItemId'] == '45fcc296-2718-4519-a1e9-59d016c4ce8a':
                    data = load_fixture('deleteitem.json')
                else:
                    data = load_fixture('invalid_item_id.json')
            if request.path == '/fil/playback':
                if json['ItemId'] == '45fcc296-2718-4519-a1e9-59d016c4ce8a':
                    data = load_fixture('playback.json')
                else:
                    data = load_fixture('invalid_item_id.json')
            if request.path == '/fil/getthumbnail':
                content_type = 'application/octet-stream'
                data = 'Image'
            if request.path == '/hls/vod':
                content_type = 'audio/x-mpegURL'
                data = 'm3u8'
        else:
            data = load_fixture('invalid_session_key.json')
    else:
        if request.path == '/app/login':
            if json['UserCode'] == '010101' and json['UserName'] == 'user001':
                data = load_fixture('login.json')
            else:
                data = load_fixture('invalid_username.json')
        if request.path == '/app/pingstatus':
            if json['ServerPassword'] == 'paradox':
                data = load_fixture('pingstatus.json')
            else:
                data = load_fixture('invalid_server_password.json')

    context.headers['Content-Type'] = content_type
    context.status_code = status_code
    return data


@pytest.fixture
def client_session() -> requests.Session:
    adapter = requests_mock.Adapter()
    adapter.register_uri('POST', 'mock://127.0.0.1:80/app/login', text=fake_hd77cam)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/app/pingstatus', text=fake_hd77cam)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/app/getstatus', text=fake_hd77cam)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/app/rod', text=fake_hd77cam)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/app/areacontrol', text=fake_hd77cam)

    adapter.register_uri('POST', 'mock://127.0.0.1:80/fil/getitemlist', text=fake_hd77cam)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/fil/deleteitem', text=fake_hd77cam)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/fil/playback', text=fake_hd77cam)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/fil/getthumbnail', text=fake_hd77cam)

    adapter.register_uri('POST', 'mock://127.0.0.1:80/hls/vod', text=fake_hd77cam)

    session = requests.Session()
    session.mount('mock://', adapter)

    return session


def test_login(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    cam.login(usercode='010101', username='user001')
    assert cam.name == 'Camera 1'
    assert cam.model == 'HD77'
    assert cam.version == 'v1.25.7'
    assert cam.serial == 'e0000002'
    assert cam.session_key == 'qeQHCBgRXSEKUNEcbNMBxCt_Jeh67gLk'

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.login(usercode='error', username='error')


def test_pingstatus(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    data = cam.pingstatus()
    assert data['ResultStr'] == 'Ping status request successful'

    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='error', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    data = cam.pingstatus()
    assert data['ResultStr'] == 'Login refused, invalid server password'

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.pingstatus()


def test_getstatus(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    data = cam.getstatus(status_type=1)
    assert data['ResultStr'] == 'Request failed, invalid session key'

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.getstatus(status_type=1)

    cam.login(usercode='010101', username='user001')
    data = cam.getstatus(status_type=1)
    assert data['ResultStr'] == 'Get status request successful'


def test_rod(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.rod()

    cam.login(usercode='010101', username='user001')
    data = cam.rod()
    assert data['ResultStr'] == 'ROD request successful'


def test_areacontrol(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    data = cam.areacontrol([{"ForceZones": False, "AreaCommand": 6, "AreaID": 1}])
    assert data['ResultStr'] == 'Request failed, invalid session key'

    cam.login(usercode='010101', username='user001')
    data = cam.areacontrol([{"ForceZones": False, "AreaCommand": 6, "AreaID": 1}])
    assert data['Areas'][0]['OpResultCode'] == 34209792


def test_getitemlist(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.getitemlist()

    cam.login(usercode='010101', username='user001')
    data = cam.getitemlist()
    assert data['ResultStr'] == 'Browse, request successful'


def test_deleteitem(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')
    cam.login(usercode='010101', username='user001')

    data = cam.deleteitem('45fcc296-2718-4519-a1e9-59d016c4ce8a')
    assert data['ResultStr'] == 'Item delete, request successful'

    data = cam.playback('error')
    assert data['ResultStr'] == 'Item play failed, invalid item id'

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.playback('error')


def test_playback(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')
    cam.login(usercode='010101', username='user001')

    data = cam.playback('45fcc296-2718-4519-a1e9-59d016c4ce8a')
    assert data['ResultStr'] == 'Item playback, request successful'

    data = cam.playback('error')
    assert data['ResultStr'] == 'Item play failed, invalid item id'


def test_getthumbnail(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.getthumbnail()

    cam.login(usercode='010101', username='user001')
    data = cam.getthumbnail()
    assert data == b'Image'


def test_vod(client_session):
    cam = ParadoxHD77(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    cam._url = cam._url.with_scheme('mock')

    cam._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError):
        cam.vod()

    cam.login(usercode='010101', username='user001')
    data = cam.vod(action=1, channel_type='normal')
    assert data == b'm3u8'
