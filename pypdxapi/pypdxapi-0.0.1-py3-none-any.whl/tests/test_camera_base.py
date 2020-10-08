"""The tests for the ParadoxCamera."""
import pytest
import requests
import requests_mock

from pypdxapi.camera.base import (ParadoxCamera, ParadoxCameraError)


def fake_api(request, context):
    if request.path == '/get':
        context.status_code = 200
        return 'Success'
    if request.path == '/post' and request.json() == {'a': 'b'}:
        context.status_code = 200
        return 'Success'

    return 'Error'


@pytest.fixture
def client_session() -> requests.Session:
    adapter = requests_mock.Adapter()
    adapter.register_uri('GET', 'mock://127.0.0.1:80/get', text=fake_api)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/post', text=fake_api)

    session = requests.Session()
    session.mount('mock://', adapter)

    return session


def test_api_request(client_session: requests.Session):
    payload = {'a': 'b'}
    base = ParadoxCamera(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    base._url = base._url.with_scheme('mock')

    response = base._api_request(method='GET', endpoint='/get', payload={})
    assert response.text == 'Success'

    response = base._api_request(method='POST', endpoint='/post', payload=payload)
    assert response.text == 'Success'


def test_raise_for_response_error():
    base = ParadoxCamera(host='127.0.0.1', port=80, module_password='paradox')
    base._raise_on_response_error = True

    data = {
        'ResultCode': 1,
        'ResultStr': 'a'
    }
    with pytest.raises(ParadoxCameraError) as err:
        base._raise_for_response_error(data)
        assert f"Error no {data['ResultCode']}: {data['ResultStr']}" == str(err.value)

    with pytest.raises(ParadoxCameraError) as err:
        base._raise_for_response_error({})
        assert "Unknown error occurred while communicating with Paradox camera." == str(err.value)

