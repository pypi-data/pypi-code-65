# !/usr/bin/env python
# coding: utf-8
import codecs
import json
import os
import subprocess
import time

ROOT = os.path.join(os.path.dirname(__file__))


class SolcWrap(object):
    """docstring for SolcWrap"""
    outputfolder = "build"
    solfolder = ""
    file_name = "xxx.sol"
    prefixname = ""
    statement = 'End : {}, IO File {}'
    workspace = ""

    def __init__(self, workspace):
        self.workspace = workspace
        super(SolcWrap, self).__init__()

    def SetOutput(self, path):
        self.outputfolder = path
        return self

    def SetSolPath(self, path):
        self.solfolder = path
        return self

    def BuildRemote(self):
        """using remote compile method to compile the sol files
        all works will be done with the remote server or using the docker"""
        list_files = subprocess.run(["{}/solc_remote".format(self.workspace)])
        print("The exit code was: %d" % list_files.returncode)
        return self

    def WrapModel(self):
        # path="{}/combinded.json".format(self.outputfolder)
        pathc = os.path.join(os.path.dirname(__file__), self.outputfolder, "combined.json")
        try:
            pathcli = codecs.open(pathc, 'r', 'utf-8-sig')
            self.combined_data = json.load(pathcli)
        except Exception as e:
            print("Problems from loading items from the file: ", e)
        return self

    def byClassName(self, path, classname):
        return "{prefix}:{name}".format(prefix=path, name=classname)

    def GetCode(self, fullname):
        return self.combined_data["contracts"][fullname]["abi"], self.combined_data["contracts"][fullname]["bin"]

    def GetCode(self, path, classname) -> [str, str]:
        return self.combined_data["contracts"][self.byClassName(path, classname)]["abi"], \
               self.combined_data["contracts"][self.byClassName(path, classname)]["bin"]

    def writeFile(self, content, filename):
        fo = open(filename, "w")
        fo.write(content)
        fo.close()
        print(self.statement.format(time.ctime(), filename))

    def StoreTxResult(self, tx_result_data, filepath):
        self.writeFile(json.dumps(tx_result_data, ensure_ascii=False), filepath)
