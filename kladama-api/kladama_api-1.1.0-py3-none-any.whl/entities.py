from abc import ABC


class Identifiable:

    def __init__(self, obj):
        self._name = obj['name']

    @property
    def name(self):
        return self._name


class Describable(Identifiable):

    def __init__(self, obj):
        Identifiable.__init__(self, obj)
        self._description = obj['description']

    @property
    def description(self):
        return self._description


class Linkable:

    def __init__(self, obj):
        links = obj['_links']
        self_link = links['self']
        self._link = self_link['href']
        all_links = {}
        for key in list(links.keys()):
            link = links[key]
            all_links[key] = link['href']

        self._all_links = all_links

    @property
    def link(self):
        return self._link

    @property
    def all_links(self):
        return self._all_links


# Entity DTO types

class EntityDTO(ABC):
    pass


class AreaOfInterest(EntityDTO, Describable, Linkable):

    def __init__(self, obj):
        Describable.__init__(self, obj)
        Linkable.__init__(self, obj)


class BinaryResult(EntityDTO, Identifiable):

    def __init__(self, obj):
        Identifiable.__init__(self, obj)
        self._content = obj['content']

    @property
    def content(self):
        return self._content


class Date(EntityDTO):

    def __init__(self, obj):
        self._year = obj['year']
        self._month = obj['month']
        self._day = obj['day']
        self._iso_str = obj['iso_str']

    @property
    def day(self):
        return self._day

    @property
    def month(self):
        return self._month

    @property
    def year(self):
        return self._year

    @property
    def iso_str(self):
        return self._iso_str


class Mask(EntityDTO, Describable, Linkable):

    def __init__(self, obj):
        Describable.__init__(self, obj)
        Linkable.__init__(self, obj)
        self._category = obj['category']
        self._resolution = obj['resolution']
        self._threshold = obj['threshold']
        self._owner = obj['owner']

    @property
    def category(self):
        return self._category

    @property
    def resolution(self):
        return self._resolution

    @property
    def threshold(self):
        return self._threshold

    @property
    def owner(self):
        return self._owner


class Organization(EntityDTO, Identifiable, Linkable):

    def __init__(self, obj):
        Identifiable.__init__(self, obj)
        Linkable.__init__(self, obj)
        self._acronym = obj['acronym']
        self._juridic_id = obj['juridic_id']
        self._address = obj['address']
        self._actual_credits = obj['actual_credits']
        self._migrated_credits = obj['migrated_credits']

    @property
    def acronym(self):
        return self._acronym

    @property
    def juridic_id(self):
        return self._juridic_id

    @property
    def address(self):
        return self._address

    @property
    def actual_credits(self):
        return self._actual_credits

    @property
    def migrated_credits(self):
        return self._migrated_credits


class Phenomena(EntityDTO, Describable, Linkable):

    def __init__(self, obj):
        Describable.__init__(self, obj)
        Linkable.__init__(self, obj)


class Schedule(EntityDTO, Linkable):

    def __init__(self, obj):
        Linkable.__init__(self, obj)
        self._job_id = obj['job_id']
        self._user = obj['user']
        self._organization = obj['organization']
        self._subscription = obj['subscription']
        self._data_source = obj['data_source']
        self._variable = obj['variable']
        self._cron_exp = obj['cron_exp']

    @property
    def job_id(self):
        return self._job_id

    @property
    def user(self):
        return self._user

    @property
    def organization(self):
        return self._organization

    @property
    def subscription(self):
        return self._subscription

    @property
    def data_source(self):
        return self._data_source

    @property
    def variable(self):
        return self._variable

    @property
    def cron_exp(self):
        return self._cron_exp


class SpatialOperation(EntityDTO, Describable):

    def __init__(self, obj):
        Describable.__init__(self, obj)
        self._type = obj['type']

    @property
    def type(self):
        return self._type


class Source(EntityDTO, Describable, Linkable):

    def __init__(self, obj):
        Describable.__init__(self, obj)
        Linkable.__init__(self, obj)


class Subscription(EntityDTO, Linkable):

    def __init__(self, obj):
        Linkable.__init__(self, obj)
        self._code = obj['code']
        self._owner = obj['owner']
        self._type = obj['type']
        self._created_timestamp = obj['created_timestamp']
        self._mask = Mask(obj['mask']) if obj['mask'] is not None else None
        self._spatial_operation = SpatialOperation(obj['spatial_operation'])
        self._status = obj['status']
        self._schedule = obj['schedule']
        self._aoi = obj['area_of_interest']
        self._variable = Variable(obj['variable'])

    @property
    def code(self):
        return self._code

    @property
    def owner(self):
        return self._owner

    @property
    def type(self):
        return self._type

    @property
    def created_timestamp(self):
        return self._created_timestamp

    @property
    def mask(self):
        return self._mask

    @property
    def spatial_operation(self):
        return self._spatial_operation

    @property
    def status(self):
        return self._status

    @property
    def schedule(self):
        return self._schedule

    @property
    def aoi(self):
        return self._aoi

    @property
    def variable(self):
        return self._variable


class User(EntityDTO, Identifiable, Linkable):

    def __init__(self, obj):
        Identifiable.__init__(self, obj)
        Linkable.__init__(self, obj)
        self._username = obj['login']
        self._organization = Organization(obj['organization'])

    @property
    def username(self):
        return self._username

    @property
    def organization(self):
        return self._organization


class Variable(EntityDTO, Describable, Linkable):

    def __init__(self, obj):
        Describable.__init__(self, obj)
        Linkable.__init__(self, obj)
        self._type = obj['type']
        self._schedule = obj['schedule']
        self._dataset = obj['dataset']
        self._spatial_resolution = obj['spatial_resolution']
        self._temporal_resolution = obj['temporal_resolution']
        self._phenomena = Phenomena(obj['phenomenon'])
        self._source = Source(obj['source'])

    @property
    def schedule(self):
        return self._schedule

    @property
    def dataset(self):
        return self._dataset

    @property
    def phenomena(self):
        return self._phenomena

    @property
    def spatial_resolution(self):
        return self._spatial_resolution

    @property
    def source(self):
        return self._source

    @property
    def temporal_resolution(self):
        return self._temporal_resolution

    @property
    def type(self):
        return self._type
