import json
import os


def create_summary(endpoint, basepath="results"):
    endpoint_name = endpoint.func.__name__
    as_json = {
        "name": endpoint_name,
        "kind": endpoint.kind,
        "inputs": list(endpoint.X.columns),
        "output": endpoint.y.name,
    }
    with open(os.path.join(basepath, endpoint_name, "summary.json"), "w") as summary:
        json.dump(as_json, summary)
