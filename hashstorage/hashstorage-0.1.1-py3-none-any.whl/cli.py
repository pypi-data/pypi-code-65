from hashstorage.hashstorage import *
import sys
import argparse

from flask import Flask, request, jsonify, make_response
app = Flask(__name__)
hs = None

class HashStorageCli():
    def __init__(self, args):
        self.parser = self.parseArgs(args)

    def parseArgs(self, args):
        parser = argparse.ArgumentParser(description='Simple Hash Storage v0.0.1 (C) Ryosuke Abe 2020')
        parser.add_argument('-dir', '--datadir', help='Path to datadir') 
        return parser.parse_args(args)

@app.route("/", methods=["GET"])
def versionMessage():
    return 'Simple Hash Storage v0.0.1 (C) Ryosuke Abe 2020'

@app.route("/store", methods=['POST'])
def GetStoreReq():
    params = request.json
    if "value" not in params.keys():
        resbody = {"result": False, "error": "Request Json is Invalid"} 
    else:
        data = params["value"]
        key = hs.store(data)

        resbody = {"result": True, "key": key}
    return make_response(jsonify(resbody))
    
@app.route("/get", methods=['POST'])
def GetGetReq():
    params = request.json
    data = hs.get(params["key"])
    if data:
        resbody = {"result": True, "value": data}
    else:
        resbody = {"result": False, "error": "Key (%s) is not found"%params["key"] }
    return make_response(jsonify(resbody))

def main():
    runHashStorageCli(sys.argv[1:])

def runHashStorageCli(args):
    cli = HashStorageCli(args)
    global hs 
    hs = HashStorage(cli.parser.datadir)
    try:
        app.run(host="localhost", port=6666)
    finally:
        hs.shutdown()
