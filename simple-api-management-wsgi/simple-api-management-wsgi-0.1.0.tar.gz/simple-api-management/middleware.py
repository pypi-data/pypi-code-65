import requests
from data import DataHolder
from werkzeug import exceptions
from flask import request

from werkzeug import Request



class SimpleAPIManagementMiddleware(object):
    #def __init__(self, app,test, options):
    def __init__(self, app, options):
        self.app = app
        #self.test = test

        #print('rules')
        #for rule in test.url_map.iter_rules():
        #    print(rule)
       

        if options is None:
            raise Exception('Simple API Management API key is required')
        self.options = options

        if options.get('KEY', None):
            self.key = options.get('KEY')
        else:
            raise Exception('Key is required')

        self.metrics = options.get('METRICS', True)
        self.rate_imits = options.get('RATE_LIMITS', True)
        
        ## TODO how do we do this with param or body???
        # and not only the environment 
        self.identifier = options['IDENTIFIER']
     
        # todo check for api key


    def __call__(self, environ, start_response):

       
        #finally:
        #    if hasattr(iterable, 'close'):
        #        iterable.close()
                
      
        method = environ['REQUEST_METHOD']
        path = environ['PATH_INFO']
        host = environ['HTTP_HOST']

        print(environ)

        request = Request(environ)
        #urls = self.test.url_map.bind_to_environ(environ)

        #with self.test.request_context(environ) as ctx:
        #    print(ctx.request.url_rule)

        if(self.rate_imits):
            request = {
                'path': path,
                'key': self.key,
                'identifier': 'todo',
                'method': method
            }
            
            response = requests.post('https://api.simpleapimanagement.com/ratelimits/validate', json = request)
            
            if (response.json()['limitReached']):
                return exceptions.TooManyRequests()(environ, start_response)

            

        data_holder = DataHolder()

        def _start_response(status, response_headers, *args):
            print(args)
            data_holder.capture_response_status(status, response_headers)
            return start_response(status, response_headers, *args)

        # better solution?
        #return self.app(environ, _start_response)
        
        response_chunks = data_holder.finish_response(self.app(environ, _start_response))

   

        print(data_holder.response_headers)
        responseTime = data_holder.response_time - data_holder.request_time

        if(self.metrics):
            print('send metrics')
            metric = {
                'key': self.key,
                'host': host,
                'path': path,
                'method': method,
                'statusCode': 200,
                'latency': responseTime
            }

            # capture metrics
            requests.post('https://api.simpleapimanagement.com/metrics', json = metric)
        
        return response_chunks
