#!/usr/bin/env python3
# Author: Federico Sismondi

import re
import logging

from ttproto.core import exceptions
from ttproto.core.data import Value
from ttproto.core.lib.inet.meta import *
from ttproto.core.lib.inet.ip import *
from ttproto.core.data import *
from ttproto.core.packet import *
from ttproto.core.lib.inet import coap
from ttproto.core.lib.inet import http
from ttproto.core.exceptions import Error, DecodeError

from urllib.parse import urlparse

__all__ = [
    "OneM2M",
    "OneM2MRequest",
    "OneM2MResponse",
    "is_oneM2M_HTTP"
]


class Operation:
    CREATE = 'Create'
    RETRIEVE = 'Retrieve'
    UPDATE = 'Update'
    DELETE = 'Delete'
    NOTIFY = 'Notify'


"""

oneM2M requirements:
====================

- get oneM2M dissect representations
- handle different oneM2M bindings


Notes from the oneM2M Standard document (oneM2M Partners Type 1):
=================================================================

              Mca                        Mcc                        Mcc
+----------+  primitives   +----------+  primitives   +----------+  primitives +----------+
|          +-------------->+          +-------------->+          +-------------+          |
|    AE    |               |  MS-CSE  |               |  IN-CSE  |             |   MN-CSE |
|          <---------------+          <---------------+          +<------------+          |
+----------+               +----------+               +----------+             +----------+



               HTTP                      HTTP                      HTTP
+----------+   messages    +----------+  messages     +----------+ messages    +----------+
|  HTTP    +-------------->+  HTTP    +-------------->+  HTTP    +-------------+  HTTP    |
|  Client  |               |  Proxy   |               |  Server  |             |  Server  |
|          <---------------+  Server  <---------------+          +<------------+          |
+----------+               +----------+               +----------+             +----------+



Figure 5.1-1 illustrates an example oneM2M system configuration and its correspondence to an HTTP-based information
system if HTTP binding as defined in this specification is applied.

The upper diagram in figure 5.1-1 shows with solid line arrows the flow of a request primitive originating from an AE
which is registered to an MN-CSE (Registrar of AE).

The request primitive is assumed to address a resource which is hosted by another MN-CSE (Host of Resource).

Both MN-CSEs are registered to the same IN-CSE.

When applying HTTP binding, the oneM2M entities of the upper diagram take the roles outlined in the lower diagram of a
corresponding HTTP information system as defined in IETF RFC 7230 [1].

The AE takes the role of an HTTP client, the MN-CSE (Registrar of AE) takes the role of a HTTP Proxy Server, and both
the IN-CSE and MN-CSE (Host of Resource) take the role of a HTTP server for this particular request message.

CSEs may also issue unsolicited request messages (... ~ in the opposite direction of what the diagram shows) )

Therefore, for HTTP protocol binding, CSEs generally provides capability of both HTTP Server and HTTP Client.

Aes may provide HTTP Server capability optionally in order to be able to serve Notification request messages
(see TS-0004 [3] and TS-0001 [7]).

This clause describes how oneM2M request/response primitives can be mapped to HTTP request/response messages and vice
versa.

Each individual request primitive will be mapped to single HTTP request message, and each individual response primitive
will be mapped to a single HTTP response message, and vice-versa.

An HTTP request message consists of Request-Line, headers and message-body.
An HTTP response message consists of Status-Line, headers and message-body [1].
HTTP header names are case-insensitive and a Receiver shall accept headers that are either lower or upper or any mixture
thereof.

This clause describes how oneM2M request/response primitives are mapped to HTTP messages at a high level.
Corresponding details are specified in clause 6.


Mappings
========
Shall be applied in the following four use cases:
1) Mapping of request primitive to HTTP request message at the request originator (HTTP client)
2) Mapping of HTTP request message to request primitive at the request receiver (HTTP server)
3) Mapping of response primitive to HTTP response message at the request receiver (HTTP server)
4) Mapping of HTTP response message to response primitive at the request originator (HTTP client)

HTTP
====

oneM2M binds to HTTP/1.1 (only)

HTTP headers
=============

Discrimination between Create and Notify operations can be accomplished by inspection of the content-type header.

TL;DR resource type present only for Create Primitive

The Resource Type parameter is present in the content-type header only when the HTTP POST request represents a Create
request (see clause 6.4.3).
The Resource Type parameter is not present in the content-type header when the HTTP POST request represents a Notify
request.

"""

log = logging.getLogger('[oneM2M]')
log.propagate = True  # so AMQP handler (if attached by ancestor) emits logs into the bus


def is_oneM2M_CoAP(value):
    pass


def is_oneM2M_HTTP(value):
    """
    Educated guessing if HTTP is oneM2M.
    Assumes every oneM2M message includes at least one headers starting with 'X-M2M-xxx'

    :param value:
    :return:
    """
    assert issubclass(type(value), http.HTTP), "Not HTTP type"

    if http.get_http_header_by_id(value, 'X-M2M-'):
        log.debug("This is a oneM2M message, found {}".format(http.get_http_header_by_id(value, 'X-M2M-')))
        return True

    log.debug("Not a oneM2M message")
    return False


# def is_oneM2M_request(value):
#     """Checks whether the value is a oneM2M request or not
#     :param value:
#     :return:
#     """
#
#     if type(value) is http.HTTP:
#         if http.get_http_header_by_id(value, 'X-M2M-'):
#             return True
#
#     return False


def _getOperationPrimitive(value):
    """
    Deduces operation primitive from lower layer.

    The HTTP ‘Method’ shall be derived from the Operation request primitive parameter of the request primitive.
    oneM2M Operation

    oneM2M operation    HTTP Method
    ================    ===========
    Create              POST (resource type present in content-type header)
    Retrieve            GET
    Update              PUT
    Delete              DELETE
    Notify              POST (resource type not present in content-type header )

    e.g.
    Content-Type:
    application/vnd.onem2m-res+xml; ty=3 => Resource Type 3
    application/vnd.onem2m-res+json; ty=3 => Resource Type 3
    application/vnd.onem2m-res+cbor; ty=3 => Resource Type 3

    """
    # TODO process notify once we have processor for resourtype/ content type
    # TODO introduce constant / enumerates fir HTTP methods
    if issubclass(type(value), http.HTTP):
        if value['method'] == 'POST':
            return Operation.CREATE
        elif value['method'] == 'GET':
            return Operation.RETRIEVE
        elif value['method'] == 'PUT':
            return Operation.UPDATE
        elif value['method'] == 'DELETE':
            return Operation.DELETE

        raise Exception('Cannot map HTTP method to oneM2M operation <{}> from value {}'.format(value['method'], value))

    raise NotImplementedError('Expecting HTTP message')


def _getToPrimitiveParam(value):
    """
    The path component of the origin-form HTTP Request-Target shall be interpreted as the mapping of the resource
    identifier part of the To request primitive parameter

    :return:
    """

    log.info("type is {}".format(type(value)))
    if isinstance(value, http.HTTP):
        uri = value['uri']
        # re.search(uri, r'^\/~\/')
        if str(uri).startswith('/~/'):
            log.debug("onem2m TO primitive, SP-Relative-Resource-ID")
            return str(uri).replace('/~/', '/')
        elif str(uri).startswith('/_/'):
            log.debug("onem2m TO primitive, Absolute-Resource-ID")
            return str(uri).replace('/_/', '//')
        elif str(uri).startswith('/'):
            log.debug("onem2m TO primitive, CSE-Relative-Resource-ID")
            return str(uri)[1:]
        else:
            log.debug("onem2m TO primitive unknown decode type")
            return None
    else:
        log.debug("NOT inspecting http for onem2m TO primitive")
    return None


def _queryStringTag():
    """
    Deduces oneM2M field from query String
    :return:
    """

    pass


def _getResourceTypePrimitiveParam():
    pass


def _getTokenPrimitiveParamTag():
    """
    6.4.19 Authorization
    If a request primitive includes a Tokens parameter it shall be mapped to the Authorization header.
    The Tokens primitive parameter is represented as a space separated list of JSON Web Signature (JWS) and JSON Web Encryption (JWE) strings in Compact Serialization format of datatype m2m:dynAuthJWT as defined in clause 6.3.3 of TS-0004 [3].
    When mapped into the Authorization header, each individual token in the Tokens primitive parameter shall be separated by ‘+’ character.
    For example, if the Tokens parameter consists of a list of two JWS/JWE Tokens, eyJ0eXAiOiJK.eyJpc3MiOiJqb2UiLA0KIC.dBjftJeZ4CVP
    eyJ0eXAiOiJK.eyJpc3MiOiJqb2UiLA0KIC.dBjftJeZ4CVP.5eym8TW_c8SuK.SdiwkIr3a.XFBoMYUZo
    the Authorization header looks as follows:
    Authorization: eyJ0eXAiOiJK.eyJpc3MiOiJqb2UiLA0KIC.dBjftJeZ4CVP+ eyJ0eXAiOiJK.eyJpc3MiOiJqb2UiL A0KIC.dBjftJeZ4CVP.5eym8TW_c8SuK.SdiwkIr3a.XFBoMYUZo
    The line break in the above example is for illustrative purposes and shall not be included into the Authorization header.

    :return:
    """

    pass


def _getResourceTypePrimitiveParamTag():
    pass


def _getPrimitiveContentTag():
    pass


class HTTPHeader(
    metaclass=InetPacketClass,
    fields=[
        ("field-name", "name", str, ''),
        ("field-value", "value", str, ''),
        ("field-content", "content", bytes, b""),
    ]):

    def __init__(self, *k, **kw):
        if len(k) == 1:
            kw["value"] = k[0]
            k = ()
        super().__init__(*k, **kw)


def _primitiveParamFromHTTPHeaderField(value):
    """ Returns dict of pairs oneM2M primitive param and value
    """
    output_dict = dict()

    # params for oneM2M request
    prim_http_bidict = Bidict({
        'fr': 'X-M2M-Origin',
        'rqi': 'X-M2M-RI',
        'ot': 'X-M2M-OT',
        'rqet': 'X-M2M-RQET',
        'rset': 'X-M2M-RSET',
        'rt': 'X-M2M-RT',
        'rp': 'X-M2M-RP',
        'rcn': 'X-M2M-RCN',
        'ec': 'X-M2M-EC',
        'gid': 'X-M2M-GID',
        'asi': 'X-M2M-ASI',
        'auri': 'X-M2M-AURI',
        'rvi': 'X-M2M-RVI',
        'rsi': 'X-M2M-RSI',
    })

    # params for oneM2M response
    prim_http_bidict.update({
        #'to': 'X-M2M-TO',
        'fr': 'X-M2M-Origin',
        'rqi': 'X-M2M-RI',
        'pc': 'X-M2M-PC',
        'ot': 'X-M2M-OT',
        'rset': 'X-M2M-RSET',
        'ec': 'X-M2M-EC',
        'rsc': 'X-M2M-RSC',
        'ati': 'X-M2M-ATI',
        'tqf': 'X-M2M-TQF',
        'cnst': 'X-M2M-CNST',
        'cnot': 'X-M2M-CNOT',
        'asri': 'X-M2M-ASRI',
        'rvi': 'X-M2M-RVI',
        'rsi': 'X-M2M-RSI',
    })

    if issubclass(type(value), http.HTTP) and value['headers']:
        for header in value['headers']:
            try:
                primitive_k = prim_http_bidict[:header['name']]
                primitive_v = header['value']
                output_dict[primitive_k] = primitive_v
            except KeyError:
                logging.warning("HTTP option is not a oneM2M primitive {}".format(header['name']))

    # ToDo test this
    return output_dict


class oneM2M(
    metaclass=InetPacketClass,
    fields=[
        ("To", "to", str, ''),
    ]):

    @classmethod
    def _decode_from_binding(cls, value: Value):
        """value is parsed and following the right binding rules, a OneM2M value is returned
        :param value:
        :return:
        """

        # TODO make if else for http and coap
        logging.info('decoding oneM2M from {}'.format(value))
        onem2m_values = _primitiveParamFromHTTPHeaderField(value)
        logging.debug('Got http fields: {}'.format(onem2m_values))

        if type(value) is http.HTTPRequest:
            onem2m_values.update({
                'op': _getOperationPrimitive(value),
                'to': _getToPrimitiveParam(value),
            })
            print("onem2m values: {}".format(onem2m_values))
            return OneM2MRequest(**onem2m_values)

        elif type(value) is http.HTTPResponse:

            print("onem2m values: {}".format(onem2m_values))
            return OneM2MResponse(**onem2m_values)

        else:
            raise DecodeError(
                None,
                cls,
                'Couldnt deduce oneM2M type from {}, of type {}'.format(value, type(value))
            )


class oneM2MRequest(
    metaclass=InetPacketClass,
    variant_of=oneM2M,
    prune=-1,
    fields=[
        ("Operation", "op", str, ''),
        ("To", "to", Optional(str), ''),
        ("From", "fr", Optional(str), ''),
        ("RequestIdentifier", "rqi", Optional(str), ''),
        ("ResourceType", "ty", Optional(str), _getResourceTypePrimitiveParamTag()),

        ("RoleIDs", "rids", Optional(str), 'fixMe'),
        ("OriginatingTimestamp", "ot", Optional(str), ''),
        ("RequestExpirationTimestamp", "rqet", Optional(str), ''),
        ("ResultExpirationTimestamp", "rset", Optional(str), ''),
        # Operation Execution Time - oet?
        ("ResponseType", "rt", Optional(str), ''),

        ("ResultPersistence", "rp", Optional(str), ''),
        ("ResultContent", "rcn", Optional(str), ''),

        ("EventCategory", "ec", Optional(str), ''),
        ("DeliveryAggregation", "da", Optional(str), 'fixMe'),
        ("GroupRequestIdentifier", "gid", Optional(str), ''),
        ("FilterCriteria", "fc", Optional(str), 'fixMe'),
        ("DiscoveryResultType", "drt", Optional(str), 'fixMe'),
        ("Tokens", "tkns", Optional(str), _getTokenPrimitiveParamTag()),
        ("TokenIDs", "tids", Optional(str), 'fixMe'),
        ("TokenRequestIndicator", "tqi", Optional(str), 'fixMe'),
        ("LocalTokenIDs", "ltids", Optional(str), 'fixMe'),
        ("GroupRequestTargetMembers", "grtm", Optional(str), 'fixMe'),
        ("AuthorSignIndicator", "asi", Optional(str), ''),

        ("AuthorSign", "aus", Optional(str), 'fixMe'),
        ("AuthorRelIndicator", "auri", Optional(str), ''),
        ("SemanticQueryIndicator", "sqi", Optional(str), 'fixMe'),
        ("ReleaseVersionIndicator", "rvi", Optional(str), ''),
        ("VendorInformation", "rsi", Optional(str), ''),
        ("Content", "pc", Optional(bytes), _getPrimitiveContentTag()),
    ],
):
    def describe(self, desc):
        t = 'oneM2M ({}) - {} {}'.format(
            self['op'],
            self['to'],
            self['rvi'],
        )
        if desc.info:
            desc.info = repr(self)  # '{} | {}'.format(t,desc.info)
        else:
            desc.info = repr(self)  # t

        return True


class oneM2MResponse(
    metaclass=InetPacketClass,
    variant_of=oneM2M,
    prune=-1,
    fields=[
        ("To", "to", Optional(str), ''),
        ("From", "fr", Optional(str), ''),
        ("RequestIdentifier", "rqi", Optional(str), ''),
        ("OriginatingTimestamp", "ot", Optional(str), ''),
        ("ResultExpirationTimestamp", "rset", Optional(str), ''),
        ("EventCategory", "ec", Optional(str), ''),
        ("ResponseStatusCode", "rsc", Optional(str), ''),
        ("AssignedTokenIdentifiers", "ati", Optional(str), ''),
        ("TokenRequestInformation", "tqf", Optional(str), ''),
        ("ContentStatus", "cnst", Optional(str), ''),
        ("ContentOffset", "cnot", Optional(str), ''),
        ("AuthorSignReqInfo", "asri", Optional(str), ''),
        ("ReleaseVersionIndicator", "rvi", Optional(str), ''),
        ("VendorInformation", "rsi", Optional(str), ''),
        ("Content", "pc", Optional(bytes), _getPrimitiveContentTag()),

    ]):
    # descriptions={"pro": ip_next_header_descriptions},

    def describe(self, desc):
        t = 'oneM2M {} : {} -> {} {}'.format(
            self['cnst'],
            self['fr'],
            self['to'],
            self['rvi'],
        )
        if desc.info:
            desc.info = repr(self)  # '{} | {}'.format(t,desc.info)
        else:
            desc.info = repr(self)  # t

        return True


# Aliases
OneM2MRequest = oneM2MRequest
OneM2MResponse = oneM2MResponse
OneM2M = oneM2M
