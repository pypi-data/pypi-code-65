import logging
import traceback
from flask import Flask, jsonify, request
import copy


class BaseJob:
    def __init__(self, uuid_str):
        self.uuid_str = uuid_str

    def run(self):
        raise Exception("Not implemented in base class ")


def setup_app():
    app = Flask(__name__)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
    )

    @app.route("/ping", methods=['GET'])
    def ping():
        status = {"status": "ok"}
        app.logger.info("ping " + str(status))
        return jsonify(status)

    return app


def declare_method(app, method_name, job_builder, **kwargs):
    @app.route("/", methods=['POST'])
    def handle():
        req_json = request.json
        uuid_str = req_json['uuid_str']
        try:
            req_json_to_log = copy.copy(req_json)
            if 'data' in req_json_to_log:
                req_json_to_log['len_data'] = len(req_json_to_log['data'])
                del req_json_to_log['data']
            app.logger.info(method_name, {'req_json': req_json_to_log, 'uuid_str': uuid_str})
            my_job = job_builder(uuid_str, req_json, **kwargs)
            res = my_job.run()
            return jsonify(res)
        except Exception:
            app.logger.error(method_name + str({'traceback': traceback.format_exc(), 'uuid_str': uuid_str}))
            return jsonify({'message': 'Error', 'uuid_str': uuid_str}), 500
