from dataclasses import dataclass
from typing import Union
from snowday.objects.account import Role, User
from snowday.types.base import Sql


@dataclass
class RoleGrant:
    # https://docs.snowflake.com/en/sql-reference/sql/grant-role.html
    grantee: Union[Role, User]
    subject: Role

    @property
    def assign(self):
        return Sql(
            statement=f"grant role {self.subject.name} to {self.grantee.resource_type} {self.grantee.name};"
        )

    @property
    def revoke(self):
        return Sql(
            statement=f"revoke role {self.subject.name} from {self.grantee.resource_type} {self.grantee.name};"
        )
