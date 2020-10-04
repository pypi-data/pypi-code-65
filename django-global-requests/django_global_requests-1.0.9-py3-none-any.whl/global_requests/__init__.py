# from django.utils.thread_support import currentThread
from threading import currentThread

from django.utils.deprecation import MiddlewareMixin

_requests = {}

def get_request():
    return _requests[currentThread()]

def get_thread_user():
    try:
        return get_request().user
    except:
        return None

def set_request(request):
    _requests[currentThread()] = request

def delete_request():
    del _requests[currentThread()]

class GlobalRequestMiddleware(object):
    def process_request(self, request):
        _requests[currentThread()] = request

class GlobalRequestMiddleware(MiddlewareMixin):
    # One-time configuration and initialization.

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        set_request(request)
        response = self.get_response(request)
        delete_request()
        return response