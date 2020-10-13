import random


from .util import Value, Values


class Dummy:
    def _generate(generator, count, exhaustive, **kwargs):
        res = generator(**kwargs)
        if isinstance(res, Value):
            return [generator(**kwargs).value for _ in range(count)]
        elif isinstance(res, Values):
            if isinstance(res.values, (list, tuple)):
                if exhaustive or count >= len(res.values):
                    return [x for x in res.values]
                else:
                    return list(random.sample(res.values, count))
            else:
                return [res.values(**kwargs) for _ in range(count)]
        else:
            raise TypeError("Result of generator has invalid type: {}".format(type(res)))
    
    def valids(self, count=1, exhaustive=False, **kwargs):
        return Dummy._generate(self._valids, count, exhaustive, **kwargs)
    
    def invalids(self, count=1, exhaustive=False, **kwargs):
        return Dummy._generate(self._invalids, count, exhaustive, **kwargs)

    def _valids(self, **kwargs):
        raise NotImplementedError("_valids() it not implemented for {}.".format(type(self)))

    def _invalids(self, **kwargs):
        raise NotImplementedError("_invalids() it not implemented for {}.".format(type(self)))

    def valid(self, value, raise_error=False):
        raise NotImplementedError("valid() is not implemented for {}.".format(type(self)))

    def examples(self):
        return {
            "valid": self.valids(),
            "invalid": self.invalids(),
        }
    
    def equals(self, v1, v2):
        if v1 is None and v2 is None:
            return True
        if v1 is None or v2 is None:
            return False
        return self._equals(v1, v2)

    def _equals(self, v1, v2):
        return v1 == v2
