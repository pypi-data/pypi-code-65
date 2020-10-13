from enum import Enum
from typing import Union


class Granularity(Enum):
    """
    Enum class to describe allowed types of granularities
    """
    # TODO: This exists to support validation prior to posting from the API.
    #       For ease of maintenance, this should be handled through API returns.
    HOUR = 'hour'
    DAY = 'day'
    WEEK = 'week'
    MONTH = 'month'
    YEAR = 'year'
    QUARTER = 'quarter'
    FIPS = 'FIPS'
    MOVIE = 'movie'
    CBG = 'CBG'
    TICKER = 'ticker'


class ModelTypes(Enum):
    """
    Enum class to describe allowed types of models
    """
    # TODO: This exists to support validation prior to posting from the API.
    #       For ease of maintenance, this should be handled through API returns.
    TIMESERIES = 'time series'


class ModelType(object):
    """
    Class to wrap the ModelTypes enum for additional functionality

    (Extending the enum class is not allowed, and subclassing is possible, but unnecessary)
    """

    def __init__(self, name: str):
        self._type = ModelTypes(name)
        # TODO: Lookup compatible when other model types and/or granularities are supported.
        self._compatible_granularities = [Granularity.DAY, Granularity.MONTH, Granularity.YEAR, Granularity.WEEK, Granularity.QUARTER]

    @property
    def name(self):
        return self._type.name

    @property
    def value(self):
        return self._type.value

    @property
    def compatible_granularities(self):
        return self._compatible_granularities

    def is_compatible(self, granularity: Union[str, Granularity]) -> bool:
        # If not enum, convert to enum first.
        try:
            granularity.name
        except AttributeError:
            granularity = Granularity(granularity)
        return granularity in self._compatible_granularities