import logging
import traceback
from .api import Api
from .errors import MellisugaViewError
from functools import wraps
from collections import defaultdict


class Mellisuga(object):
    FORMAT_STRING = '%(name)s - %(levelname)s - %(message)s'

    def __init__(self, app_name, default_route=None, debug=False, api=Api):
        self.app_name = app_name
        self._debug = debug
        self.log = logging.getLogger(self.app_name)
        self.default_route = default_route
        self.actions = {}
        self.paths = defaultdict(dict)
        self.api = api

    @property
    def debug(self):
        return self._debug

    def path(self, route, **kwargs):
        def _register_path(route_func):
            def _decorator(*args, **kwargs):
                return route_func(*args, **kwargs)
            self._add_path(route, route_func, **kwargs)
            return wraps(route_func)(_decorator)
        return _register_path

    def _add_path(self, path, route_func, **kwargs):
        name = kwargs.pop('name', route_func.__name__)
        methods = kwargs.pop('methods', ['GET'])
        if kwargs:
            raise TypeError('TypeError: route() got unexpected keyword '
                            'arguments: %s' % ', '.join(list(kwargs)))
        for method in methods:
            if method in self.paths[path]:
                raise ValueError(
                    "Duplicate method: '%s' detected for route: '%s'\n"
                    "between view functions: \"%s\" and \"%s\". A specific "
                    "method may only be specified once for "
                    "a particular path." % (
                        method, path, self.paths[path][method].view_name,
                        name)
                )
            self.paths[path][method] = route_func

    def action(self, route, **kwargs):
        def _register_action(route_func):
            def _decorator(*args, **kwargs):
                # import pdb; pdb.set_trace()
                return route_func(*args, **kwargs)

            self._add_action(route, route_func, **kwargs)
            return wraps(route_func)(_decorator)
        return _register_action

    def _add_action(self, action, route_func, **kwargs):
        name = kwargs.pop('name', route_func.__name__)
        if kwargs:
            raise TypeError('TypeError: route() got unexpected keyword '
                            'arguments: %s' % ', '.join(list(kwargs)))
        if action in self.actions:
            raise ValueError("Duplicate action: '%s' detected. Name: %s" % (action, name))
        self.actions[action] = route_func

    def _error_response(self, message, error_code, http_status_code):
        body = {'Code': error_code, 'Message': message}
        response = self.api.new_response(body=body, status_code=http_status_code)
        return response

    def __call__(self, event, context):
        # This is what's invoked via lambda.
        # Sometimes the event can be something that's not
        # what we specified in our request_template mapping.
        # When that happens, we want to give a better error message here.
        try:
            api = self.api(event, context)
            request = api.request()
        except KeyError as e:
            self.log.warning("Missing parameter in Request: {}".format(e))
            return self._error_response(error_code='InternalServerError',
                                        message='Invalid api request.',
                                        http_status_code=500)

        route = request.route
        route_func = None
        if api.api == 'ws' and route in self.actions:
            route_func = self.actions[route]
        elif api.api == 'rest' and route in self.paths:
            rest_method = api.method
            if rest_method not in self.paths[route]:
                return self._error_response(
                    error_code='MethodNotAllowedError',
                    message='Unsupported method: %s' % rest_method,
                    http_status_code=405)
            route_func = self.paths[route][rest_method]
        elif self.default_route:
            route_func = self.default_route
        else:
            return self._error_response(
                error_code='MethodNotFound',
                message="No view function for: %s" % route,
                http_status_code=404)

        self.log.info('Call Function: {}'.format(route_func.__name__))

        response = self._get_route_function_response(route_func, request, context)

        if self.debug:
            self.log.info('Response: {}'.format(response.data))

        return api.response(response)

    def _get_route_function_response(self, route_function, request, context):
        try:
            response = route_function(request, context)
            if not isinstance(response, self.api.new_response):
                response = self.api.new_response(data=response)
        except MellisugaViewError as e:
            # Any mellisuga view error should propagate.  These
            # get mapped to various HTTP status codes in API Gateway.
            response = self.api.new_response(
                data={
                    'Code': e.__class__.__name__,
                    'Message': str(e)
                },
                status_code=e.STATUS_CODE
            )
        except Exception as e:
            headers = {}
            if self.debug:
                print(traceback.format_exc())
                # If the user has turned on debug mode,
                # we'll let the original exception propogate so
                # they get more information about what went wrong.
                self.log.debug("Caught exception for %s with error: %s", route_function, e,
                               exc_info=True)
                stack_trace = ''.join(traceback.format_exc())
                data = stack_trace
                headers['Content-Type'] = 'text/plain'
            else:
                data = {'Code': 'InternalServerError',
                        'Message': 'An internal server error occurred.'}
            response = self.api.new_response(data=data, headers=headers, status_code=500)
        return response
