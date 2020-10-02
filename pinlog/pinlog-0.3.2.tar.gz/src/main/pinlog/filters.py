class Filters():
    def __init__(self, config):
        self._config = config
        # self._keynames = []
        self._primary_keyname = None
        self._sub_keyname = None
        self._keys = []

    # def set_keynames(self, keys):
    #     self._keynames = keys

    def set_primary_keyname(self, key):
        self._primary_keyname = key

    def set_sub_keyname(self, key):
        self._sub_keyname = key

    def add_filter(self, key):
        self._keys.append(key)

    def add_filters(self, keys):
        self._keys.extend(keys)

    def primary_keyname(self):
        return self._primary_keyname

    def sub_keyname(self):
        return self._sub_keyname

    def keys(self):
        return self._keys