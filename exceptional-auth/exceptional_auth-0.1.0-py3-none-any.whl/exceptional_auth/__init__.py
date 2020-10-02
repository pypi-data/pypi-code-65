class AuthException(Exception):
    '''
        Base class for all of our exceptions. 

        Has no particular meaning, other than "the current user cannot currently access this resource".
    '''
    pass

class LoginRequired(AuthException):
    '''
        The user is not logged in, and must log in to access this resource.

        App developers are not expected to instantiate this directly. Call require_login() instead.

        Site developers should catch this and provide the user with the opportunity to log in.
    '''
    pass

class PermissionDenied(AuthException):
    '''
        Indicates that the user is logged in, but lacks some necessary permission.

        App developers should call require_permission() when checking for standard django permissions, but they may also raise this directly when performing other custom permission checks.
    '''
    def __init__(self, message=None):
        self.message = message

class NotCurrentlyAllowed(AuthException):
    '''
        Indicates that the user has all necessary permissions, but that the request cannot be handled because of some other time-based/logic constraints.

        Site developers should catch this and display a generic error message to the user.
    '''
    def __init__(self, reason):
        self.reason = reason


def require_login(request):
    if request.user.is_anonymous :
        raise LoginRequired()

def require_permissions(request, *permission_names):
    require_login(request)
    user = request.user
    for permission_name in permission_names :
        # TODO - if DEBUG, should we validate that permission_name is actually a valid permission name?
        if not user.has_perm(permission_name) :
            raise PermissionDenied()


class BaseMiddleware:
    '''
        A Middleware base class which site developers can extend, to make handling our exceptions easier.
    '''

    # Boilerplate, required by all middleware
    def __init__(self, get_response):
        self.get_response = get_response
    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        if isinstance(exception, LoginRequired) :
            return self.login_required(request, exception)
        if isinstance(exception, PermissionDenied) :
            return self.permission_denied(request, exception)
        if isinstance(exception, NotCurrentlyAllowed) :
            return self.not_currently_allowed(request, exception)

    # Site developers should override these methods
    # Note that exceptions don't really provide any useful information, but we might attach useful attributes to them later (ie. 'missing_permission'), and we want all subclasses to be prepared to receive them
    def login_required(self, request, exception):
        raise NotImplementedError()
    def permission_denied(self, request, exception):
        raise NotImplementedError()
    def not_currently_allowed(self, request, exception):
        raise NotImplementedError()
