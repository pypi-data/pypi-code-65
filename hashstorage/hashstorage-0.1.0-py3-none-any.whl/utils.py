import hashlib
import binascii
import json

def sha256(keyword): 
    bytekey = binascii.hexlify(keyword.encode("utf-8"))
    hashvalue = hashlib.sha256(bytekey).digest()
    return hashvalue.hex()

def loadJson(jsonpath):
    try:
        with open(jsonpath) as f:
            df = json.load(f)
    except FileNotFoundError:
        return False
    return df

def saveJson(dictdata, storepath):
    f = open(storepath, "w")
    json.dump(dictdata, f,
            ensure_ascii=False,
            indent=4,
            sort_keys=True,
            separators=(',', ': '))
