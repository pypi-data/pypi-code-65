
import json

version_json = '''
{"date": "2020-10-03T14:14:30.886497", "dirty": false, "error": null, "full-revisionid": "75f847524f936f01ecc1f27e2b2d7dcc44b02a05", "version": "0.21.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

