import json
import urllib.request as urllib2
from distutils.version import StrictVersion


def get_versions(package_name):
    url = "https://pypi.org/pypi/%s/json" % (package_name,)
    data = json.load(urllib2.urlopen(urllib2.Request(url)))
    versions = data["releases"].keys()
    versions = sorted(versions, key=StrictVersion)
    return versions


def get_current_version():
    return get_versions("pynevin")[-1]


def get_latest_version():
    current = get_current_version().split(".")
    current[-1] = str(int(current[-1]) + 1)
    return ".".join(current)


print(get_latest_version())
