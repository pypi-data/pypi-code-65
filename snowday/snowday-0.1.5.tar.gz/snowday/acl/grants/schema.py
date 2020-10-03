from dataclasses import dataclass
from typing import Union

from snowday.acl.grants.base import BaseGrant
from snowday.objects.account import Role
from snowday.objects.database import Database, Schema
from snowday.acl.grants.util import get_future_privilege


@dataclass
class SchemaGrant(BaseGrant):
    subject: Schema


@dataclass
class FutureSchemaGrant:
    subject: Database
    grantee: Role

    @property
    def privilege(self):
        return get_future_privilege(self.__class__.__name__)

    @property
    def assign(self):
        return Sql(
            statement=(
                f"grant {self.privilege} on future schemas "
                f"in {self.subject.resource_type} {self.subject.name} "
                f"to role {self.grantee.name};"
            )
        )

    @property
    def revoke(self):
        return Sql(
            statement=(
                f"revoke {self.privilege} on future schemas "
                f"in {self.subject.resource_type} {self.subject.name} "
                f"from role {self.grantee.name};"
            )
        )


@dataclass
class FutureAllSchemaGrant(FutureSchemaGrant):
    @property
    def privilege(self):
        return "all"


@dataclass
class CreateTableGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateTableGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateExternalTableGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateExternalTableGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateViewGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateViewGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateMaterializedViewGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateMaterializedViewGrant(SchemaGrant):
    pass


@dataclass
class CreateMaskingPolicyGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateMaskingPolicyGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateFileFormatGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateFileFormatGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateStageGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateStageGrant(FutureSchemaGrant):
    pass


@dataclass
class CreatePipeGrant(SchemaGrant):
    pass


@dataclass
class FutureCreatePipeGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateStreamGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateStreamGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateTaskGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateTaskGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateSequenceGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateSequenceGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateFunctionGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateFunctionGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateUDFGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateUDFGrant(FutureSchemaGrant):
    pass


@dataclass
class CreateProcedureGrant(SchemaGrant):
    pass


@dataclass
class FutureCreateProcedureGrant(FutureSchemaGrant):
    pass
