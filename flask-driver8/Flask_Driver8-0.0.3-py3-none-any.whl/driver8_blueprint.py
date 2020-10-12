from flask import Blueprint, request
from flask import abort, jsonify, make_response
from uuid import uuid1
import re

driver8_blueprint = Blueprint('driver8_blueprint', __name__)

sessions = {}


def success(value, session_id):
    """Return successful response in the scope of particular Driver8 session"""
    return {'status': 0, 'value': value, 'sessionId': session_id}


def error(message, session_id):
    """Return error response in the scope of particular Driver8 session. Status 13 is interpreted as unknown error"""
    return {'status': 13, 'message': message, 'sessionId': session_id}


@driver8_blueprint.before_app_request
def check_session():
    match = re.match("/session/(.+?)/", request.path)
    if match and match.group(1) is not None:
        if match.group(1) not in sessions:
            abort(make_response(jsonify(message='Session not found'), 404))


@driver8_blueprint.route('/')
def index():
    return 'You are using Driver 8 (python) 0.0.3'


@driver8_blueprint.route('/status')
def status():
    return {'message': 'Driver8 (python) app version 0.0.3', 'ready': True}


@driver8_blueprint.route('/session', methods=['POST'])
def post():
    session_id = str(uuid1())
    sessions[session_id] = {}
    return success({}, session_id)


@driver8_blueprint.route('/session/<session_id>', methods=['GET'])
def get_session(session_id):
    if session_id in sessions:
        return success({}, session_id)
    else:
        abort(make_response(jsonify(message='Session not found'), 404))


@driver8_blueprint.route('/session/<session_id>', methods=['DELETE'])
def delete_session(session_id):
    if session_id in sessions:
        del sessions[session_id]
        return '', 204
    else:
        abort(make_response(jsonify(message='Session not found'), 404))
