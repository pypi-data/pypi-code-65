from typing import Dict

import zeep
from pydantic import AnyHttpUrl
from requests import Session
from zeep import Client
from zeep import Transport
from zeep.helpers import serialize_object


def get_client(wsdl: AnyHttpUrl) -> Client:
    session = Session()
    session.verify = False
    transport = Transport(session=session)
    client = zeep.Client(wsdl=wsdl, transport=transport)
    return client


def call_service(client: Client,  *args, service: str=None) -> Dict:
    """ call service + use default cred + make it a python object """
    credentials = 'anonymous', 'anonymous'
    if service is None:
        service = dir(client.service)[0]

    service_proxy = getattr(client.service, service)
    result = service_proxy(*credentials, *args)
    result = serialize_object(result, target_cls=dict)
    return result


def call(*args, wsdl: AnyHttpUrl) -> Dict:
    client = get_client(wsdl)
    return call_service(client, *args)
