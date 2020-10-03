from dataclasses import dataclass
from snowday.objects.account import Role
from snowday.acl.grants.base import BaseGrant
from snowday.acl.grants.util import get_privilege

from snowday.types.base import Sql


@dataclass
class AccountGrant(BaseGrant):
    @property
    def privilege(self):
        return get_privilege(self.__class__.__name__)

    @property
    def assign(self):
        return Sql(
            statement=f"grant {self.privilege} on account to role {self.grantee.name};"
        )

    @property
    def revoke(self):
        return Sql(
            statement=f"revoke {self.privilege} on account from role {self.grantee.name};"
        )


@dataclass
class CreateAccountGrant(AccountGrant):
    pass


@dataclass
class CreateRoleGrant(AccountGrant):
    pass


@dataclass
class CreateUserGrant(AccountGrant):
    pass


@dataclass
class CreateWarehouseGrant(AccountGrant):
    pass


@dataclass
class CreateDatabaseGrant(AccountGrant):
    pass


@dataclass
class CreateIntegrationGrant(AccountGrant):
    pass


@dataclass
class CreateSchemaGrant(AccountGrant):
    pass


@dataclass
class CreateShareGrant(AccountGrant):
    pass


@dataclass
class ImportShareGrant(AccountGrant):
    pass


@dataclass
class MonitorUsageGrant(AccountGrant):
    pass


@dataclass
class ManageGrantsGrant(AccountGrant):
    pass
