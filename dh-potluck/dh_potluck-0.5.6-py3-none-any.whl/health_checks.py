from http import HTTPStatus

from flask import abort, Blueprint

healthz = Blueprint('healthz', __name__)


class HealthChecks:
    callback = None

    def __init__(self, callback=lambda: True):
        HealthChecks.callback = callback

    def init_app(self, app):
        app.register_blueprint(healthz, url_prefix='/healthz')


@healthz.route('/liveness')
def liveness():
    return 'OK'


@healthz.route('/readiness')
def readiness():
    try:
        if not HealthChecks.callback():
            abort(HTTPStatus.SERVICE_UNAVAILABLE, 'Pod unready to service requests.')
    except Exception as e:
        abort(HTTPStatus.SERVICE_UNAVAILABLE, str(e))
    return 'OK'
