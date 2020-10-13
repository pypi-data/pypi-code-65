import abc
from abc import ABC
import json


# Operations

class Transaction(ABC):

    @property
    @abc.abstractmethod
    def url_path(self) -> str:
        pass


class PostTransaction(Transaction, ABC):

    @property
    @abc.abstractmethod
    def post_obj(self):
        pass


class PutTransaction(Transaction, ABC):

    @property
    @abc.abstractmethod
    def put_obj(self):
        pass


class CreateTransaction(Transaction, ABC):

    def __init__(self):
        Transaction.__init__(self)


class DeleteTransaction(Transaction, ABC):
    pass


class CreateAreaOfInterestTransaction(CreateTransaction, PutTransaction):

    def __init__(
        self,
        user,
        name,
        description,
        category,
        features
    ):
        CreateTransaction.__init__(self)
        PutTransaction.__init__(self)
        self._user = user
        self._name = name
        self._description = description
        self._category = category
        self._features = features

    @property
    def url_path(self):
        return "/aoi/user/{0}/{1}".format(self._user, self._name)

    @property
    def put_obj(self):
        return {
            "description": self._description,
            "category": self._category,
            "features": self._features if isinstance(self._features, str) else json.dumps(self._features)
        }


class CreatePeriodicSubscriptionTransaction(CreateTransaction, PostTransaction):

    def __init__(
        self,
        user,
        variable_name,
        spatial_operation_name,
        aoi_name,
    ):
        CreateTransaction.__init__(self)
        PostTransaction.__init__(self)
        self._user = user
        self._variable_name = variable_name
        self._spatial_operation_name = spatial_operation_name
        self._aoi_name = aoi_name

    @property
    def url_path(self):
        return "/subsc/user/{0}".format(self._user)

    @property
    def post_obj(self):
        return {
            "type": "PERIODIC",
            "variable": {
                "name": self._variable_name
            },
            "spatial_operation": {
                "name": self._spatial_operation_name
            },
            "aoi": {
                "name": self._aoi_name
            }
        }


class DeleteAreaOfInterestTransaction(DeleteTransaction):

    def __init__(self, user, aoi_id):
        DeleteTransaction.__init__(self)
        self._user = user
        self._aoi_id = aoi_id

    @property
    def url_path(self) -> str:
        return "/aoi/user/{0}/{1}".format(self._user, self._aoi_id)


class DeleteSubscriptionTransaction(DeleteTransaction):

    def __init__(self, user, subscription_id):
        DeleteTransaction.__init__(self)
        self._user = user
        self._subscription_id = subscription_id

    @property
    def url_path(self) -> str:
        return "/subsc/user/{0}/{1}".format(self._user, self._subscription_id)


class CheckScheduleTransaction(PutTransaction):

    def __init__(self, user, *subscriptions):
        PutTransaction.__init__(self)
        self._user = user
        self._subscriptions = subscriptions

    @property
    def url_path(self) -> str:
        subscriptions_path = ''
        if len(self._subscriptions) > 0:
            subscriptions_path = '/subsc/{0}'.format(','.join(self._subscriptions))

        return '/schedule/user/{0}{1}'.format(self._user, subscriptions_path)

    @property
    def put_obj(self):
        return {}


class ClearScheduleTransaction(DeleteTransaction):

    def __init__(self, user, *subscriptions):
        DeleteTransaction.__init__(self)
        self._user = user
        self._subscriptions = subscriptions

    @property
    def url_path(self) -> str:
        subscriptions_path = ''
        if len(self._subscriptions) > 0:
            subscriptions_path = '/subsc/{0}'.format(','.join(self._subscriptions))

        return '/schedule/user/{0}{1}'.format(self._user, subscriptions_path)


class ReScheduleTransaction(PostTransaction):

    def __init__(self, user, *subscriptions):
        PostTransaction.__init__(self)
        self._user = user
        self._subscriptions = subscriptions

    @property
    def url_path(self) -> str:
        subscriptions_path = ''
        if len(self._subscriptions) > 0:
            subscriptions_path = '/subsc/{0}'.format(','.join(self._subscriptions))

        return '/schedule/user/{0}{1}'.format(self._user, subscriptions_path)

    @property
    def post_obj(self):
        return {}


# Builders

class TransactionBuilder(ABC):

    @abc.abstractmethod
    def build(self) -> Transaction:
        pass

    @property
    def url_path(self) -> str:
        return self.build().url_path


class CreateAreaOfInterestBuilder(TransactionBuilder):

    def __init__(self):
        TransactionBuilder.__init__(self)
        self._user = ""
        self._name = ""
        self._description = ""
        self._category = ""
        self._features = {}

    def build(self) -> CreateAreaOfInterestTransaction:
        return CreateAreaOfInterestTransaction(
            self._user,
            self._name,
            self._description,
            self._category,
            self._features
        )

    def for_user(self, user: str):
        self._user = user
        return self

    def with_name(self, name: str):
        self._name = name
        return self

    def with_description(self, description: str):
        self._description = description
        return self

    def with_category(self, category: str):
        self._category = category
        return self

    def with_features(self, features):
        self._features = features
        return self

    def from_file(self, file_path: str):
        with open(file_path, 'r') as file:
            data = file.read()
            features = json.loads(data)
            self.with_features(features)
            return self


class CreatePeriodicSubscriptionBuilder(TransactionBuilder):

    def __init__(self):
        TransactionBuilder.__init__(self)
        self._user = ""
        self._subscription_type = ""
        self._variable_name = ""
        self._variable_source_name = ""
        self._spatial_operation_name = ""
        self._aoi_name = ""

    def build(self) -> CreatePeriodicSubscriptionTransaction:
        return CreatePeriodicSubscriptionTransaction(
            self._user,
            self._variable_name,
            self._spatial_operation_name,
            self._aoi_name,
        )

    def for_user(self, user: str):
        self._user = user
        return self

    def with_variable(self, variable_name: str):
        self._variable_name = variable_name
        return self

    def with_operation(self, spatial_operation_name: str):
        self._spatial_operation_name = spatial_operation_name
        return self

    def with_aoi(self, aoi_name: str):
        self._aoi_name = aoi_name
        return self


class DeleteAreaOfInterestBuilder(TransactionBuilder):

    def __init__(self):
        TransactionBuilder.__init__(self)
        self._user = ""
        self._aoi_id = ""

    def build(self) -> DeleteAreaOfInterestTransaction:
        return DeleteAreaOfInterestTransaction(self._user, self._aoi_id)

    def from_user(self, user: str):
        self._user = user
        return self

    def with_aoi(self, aoi_id: str):
        self._aoi_id = aoi_id
        return self


class DeleteSubscriptionBuilder(TransactionBuilder):

    def __init__(self):
        TransactionBuilder.__init__(self)
        self._user = ""
        self._subscription_id = ""

    def build(self) -> DeleteSubscriptionTransaction:
        return DeleteSubscriptionTransaction(self._user, self._subscription_id)

    def from_user(self, user: str):
        self._user = user
        return self

    def with_subsc(self, subscription_id: str):
        self._subscription_id = subscription_id
        return self


class CheckScheduleBuilder(TransactionBuilder):

    def build(self) -> Transaction:
        return CheckScheduleTransaction(self._user, *self._subscriptions)

    def __init__(self):
        TransactionBuilder.__init__(self)
        self._user = ''
        self._subscriptions = []

    def for_user(self, user):
        self._user = user
        return self

    def for_subsc(self, *subscriptions):
        self._subscriptions = subscriptions
        return self


class ClearScheduleBuilder(TransactionBuilder):

    def build(self) -> Transaction:
        return ClearScheduleTransaction(self._user, *self._subscriptions)

    def __init__(self):
        TransactionBuilder.__init__(self)
        self._user = ''
        self._subscriptions = []

    def for_user(self, user):
        self._user = user
        return self

    def for_subsc(self, *subscriptions):
        self._subscriptions = subscriptions
        return self


class ReScheduleBuilder(TransactionBuilder):

    def build(self) -> Transaction:
        return ReScheduleTransaction(self._user, *self._subscriptions)

    def __init__(self):
        TransactionBuilder.__init__(self)
        self._user = ''
        self._subscriptions = []

    def for_user(self, user):
        self._user = user
        return self

    def for_subsc(self, *subscriptions):
        self._subscriptions = subscriptions
        return self


class Transactions:

    @property
    def add_aoi(self):
        return CreateAreaOfInterestBuilder()

    @property
    def check_schedule(self):
        return CheckScheduleBuilder()

    @property
    def clear_schedule(self):
        return ClearScheduleBuilder()

    @property
    def delete_aoi(self):
        return DeleteAreaOfInterestBuilder()

    @property
    def periodic_subsc(self):
        return CreatePeriodicSubscriptionBuilder()

    @property
    def re_schedule(self):
        return ReScheduleBuilder()

    @property
    def unsubscribe(self):
        return DeleteSubscriptionBuilder()
