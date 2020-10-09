"""The tests for the ParadoxCamera."""
import json
import pytest
import requests
import requests_mock

from pypdxapi.camera.camera import (ParadoxCamera, ParadoxCameraError)


def fake_api(request, context):
    content_type = 'application/json'
    status_code = 200
    data = None

    if request.path == '/404':
        content_type = 'text/html'
        status_code = 404
        data = '404'
    if request.path == '/not_application_json':
        content_type = 'audio/x-mpegURL'
        data = 'm3u8'
    if request.path == '/application_json':
        payload = request.json()
        if payload['RequestCode'] == 1:
            data = json.dumps(
                {
                    "ResultCode": 101010,
                    "ResultStr": 'Success'
                }
            )
        if payload['RequestCode'] == 2:
            data = json.dumps(
                {
                    "ResultStr": 'Success'
                }
            )

    context.headers['Content-Type'] = content_type
    context.status_code = status_code
    return data


@pytest.fixture
def client_session() -> requests.Session:
    adapter = requests_mock.Adapter()
    adapter.register_uri('POST', 'mock://127.0.0.1:80/404', text=fake_api)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/not_application_json', text=fake_api)
    adapter.register_uri('POST', 'mock://127.0.0.1:80/application_json', text=fake_api)

    session = requests.Session()
    session.mount('mock://', adapter)

    return session


def test_api_request_404(client_session: requests.Session):
    base = ParadoxCamera(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    base._url = base._url.with_scheme('mock')

    with pytest.raises(requests.exceptions.HTTPError):
        base.api_request(method='POST', endpoint='/404', payload={})


def test_api_request_not_json(client_session: requests.Session):
    base = ParadoxCamera(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    base._url = base._url.with_scheme('mock')

    response = base.api_request(method='POST', endpoint='/not_application_json', payload={})
    assert response == b'm3u8'


def test_api_request_json(client_session: requests.Session):
    base = ParadoxCamera(host='127.0.0.1', port=80, module_password='paradox', session=client_session)
    base._url = base._url.with_scheme('mock')

    # 'ResultCode' in data
    payload = {"RequestCode": 1}
    base._raise_on_response_error = False

    # result_code is None
    response = base.api_request(method='POST', endpoint='/application_json', payload=payload)
    assert response['ResultStr'] == 'Success'

    # result_code == ResultCode
    response = base.api_request(method='POST', endpoint='/application_json', payload=payload, result_code=101010)
    assert response['ResultStr'] == 'Success'

    # result_code != ResultCode
    base._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError) as err:
        base.api_request(method='POST', endpoint='/application_json', payload=payload, result_code=202020)
        assert 'Error no 101010: Success' == str(err.value)

    # 'ResultCode' NOT in data
    payload = {"RequestCode": 2}
    base._raise_on_response_error = False

    # result_code is None
    response = base.api_request(method='POST', endpoint='/application_json', payload=payload)
    assert response['ResultStr'] == 'Success'

    response = base.api_request(method='POST', endpoint='/application_json', payload=payload, result_code=101010)
    assert response['ResultStr'] == 'Unknown error occurred while communicating with Paradox camera.'

    base._raise_on_response_error = True
    with pytest.raises(ParadoxCameraError) as err:
        base.api_request(method='POST', endpoint='/application_json', payload=payload, result_code=101010)
        assert 'Unknown error occurred while communicating with Paradox camera.' == str(err.value)
