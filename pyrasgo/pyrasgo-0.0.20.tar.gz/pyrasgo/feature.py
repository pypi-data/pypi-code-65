from collections import Sequence

from pyrasgo.enums import Granularity
from pyrasgo.namespace import Namespace
from pyrasgo.connection import Connection


class FeatureList(Sequence):
    """
        Convenience class to enable simpler console presentation,
        iteration and searching through lists of Features objects
    """

    def __init__(self, api_object, api_key=None):
        # TODO: Would this be more useful as a set not a sequence?
        self._api_key = api_key
        self.data = sorted([Feature(api_key=api_key, api_object=entry) for entry in api_object], key=lambda x: x.id)

    def __getitem__(self, i: int):
        return self.data[i]

    def __len__(self) -> int:
        return len(self.data)

    def __str__(self):
        ids = [str(feature.id) for feature in self]
        return (f"Features({len(self.data)} total, "
                f"ids: [{','.join(ids if len(self) < 7 else ids[0:3] + ['...'] + ids[-3:])}])")

    def __add__(self, other):
        # TODO: Should this be a set operations??
        if isinstance(other, Feature):
            return type(self)([feature.to_dict() for feature in self.data + [other]], api_key=self._api_key)
        if isinstance(other, type(self)):
            return type(self)([feature.to_dict() for feature in self.data + other.data], api_key=self._api_key)
        if isinstance(other, list) and all([isinstance(entry, Namespace) or isinstance(entry, Feature) for entry in other]):
            return type(self)([feature.to_dict() for feature in self.data + other], api_key=self._api_key)
        raise TypeError(f"unsupported operand type(s) for +: '{type(self)}' and '{type(other)}'")

    def __repr__(self):
        return str(self)

    def filter(self, **kwargs):
        return [feature for feature in self.data
                if [feature.__getattr__(key) for key in kwargs.keys()] == list(kwargs.values())]


class Feature(Connection):
    """
    Stores the properties for a feature
    """

    def __init__(self, api_object, **kwargs):
        # TODO: Determine pathway to create feature via command line? Do we want to allow this?
        super().__init__(**kwargs)
        self._namespace = Namespace(**api_object)
        try:
            self.dimensionality
            self.datasource
            self.granularity
        except AttributeError:
            self.get()

    def __getattr__(self, item):
        try:
            return self._namespace.__getattribute__(item)
        except KeyError:
            raise AttributeError(f"No attribute named {item}")

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Feature(id={self.id}, name={self.name}, description={self.description})"

    def get(self):
        """
        Updates the Feature object's attributes from the API
        """
        self._namespace = Namespace(**self._get(f"/features/{self.id}").json())

    @property
    def datasource(self):
        """
        Retrieves datasource name from nested structure
        """
        # TODO: This is tightly coupled to the API's response object
        return self._namespace.column.featureSet.dataSource.name

    @property
    def dimensionality(self):
        """
        Retrieves dimensionality from nested structure
        """
        # TODO: This is tightly coupled to the API's response object
        return self._namespace.column.dimensionality

    @property
    def granularity(self):
        """
        Retrieves dimensionality from nested structure
        """
        # TODO: This is tightly coupled to the API's response object
        return Granularity(self._namespace.column.dimensionality.granularity)
