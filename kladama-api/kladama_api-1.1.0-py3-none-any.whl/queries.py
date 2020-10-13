import abc
from abc import ABC


# Base type

class QueryBase(ABC):

    def __init__(self, parent):
        self._parent = parent

    @property
    def parent(self):
        return self._parent

    @property
    def url_path(self) -> str:
        return '{0}{1}'.format(self._parent.url_path, self.sub_url)

    @property
    @abc.abstractmethod
    def sub_url(self):
        pass


class SingleResultQuery(QueryBase, ABC):
    pass


# Filter Query types

class FilterQuery(QueryBase, ABC):

    def __init__(self, parent: QueryBase, filter_value):
        QueryBase.__init__(self, parent)
        self._filter_value = filter_value

    @property
    def _collection_filter_value_path(self):
        return ','.join(self._filter_value)


class ByDatesQuery(FilterQuery):

    def __init__(self, parent, *dates):
        FilterQuery.__init__(self, parent, dates)

    @property
    def sub_url(self):
        dates_path = '/dates'
        if len(self._filter_value) > 0:
            return '{0}/{1}'.format(dates_path, self._collection_filter_value_path)

        return dates_path


class ByDatePeriodQuery(QueryBase):

    def __init__(self, parent, from_, to):
        QueryBase.__init__(self, parent)
        self._from = from_
        self._to = to

    @property
    def sub_url(self):
        return '/dates/{0}TO{1}'.format(self._from, self._to)


class ByKeyQuery(FilterQuery, SingleResultQuery):

    @property
    def sub_url(self):
        return '/{0}'.format(self._filter_value)


class ByPhenomenaQuery(FilterQuery):

    @property
    def sub_url(self):
        return '/phenom/{0}'.format(self._filter_value)


class BySourcesQuery(FilterQuery):

    def __init__(self, parent, *sources):
        FilterQuery.__init__(self, parent, sources)

    @property
    def sub_url(self):
        return '/src/{0}'.format(self._collection_filter_value_path)


class ByStatusQuery(FilterQuery):

    @property
    def sub_url(self):
        return '/status/{0}'.format(self._filter_value)


class BySubscriptionsQuery(FilterQuery):

    def __init__(self, parent, *subscriptions):
        FilterQuery.__init__(self, parent, subscriptions)

    @property
    def sub_url(self):
        result = '/subsc'
        if len(self._filter_value) > 0:
            subscriptions = self._collection_filter_value_path
            return '{0}/{1}'.format(result, subscriptions)

        return result


class ByUserQuery(FilterQuery):

    @property
    def sub_url(self):
        return '/user/{0}'.format(self._filter_value)


class ForecastQuery(QueryBase):

    def __init__(self, parent):
        QueryBase.__init__(self, parent)

    @property
    def sub_url(self):
        return '/forecast'


class ObservedQuery(QueryBase):

    def __init__(self, parent):
        QueryBase.__init__(self, parent)

    @property
    def sub_url(self):
        return '/observed'


# Result queries

class AroundQuery(QueryBase):

    def __init__(self, parent, days, *dates):
        QueryBase.__init__(self, parent)
        self._days = days
        self._dates = dates

    @property
    def sub_url(self) -> str:
        return '/{1}around{2}'.format(self.parent.url_path, self._days, '/' + ','.join(*self._dates))


class LastQuery(QueryBase):

    def __init__(self, parent):
        QueryBase.__init__(self, parent)

    @property
    def sub_url(self):
        return '/last'


class LastNQuery(QueryBase):

    def __init__(self, parent, count: int):
        QueryBase.__init__(self, parent)
        self._count = count

    @property
    def sub_url(self):
        return '/last{0}'.format(self._count)


class LastNYearsQuery(QueryBase):

    def __init__(self, parent, years: int, *dates):
        QueryBase.__init__(self, parent)
        self._years = years
        self._dates = dates

    @property
    def sub_url(self):
        dates_path = ','.join(self._dates)
        return '/{0}years{1}'.format(self._years, '/' + dates_path)


class PeriodQuery(QueryBase):

    def __init__(self, parent, from_, to):
        QueryBase.__init__(self, parent)
        self._from = from_
        self._to = to

    @property
    def sub_url(self):
        return '/period/{0}TO{1}'.format(self._from, self._to)


class ResultsQuery(QueryBase):

    def __init__(self, parent):
        QueryBase.__init__(self, parent)

    @property
    def sub_url(self):
        return '/results'

    def around(self, days: int, *dates):
        return AroundQuery(self, days, dates)

    def dates(self, *dates):
        return ByDatesQuery(self, *dates)

    @property
    def last(self):
        return LastQuery(self)

    def last_n(self, count: int):
        return LastNQuery(self, count)

    def last_n_years(self, years: int, *dates):
        return LastNYearsQuery(self, years, *dates)

    def period(self, from_, to):
        return PeriodQuery(self, from_, to)


# Queryable types

class ByKeyQueryable(QueryBase, ABC):

    def by_key(self, name):
        return ByKeyQuery(self, name)


class ByDatesQueryable(QueryBase, ABC):

    def by_dates(self, *dates):
        return ByDatesQuery(self, *dates)


class ByPhenomenaQueryable(QueryBase, ABC):

    def by_phenomena(self, phenomena):
        return ByPhenomenaQuery(self, phenomena)


class BySourcesQueryable(QueryBase, ABC):

    def by_sources(self, *sources):
        return BySourcesQuery(self, *sources)


class ByStatusQueryable(QueryBase, ABC):

    def by_status(self, status):
        return ByStatusQuery(self, status)


class BySubscriptionsQueryable(QueryBase, ABC):

    def by_subsc(self, *subscriptions):
        return BySubscriptionsQuery(self, *subscriptions)


class ByUserQueryable(QueryBase, ABC):

    def by_user(self, user):
        return ByUserQuery(self, user)


class ForecastQueryable(QueryBase, ABC):

    @property
    def forecast(self):
        return ForecastQuery(self)


class ObservedQueryable(QueryBase, ABC):

    @property
    def observed(self):
        return ObservedQuery(self)


# Specific queries


class GetSubscriptionQuery(ByKeyQuery):

    @property
    def results(self):
        return ResultsQuery(self)

    @property
    def dates(self):
        return ByDatesQuery(self)

    def dates_since(self, from_):
        return ByDatePeriodQuery(self, from_, 'NOW')

    def dates_in(self, from_, to):
        return ByDatePeriodQuery(self, from_, to)


class GetSubscriptionQueryable(QueryBase, ABC):

    def by_subsc(self, subscription):
        return GetSubscriptionQuery(self, subscription)


class AfterUserByKeyQueryable(ByUserQuery, ByKeyQueryable, ABC):
    pass


class AfterUserBySubscriptionsQueryable(ByUserQuery):

    def by_subsc(self, *subscriptions):
        return BySubscriptionsQuery(self, *subscriptions)


class AfterUserGetSubscriptionQueryable(ByUserQuery, ByStatusQueryable):

    def filter_by(self, subscription):
        return GetSubscriptionQuery(self, subscription)


class AfterPhenomenaGetForecastObservedQueryable(ByPhenomenaQuery, ForecastQueryable, ObservedQueryable, ABC):
    pass


class AfterSourcesGetForecastObservedQueryable(BySourcesQuery, ForecastQueryable, ObservedQueryable, ABC):
    pass


class AfterUserByKeyStatusQueryable(AfterUserByKeyQueryable, ByStatusQueryable, ABC):

    def by_key(self, key):
        return GetSubscriptionQuery(self, key)


# Endpoint Query types

class EndpointQuery(QueryBase, ABC):

    def __init__(self):
        QueryBase.__init__(self, None)

    @property
    def url_path(self) -> str:
        return self.sub_url


class AreaOfInterestQuery(EndpointQuery, ByKeyQueryable, ByUserQueryable):

    @property
    def sub_url(self):
        return '/aoi'

    def by_user(self, user):
        return AfterUserByKeyQueryable(self, user)


class OrganizationQuery(EndpointQuery, ByKeyQueryable):

    @property
    def sub_url(self):
        return '/org'


class PhenomenaQuery(EndpointQuery, ByKeyQueryable, BySourcesQueryable, ForecastQueryable, ObservedQueryable):

    @property
    def sub_url(self):
        return '/phenom'

    def by_sources(self, *sources):
        return AfterSourcesGetForecastObservedQueryable(self, *sources)


class ScheduleQuery(EndpointQuery, ByUserQueryable):

    @property
    def sub_url(self):
        return '/schedule'

    def by_user(self, user):
        return AfterUserBySubscriptionsQueryable(self, user)


class SourceQuery(EndpointQuery, ByKeyQueryable, ByPhenomenaQueryable, ForecastQueryable, ObservedQueryable):

    @property
    def sub_url(self):
        return '/src'

    def by_phenomena(self, phenomena):
        return AfterPhenomenaGetForecastObservedQueryable(self, phenomena)


class SpatialOperationQuery(EndpointQuery):

    @property
    def sub_url(self):
        return '/oper'


class SubscriptionQuery(EndpointQuery, ByKeyQueryable, ByUserQueryable, ByStatusQueryable):

    @property
    def sub_url(self):
        return '/subsc'

    def by_key(self, name):
        return GetSubscriptionQuery(self, name)

    def by_user(self, user):
        return AfterUserByKeyStatusQueryable(self, user)


class UserQuery(EndpointQuery, ByKeyQueryable):

    @property
    def sub_url(self):
        return '/user'


class VariableQuery(EndpointQuery, ByKeyQueryable, ByPhenomenaQueryable, BySourcesQueryable, ForecastQueryable,
                    ObservedQueryable):

    @property
    def sub_url(self):
        return '/var'

    def by_phenomena(self, phenomena):
        return AfterPhenomenaGetForecastObservedQueryable(self, phenomena)

    def by_sources(self, *sources):
        return AfterSourcesGetForecastObservedQueryable(self, *sources)


# Query

class Queries:

    @property
    def aoi(self):
        return AreaOfInterestQuery()

    @property
    def oper(self):
        return SpatialOperationQuery()

    @property
    def org(self):
        return OrganizationQuery()

    @property
    def phenom(self):
        return PhenomenaQuery()

    @property
    def schedule(self):
        return ScheduleQuery()

    @property
    def subsc(self):
        return SubscriptionQuery()

    @property
    def src(self):
        return SourceQuery()

    @property
    def user(self):
        return UserQuery()

    @property
    def var(self):
        return VariableQuery()
