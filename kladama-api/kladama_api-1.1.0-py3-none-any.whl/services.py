import abc
from abc import ABC

from .queries import EndpointQuery
from .queries import SingleResultQuery


class ServiceRequestBase(EndpointQuery, ABC):

    @property
    def url_path(self) -> str:
        return '/services{0}'.format(self.sub_url)

    @property
    @abc.abstractmethod
    def method(self) -> str:
        pass

    @property
    @abc.abstractmethod
    def obj(self):
        pass


class AoiValidationServiceRequest(ServiceRequestBase, SingleResultQuery):

    def __init__(self, aoi_obj):
        ServiceRequestBase.__init__(self)
        self._aoi_obj = aoi_obj

    @property
    def sub_url(self):
        return '/validate/aoi'

    @property
    def method(self) -> str:
        return 'post'

    @property
    def aoi_obj(self):
        return self._aoi_obj

    @property
    def obj(self):
        return self.aoi_obj


class Services:

    @staticmethod
    def validate_aoi(aoi_obj):
        return AoiValidationServiceRequest(aoi_obj)
