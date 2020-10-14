from functools import wraps

import jwt
from flask import request
from flask_jwt_extended import verify_jwt_in_request, \
    verify_jwt_refresh_token_in_request, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError, WrongTokenError
from http_status_code.standard import invalid_token, missing_token, expired_token, \
    unauthorized_request, wrong_token


class APIAuth:
    # A decorator for authentication and authorization purpose
    @classmethod
    def auth_required(cls, req_token='access', authentication_required=True, authorization_object=None):
        def decorator(fn):
            @wraps(fn)
            def wrapper(*args, **kwargs):
                try:
                    if not authentication_required:
                        return fn(*args, **kwargs)

                    if req_token == 'access':
                        verify_jwt_in_request()

                    elif req_token == 'refresh':
                        verify_jwt_refresh_token_in_request()

                    request.claims = get_jwt_identity()

                    if authorization_object is not None and not authorization_object.is_authorized():
                        return unauthorized_request, None

                    return fn(*args, **kwargs)

                except jwt.DecodeError:
                    # Token is not a valid JWT token
                    return invalid_token, None

                except NoAuthorizationError:
                    # The token is not provided
                    return missing_token, None

                except jwt.ExpiredSignatureError:
                    # The token is expired
                    return expired_token, None

                except WrongTokenError as e:
                    # To discriminate between refresh and access tokens
                    wrong_token.update_msg(str(e))
                    return wrong_token, None

            return wrapper

        return decorator