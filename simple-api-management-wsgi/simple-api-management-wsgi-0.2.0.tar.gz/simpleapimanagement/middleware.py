import requests
from data import DataHolder
from werkzeug import exceptions
from flask import request

from werkzeug import Request



class SimpleAPIManagementMiddleware(object):
    def __init__(self, app, options):
        self.app = app

        if options is None:
            raise Exception('Simple API Management API key is required')
        self.options = options

        if options.get('KEY', None):
            self.key = options.get('KEY')
        else:
            raise Exception('Key is required')

        self.metrics = options.get('METRICS', True)
        self.rate_imits = options.get('RATE_LIMITS', True)
        self.identifier = options.get('IDENTIFIER', None)

       
    def __call__(self, environ, start_response):
      
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        host = environ['HTTP_HOST']

        if(self.rate_imits):
            request = {
                'path': path,
                'key': self.key,
                'identifier': self.identifier(environ, self.app),
                'method': method
            }
            
            response = requests.post('https://api.simpleapimanagement.com/ratelimits/validate', json = request)
            if (response.json()['limitReached']):
                return exceptions.TooManyRequests()(environ, start_response)

          
        data_holder = DataHolder()

        def _start_response(status, response_headers, *args):
            data_holder.capture_response_status(status, response_headers)
            return start_response(status, response_headers, *args)

        
        response_chunks = data_holder.finish_response(self.app(environ, _start_response))
        responseTime = data_holder.response_time - data_holder.request_time

        if(self.metrics):
            metric = {
                'key': self.key,
                'host': host,
                'path': path,
                'method': method,
                'statusCode': data_holder.status,
                'latency': responseTime
            }

            # capture metrics
            requests.post('https://api.simpleapimanagement.com/metrics', json = metric)
        
        return response_chunks
