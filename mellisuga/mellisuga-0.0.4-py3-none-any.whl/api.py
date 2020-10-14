import json
import decimal
from .request import Request
from .response import Response
from .errors import MellisugaError


class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, decimal.Decimal):
            return str(o)
        return super(DecimalEncoder, self).default(o)


class Api(object):
    supported = ['rest', 'ws']
    new_request = Request
    new_response = Response

    def __init__(self, event, context):
        self.event = event
        self.context = context
        self.method = None
        if 'httpMethod' in event:
            self.api = 'rest'
            self.method = event['httpMethod']
        else:
            self.api = 'ws'
        self.ws_id = None

    def _validate_headers(self, headers):
        for header, value in headers.items():
            if '\n' in value:
                raise MellisugaError("Bad value for header '%s': %r" %
                                     (header, value))

    def _request_ws(self):
        """ Will raise a KeyErro if expectet parameter are missing """
        body = json.loads(self.event['body'])
        self.ws_id = body.get('id', 0)

        return self.new_request(
            data=body.get('data', None),
            auth=self.event.get('requestContext', {}).get('authorizer', None) or {},
            params=body.get('params', None),
            route=body['action']
        )

    def _request_rest(self):
        """ Will raise a KeyErro if expectet parameter are missing """
        # TODO Check for base64 encoding

        # more than one location for parameter, merge them
        params = self.event.get('pathParameters', None) or {}
        params.update(self.event.get('queryStringParameters', None) or {})
        return self.new_request(
            data=self.event['body'],
            params=params,
            auth=self.event.get('requestContext', {}).get('authorizer', None) or {},
            headers=self.event.get('headers', None),
            route=self.event.get('path', None)
        )

    def request(self):
        return getattr(self, '_request_'+self.api)()

    def _response_ws(self, response):
        return {
            'statusCode': response.status_code,
            'body': json.dumps({
                'data': response.data,
                'id': self.ws_id,
                'status_code': response.status_code
            }, cls=DecimalEncoder)
        }

    def _response_rest(self, response):
        self._validate_headers(response.headers)
        return {
            'statusCode': response.status_code,
            'body': response.data_as_string(),
            'headers': response.headers
        }

    def response(self, response):
        return getattr(self, '_response_'+self.api)(response)
