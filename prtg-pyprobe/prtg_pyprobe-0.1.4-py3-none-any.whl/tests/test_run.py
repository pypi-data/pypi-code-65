import asyncio
import json
import time

from requests import Response

from testfixtures import LogCapture

import prtg_pyprobe.run
from prtg_pyprobe.run import main
from prtg_pyprobe.communication.communication_http_api import PRTGHTTPApi
import prtg_pyprobe.monitoring


def test_run(monkeypatch, mocker):
    monkeypatch.setenv(
        name="PROBE_CONFIG",
        value='{"disable_ssl_verification": false, "log_file_location": "", "log_level": "DEBUG", "probe_access_key": '
        '"miniprobe", "probe_access_key_hashed": "cd7b773e2ce4205e9f5907b157f3d26495c5b373", '
        '"probe_base_interval": "60", "probe_gid": "72C461B5-F768-470B-A1A8-2D5F5DEDDF8F", '
        '"probe_name": "Python Mini Probe UT", "probe_protocol_version": "1", '
        '"prtg_server_ip_dns": "ut.prtg,com", "prtg_server_port": "443"}',
    )
    config = {
        "disable_ssl_verification": False,
        "log_file_location": "",
        "log_level": "DEBUG",
        "probe_access_key": "miniprobe",
        "probe_access_key_hashed": "cd7b773e2ce4205e9f5907b157f3d26495c5b373",
        "probe_base_interval": "60",
        "probe_gid": "72C461B5-F768-470B-A1A8-2D5F5DEDDF8F",
        "probe_name": "Python Mini Probe UT",
        "probe_protocol_version": "1",
        "prtg_server_ip_dns": "ut.prtg,com",
        "prtg_server_port": "443",
    }
    monkeypatch.setattr(PRTGHTTPApi, "send_announce", return_response_200)
    monkeypatch.setattr(PRTGHTTPApi, "get_tasks", return_response_200)
    monkeypatch.setattr(PRTGHTTPApi, "send_data", return_response_200)
    monkeypatch.setattr(Response, "json", return_dict_json)
    monkeypatch.setattr(Response, "json", return_dict_json)
    monkeypatch.setattr(asyncio, "get_event_loop", mock_event_loop)
    monkeypatch.setattr(prtg_pyprobe.monitoring, "monitoring", mock_monitoring)
    monkeypatch.setattr(time, "sleep", return_true)
    with LogCapture() as log:
        main()
    log.check_present(
        ("root", "INFO", "Starting pyprobe!"),
        ("root", "INFO", "Loading configuration"),
        ("root", "INFO", "Config loaded and probe announcing to PRTG"),
        ("root", "DEBUG", f"Your current config: \n {json.dumps(config, indent=2)}"),
        ("root", "INFO", "Initializing SNMP Engine"),
        ("root", "INFO", "Initializing PRTG API"),
        ("root", "INFO", "Initializing Sensors"),
        ("root", "INFO", "Init done!"),
        ("root", "DEBUG", f"Tasks received from PRTG {return_dict_json()}"),
        ("root", "INFO", "Monitoring data successfully sent to PRTG Core."),
    )


def return_response_200(*args, **kwargs):
    resp = Response()
    resp.status_code = 200
    resp._content = (
        b'{"sensorid": "1234", "timeout": 5, "target": "https://example.com","request_type": "GET",'
        b'"acceptable_status_codes": "","headers": "","post_data": "",}'
    )
    return resp


def return_dict_json(*args, **kwargs):
    return [
        {
            "sensorid": "1234",
            "timeout": 5,
            "target": "https://example.com",
            "request_type": "GET",
            "acceptable_status_codes": "",
            "headers": "",
            "post_data": "",
        }
    ]


class MockEventLoop(object):
    @staticmethod
    def run_until_complete(self):
        return "work"

    @staticmethod
    def is_running():
        return False


def mock_event_loop():
    return MockEventLoop()


def return_true(*args, **kwargs):
    return True


def mock_monitoring(*args, **kwargs):
    return True
