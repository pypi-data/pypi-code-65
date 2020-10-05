# !/usr/bin/env python
# coding: utf-8
import codecs
import json
import os
import subprocess
import time

from tronpytool import Tron

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

    def GetCodeTag(self, fullname):
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


class CoreDeploy:
    """DEFI Contract deployment
    with the right strategies
    """
    _contract_dict: dict
    ACTION_FOLDER = "deploy_results"

    def __init__(self, tron: Tron):
        self.tron = tron
        self._contract_dict = dict()

    def getAddr(self, keyname: str) -> str:
        return self._contract_dict.get(keyname)

    def preview_all_addresses(self):
        print(self._contract_dict)

    def sol_dat_deploy(self, sol_wrap: SolcWrap, path: str, classname: str, params: list = []) -> str:
        _abi, _bytecode = sol_wrap.GetCode(path, classname)
        contractwork = self.tron.trx.contract(abi=_abi, bytecode=_bytecode)
        contract = contractwork.constructor()
        tx_data = contract.transact(
            fee_limit=10 ** 9,
            call_value=0,
            parameters=params,
            consume_user_resource_percent=1)
        print("======== TX Result ✅")
        sign = self.tron.trx.sign(tx_data)
        print("======== Signing LendingPoolAddressesProvider ✅")
        result = self.tron.trx.broadcast(sign)
        path = "{}/{}.json".format(self.ACTION_FOLDER, classname)
        print("======== Broadcast Result ✅ -> {}".format(path))
        sol_wrap.StoreTxResult(result, path)
        contract_address = self.tron.address.from_hex(result["transaction"]["contract_address"])
        self._contract_dict[classname] = contract_address
        print("======== address saved to ✅ {} -> {}".format(contract_address, classname))
        return contract_address
