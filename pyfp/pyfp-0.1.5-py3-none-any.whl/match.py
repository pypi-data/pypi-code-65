class Match:
    def __init__(self, val):
        self._val = val
        self._branches = []

    def branch(self, val, func):
        self._branches.append((val, func))

        return self
    
    def default(self, func):
        self._default = func

        return self

    def get(self):
        for v, f in self._branches:
            if callable(v):
                if v(self._val):
                    return f()
            elif v == self._val:
                return f()
        
        return self._default()