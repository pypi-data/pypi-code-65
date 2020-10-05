from flask import Flask, jsonify, request, abort

from greble_flow.managment.manager import FlowManager

app = Flask(__name__)
flow_manager = FlowManager()


@app.route("/flow-processor/<flow_name>/", methods=['POST'])
def run_flow(flow_name):
    # flow_manager
    if not request.json:
        abort(400)

    return jsonify({
        "result": flow_manager.run(flow_name, request.json)
    })
