from flask import jsonify

def exception_handler(e):
    return jsonify(code=e.code, detail=e.detail), e.status_code


class APIException(Exception):
    status_code = 400
    code = None
    detail = None


class PermissionDenied(APIException):
    status_code = 403
    code = 'permission_denied'
    detail = 'permission denied'
