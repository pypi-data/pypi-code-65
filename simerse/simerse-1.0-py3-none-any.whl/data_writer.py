
class writer:
    def __init__(self, fn):
        self.fn = fn

    def __set_name__(self, owner, name):
        if not hasattr(owner, 'writers'):
            owner.writers = {}
            owner.dimensions = []
        owner.writers[name] = self.fn
        owner.dimensions.append(name)
        setattr(owner, name, self.fn)


class cache:
    def __init__(self, getter):
        self.getter = getter

    def __get__(self, obj, typ=None):
        if not hasattr(typ, 'cache'):
            typ.cache = {}
        if self.getter.__name__ not in typ.cache:
            typ.cache[self.getter.__name__] = self.getter()
        return typ.cache[self.getter.__name__]

    def __set__(self, obj, val):
        raise AttributeError(f'Cached value {self.getter.__name__} is read-only.')

    def __delete__(self, obj):
        type(obj).cache.pop(self.getter.__name__)


class DataWriter:
    def __init__(self, data_loader):
        self.data_loader = data_loader

    @property
    def data(self):
        return self.data_loader

    def write(self, points, dimensions='all'):
        if dimensions == 'all':
            dimensions = self.data_loader.dimensions

        if isinstance(dimensions, (str, int)):
            dimensions = (dimensions,)

        if isinstance(points, int):
            points = (points,)

        dimensions = self.data_loader.get_dimension_list(dimensions)

        for dimension in dimensions:
            # noinspection PyUnresolvedReferences
            self.writers[dimension](self, points)
