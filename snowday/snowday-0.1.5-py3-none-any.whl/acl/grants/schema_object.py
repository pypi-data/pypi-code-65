from dataclasses import dataclass
from typing import Union


from snowday.acl.grants.base import BaseGrant
from snowday.acl.grants.util import get_future_privilege
from snowday.objects.account import Role
from snowday.objects.database import Database
from snowday.objects.schema import (
    View,
    MaterializedView,
    Schema,
    Stream,
    MaskingPolicy,
    InternalStage,
)
from snowday.objects.table import Table
from snowday.types.base import Sql


@dataclass
class SchemaObjectGrant(BaseGrant):
    pass


@dataclass
class FutureSchemaObjectGrant:
    # FIXME! Is this the right way forward? Is there a downside here?
    # What is a better way to incorporate future grants on schema objects?
    #
    grantee: Role

    @property
    def privilege(self):
        return get_future_privilege(self.__class__.__name__)

    @property
    def _plural_subject_type(self, suffix="s"):
        return f"{self.subject.__class__.__name__.lower()}{suffix}"

    @property
    def assign(self):
        return Sql(
            statement=(
                f"grant {self.privilege} "
                f"on future {self._plural_subject_type} "
                f"in {self.namespace.resource_type} {self.namespace.name} "
                f"to {self.subject.resource_type} {self.subject.name};"
            )
        )

    @property
    def revoke(self):
        return Sql(
            statement=(
                f"revoke {self.privilege} "
                f"on future {self._plural_subject_type} "
                f"in {self.namespace.resource_type} {self.namespace.name} "
                f"from {self.subject.resource_type} {self.subject.name};"
            )
        )


@dataclass
class SelectGrant(SchemaObjectGrant):
    subject: Union[Table, View, MaterializedView, Stream]


@dataclass
class FutureSelectGrant(FutureSchemaObjectGrant):
    subject: Union[Table, View, MaterializedView, Stream]
    namespace: Union[Database, Schema]


@dataclass
class InsertGrant(SchemaObjectGrant):
    subject: Table


@dataclass
class FutureInsertGrant(FutureSchemaObjectGrant):
    subject: Table
    namespace: Union[Database, Schema]


@dataclass
class UpdateGrant(SchemaObjectGrant):
    subject: Table


@dataclass
class FutureUpdateGrant(FutureSchemaObjectGrant):
    subject: Table
    namespace: Union[Database, Schema]


@dataclass
class DeleteGrant(SchemaObjectGrant):
    subject: Table


@dataclass
class FutureDeleteGrant(FutureSchemaObjectGrant):
    subject: Table
    namespace: Union[Database, Schema]


@dataclass
class TruncateGrant(SchemaObjectGrant):
    subject: Table


@dataclass
class FutureTruncateGrant(FutureSchemaObjectGrant):
    subject: Table
    namespace: Union[Database, Schema]


@dataclass
class ReferencesGrant(SchemaObjectGrant):
    subject: Table


@dataclass
class FutureReferencesGrant(FutureSchemaObjectGrant):
    subject: Table
    namespace: Union[Database, Schema]


@dataclass
class ReadGrant(SchemaObjectGrant):
    subject: InternalStage


@dataclass
class FutureReadGrant(FutureSchemaObjectGrant):
    subject: InternalStage
    namespace: Union[Database, Schema]


@dataclass
class WriteGrant(SchemaObjectGrant):
    subject: InternalStage


@dataclass
class FutureWriteGrant(FutureSchemaObjectGrant):
    subject: InternalStage
    namespace: Union[Database, Schema]


@dataclass
class ApplyGrant(SchemaObjectGrant):
    subject: MaskingPolicy


@dataclass
class FutureApplyGrant(FutureSchemaObjectGrant):
    subject: MaskingPolicy
    namespace: Union[Database, Schema]
