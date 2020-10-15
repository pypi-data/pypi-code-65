#           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#                   Version 2, December 2004
#
# Copyright (C) 2020 Ryosuke Abe <chike@sfc.wide.ad.jp>
# 
# Everyone is permitted to copy and distribute verbatim or modified
# copies of this license document, and changing it is allowed as long
# as the name is changed.
#
#           DO WHAT THE FUCK YOU WANT TO PUBLIC LICENSE
#  TERMS AND CONDITIONS FOR COPYING, DISTRIBUTION AND MODIFICATION
#
# 0. You just DO WHAT THE FUCK YOU WANT TO.
import os

from hashstorage.utils import *

class HashStorage():
    def __init__(self, datadir=None):
        self.datadir = ".hashstorage" if datadir is None else  datadir
        self.storage = {}
        self._loadDataDir()

    def _loadDataDir(self):
        if not os.path.exists(self.datadir):
            os.makedirs(self.datadir)
        #TODO: loadDataDir
    
    def store(self, value):
        key = sha256(value)
        self.storage[key] = value
        saveJson(self.storage, self.datadir+"/storage.json")
        return key
    
    def get(self, key):
        if key not in self.storage:
            return None
        else:
            return self.storage[key]

    def shutdown(self):
        saveJson(self.storage, self.datadir+"/storage.json")
        
