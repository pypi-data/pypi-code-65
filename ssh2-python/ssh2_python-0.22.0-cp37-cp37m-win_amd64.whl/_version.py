
import json

version_json = '''
{"date": "2020-10-03T14:59:55.662505", "dirty": false, "error": null, "full-revisionid": "a0196a8666cda4b2a65042c0cd617f0c6e8f7004", "version": "0.22.0"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

