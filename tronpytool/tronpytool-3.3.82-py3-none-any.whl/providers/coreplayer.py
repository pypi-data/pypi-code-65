#!/usr/bin/env python
# coding: utf-8


import codecs
import json
import os

import time

from tronpytool.compile.basetest import WrapContract


class CoreSimulatePlayers:
    """DEFI Contract deployment
       the player with game
        """
    statement = 'End : {}, IO File {}'
    _contract_dict: dict
    _network: str
    FILE_CONTRACT = "backedup"
    ACTION_FOLDER = "deploy_results"
    COLLECTION_CONTRACTS = "players"

    def __init__(self, network: str, workspace: str):
        self._contract_dict = dict()
        self._tron_clients = dict()
        self._workspace = workspace
        self._network = network
        """try to load up the file from the existing path"""
        try:
            self._contract_dict = json.load(codecs.open(self.playerAddrsFilePath(), 'r', 'utf-8-sig'))
            for address_wallet, v in self._contract_dict:
                tron = WrapContract(self._network).setMasterKey(address_wallet, v["privkey"]).getClientTron()
                self._tron_clients[address_wallet] = tron

            print("==== 🛄 data is prepared and the player metadata is now ready... ")
            self.preview_all_addresses()
            print("==== 🛄 End ==== ")
        except ValueError:
            pass
        except TypeError as e:
            print(e)

    def _writeFile(self, content, filename: str):
        fo = open(filename, "w")
        fo.write(content)
        fo.close()
        print(self.statement.format(time.ctime(), filename))

    def _storeTxDict(self, tx_result_data: any, filepath: str):
        self._writeFile(json.dumps(tx_result_data, ensure_ascii=False), filepath)

    @property
    def backupname(self) -> str:
        """preview the file name"""
        return self.FILE_CONTRACT

    @backupname.setter
    def backupname(self, filename: str) -> None:
        """the file name does not require extension name"""
        self.FILE_CONTRACT = filename

    @property
    def playermeta_data(self) -> str:
        return self.COLLECTION_CONTRACTS

    @playermeta_data.setter
    def playermeta_data(self, path: str) -> None:
        self.COLLECTION_CONTRACTS = path

    def getAddr(self, keyname: str) -> str:
        """example: TT67rPNwgmpeimvHUMVzFfKsjL9GZ1wGw8"""
        return self._contract_dict.get(keyname)

    def getAllAddress(self) -> dict:
        return self._contract_dict

    def preview_all_addresses(self) -> None:
        print(self._contract_dict)

    def playerAddrsFilePath(self) -> str:
        return os.path.join(self._workspace, self.ACTION_FOLDER,
                            "{}.json".format(self.COLLECTION_CONTRACTS))

    def GetMetadataByAddr(self, address: str) -> dict:
        return self._contract_dict[address]

    def SaveMetaFile(self) -> "CoreSimulatePlayers":
        self._storeTxDict(self._contract_dict, self.playerAddrsFilePath())
        return self

    def SyncBalances(self) -> "CoreSimulatePlayers":
        if len(self._contract_dict) > 0:
            for k, v in self._contract_dict:
                tron = WrapContract(self._network).setMasterKey(k, v["privkey"]).getClientTron()
                amount = tron.trx.get_balance(k, False)
                self._contract_dict[k]["balance"] = amount
        return self

    def AppendInitPlayer(self, address_wallet: str, private_key: str) -> "CoreSimulatePlayers":
        tron = WrapContract(self._network).setMasterKey(address_wallet, private_key).getClientTron()
        amount = tron.trx.get_balance(address_wallet, False)
        self._tron_clients[address_wallet] = tron
        self._contract_dict[address_wallet] = dict(
            balance=amount,
            upline="",
            invitecode="",
            privkey=private_key,
        )
        return self

    def SetUpLine(self, address: str, line: str) -> "CoreSimulatePlayers":
        if len(self._contract_dict) > 0:
            if "upline" in self._contract_dict[address]:
                self._contract_dict[address]["upline"] = line
        return self

    def SetDownLine(self, address: str, invite: str) -> "CoreSimulatePlayers":
        if len(self._contract_dict) > 0:
            if "invitecode" in self._contract_dict[address]:
                self._contract_dict[address]["invitecode"] = invite
        return self
