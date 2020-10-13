import hashlib


def sha(filename: str) -> str:
    _sha = hashlib.sha1()
    with open(filename, 'r') as f:
        _sha.update(f.read().encode('utf-8'))
    return _sha.hexdigest()


