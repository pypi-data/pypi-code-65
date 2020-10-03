from dataclasses import dataclass
from typing import Union

from snowday.objects.account import Role, User, Warehouse, ResourceMonitor
from snowday.objects.database import Database, Schema
from snowday.objects.schema import (
    InternalStage,
    Function,
    FileFormat,
    AwsApiIntegration,
    Pipe,
    Procedure,
    Sequence,
    Stream,
    Task,
    ExternalStage,
    View,
)
from snowday.objects.table import Table
from snowday.acl.grants.base import BaseGrant


@dataclass
class OwnershipGrant(BaseGrant):
    # https://docs.snowflake.com/en/sql-reference/sql/grant-ownership.html
    subject: Union[
        Role,
        User,
        Warehouse,
        Database,
        Schema,
        Table,
        View,
        FileFormat,
        Stream,
        Task,
        Pipe,
        AwsApiIntegration,
        Function,
        Procedure,
        Sequence,
    ]
    revoke_current_grants = False
    copy_current_grants = True


@dataclass
class AllGrant(BaseGrant):
    subject: Union[Warehouse, Table, Schema, InternalStage, ExternalStage, View]


@dataclass
class UsageGrant(BaseGrant):
    subject: Union[
        Warehouse,
        Database,
        Schema,
        AwsApiIntegration,
        ExternalStage,
        FileFormat,
        Function,
        Sequence,
    ]


@dataclass
class OperateGrant(BaseGrant):
    subject: Union[Warehouse, Task]


@dataclass
class ModifyGrant(BaseGrant):
    subject: Union[Warehouse, Database, Schema, ResourceMonitor]


@dataclass
class MonitorGrant(BaseGrant):
    subject: Union[Warehouse, Database, Schema, ResourceMonitor, Task]


@dataclass
class CreateSchemaGrant(BaseGrant):
    subject: Database


@dataclass
class ImportedPrivilegesGrant(BaseGrant):
    subject: Database
