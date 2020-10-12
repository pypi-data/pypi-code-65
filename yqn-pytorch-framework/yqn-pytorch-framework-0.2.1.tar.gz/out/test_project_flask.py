from flask import Flask, request
import time
import logging
import os
from flask_compress import Compress
from flask_cors import CORS
from flask_json import as_json, JsonError, FlaskJSON
from termcolor import colored
import base64
from yqn_common.helper import set_logger
from __init__ import __version_int__

from project_config_flask import LocalInferConfig
from project_config import LocalConfig

app = Flask(__name__)
logger = set_logger(colored('test_project', 'white'),
                    verbose=project_infer_config.VERBOSE)
app.logger.handlers = []
app.logger.setLevel(logging.INFO)

CORS(app, origins="*")
FlaskJSON(app)
Compress().init_app(app)

@app.route('/actuator/info', methods=['GET'])
@app.route('/info', methods=['GET'])
@as_json
def get_server_status():
    nvidia_str = os.popen('nvidia-smi').read()
    return {'status': "OK", "GPU": nvidia_str}


@app.route('/scope_url', methods=['POST'])
@as_json
def test_project_url():
    data = request.json
    failed = True
    try:
        key_values = dict()
        key_values['engine_version'] = __version_int__

        failed = False
        if key_values:
            return key_values
        else:
            return {'engine_version': __version_int__}

    except Exception as e:
        logger.error('error when handling HTTP request', exc_info=True)
        logger.error('HTTP request data ' + str(data), exc_info=True)
        raise JsonError(description=str(e), type=str(type(e).__name__))
    finally:
        if failed:
            return {'engine_version': __version_int__}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
