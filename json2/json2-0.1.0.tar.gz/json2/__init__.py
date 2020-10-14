from json import *

def read_file(filename):
    with open(filename, "r") as f:
        return json.loads(f.read())


def write_file(filename, content):
    with open(filename, "w") as f:
        f.write(json.dumps(content))