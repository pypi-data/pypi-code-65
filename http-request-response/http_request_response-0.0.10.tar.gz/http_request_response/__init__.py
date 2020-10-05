from flask import request, has_request_context
from flask import current_app as app
from flask_jwt_extended import get_jwt_identity
from functools import wraps
from http_status_code.standard import bad_request


class RequestResponse:

    def __init__(self, status_code=None, data=None, message=None):
        self.status_code = status_code
        self.data = data
        self.message = self.__message_to_str(message)

    def update(self, status_code=200, data=None, message=None):
        self.status_code = status_code
        self.data = data
        self.message = self.__message_to_str(message)

    def __message_to_str(self, message):
        return message if message is None else str(message)

    def __call__(self, *args, **kwargs):
        return self.__dict__


class RequestUtilities:
    @staticmethod
    def get_request_context():
        context = dict()
        if has_request_context():
            context['url'] = request.url
            context['remote_addr'] = request.remote_addr
            context['method'] = request.method

            context['headers'] = request.headers
            context['url_args'] = request.args
            context['body'] = request.json

            try:
                request.body_args.pop('file_bytes')
            except:
                print('body_args has not been initiated yet due to some missing args. ')

            context['file_body_args'] = request.body_args

            try:
                # Claims are not available in case of login endpoint and when the token is not provided
                claims = get_jwt_identity()
                if 'email' in claims:
                    context['email'] = claims['email']
            except:
                if request.json and 'email' in request.json:
                    context['email'] = request.json['email']
                else:
                    context['email'] = 'Anonymous'

        return context

    @staticmethod
    def try_except(fn):
        """A decorator for all of the actions to do try except"""

        @wraps(fn)
        def wrapper(*args, **kwargs):
            try:
                # Action
                status, data = fn(*args, **kwargs)

                try:
                    # Logging
                    app.app_info_logger.info(RequestUtilities.get_request_context())
                except:
                    # Logging
                    app.logger.info(RequestUtilities.get_request_context())


            except Exception as e:
                status, data = bad_request, None
                status.update_msg(e)

                try:
                    # Logging
                    app.app_exc_logger.exception(RequestUtilities.get_request_context())
                except:

                    # Logging
                    app.logger.exception(RequestUtilities.get_request_context())

            rs = RequestResponse(status_code=status.code, message=status.message, data=data)
            return rs()

        return wrapper
