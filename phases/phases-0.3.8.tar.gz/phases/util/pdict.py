class pdict(dict):
    def __getitem__(self, k):
        if not isinstance(k, list):
            return super().__getitem__(k)
        value = self
        for field in k:
            value = value.__getitem__(field)
        return value

    def __setitem__(self, k, v):
        if not isinstance(k, list):
            return super().__setitem__(k, v)
        value = self
        overwriteField = k.pop()
        for field in k:
            value = value.__getitem__(field)
        value[overwriteField] = v
