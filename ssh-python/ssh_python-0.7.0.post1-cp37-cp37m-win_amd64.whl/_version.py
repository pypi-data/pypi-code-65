
import json

version_json = '''
{"date": "2020-10-03T15:37:55.956604", "dirty": false, "error": null, "full-revisionid": "eaa65872b8c98b30b5cb72620259ccc6043d1505", "version": "0.7.0.post1"}'''  # END VERSION_JSON


def get_versions():
    return json.loads(version_json)

