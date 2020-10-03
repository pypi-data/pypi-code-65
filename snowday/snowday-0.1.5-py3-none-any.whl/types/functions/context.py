from dataclasses import dataclass
from snowday.types.base import Sql


@dataclass
class ContextFunction:
    pass


# General context functions


@dataclass
class CurrentClient(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_client")


@dataclass
class CurrentDate(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_date")


@dataclass
class CurrentRegion(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_region")


@dataclass
class CurrentTime(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_time")


@dataclass
class CurrentTimestamp(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_timestamp")


@dataclass
class CurrentVersion(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_version")


@dataclass
class LocalTime(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="localtime")


@dataclass
class LocalTimestamp(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="localtimestamp")


@dataclass
class SysDate(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="sysdate")


# Session context functions


@dataclass
class CurrentAccount(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_account")


@dataclass
class CurrentRole(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_role")


@dataclass
class CurrentSession(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_session")


@dataclass
class CurrentStatement(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_statement")


@dataclass
class CurrentTransaction(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_transaction")


@dataclass
class CurrentUser(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_user")


@dataclass
class LastQueryId(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="last_query_id")


@dataclass
class LastTransaction(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="last_transaction")


# Session object context functions


@dataclass
class CurrentDatabase(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_database")


@dataclass
class CurrentSchema(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_schema")


@dataclass
class CurrentSchemas(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_schemas")


@dataclass
class CurrentWarehouse(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="current_warehouse")


@dataclass
class InvokerRole(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="invoker_role")


@dataclass
class InvokerShare(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="invoker_share")


@datdaclass
class IsGrantedToInvokerRole(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="is_granted_to_invoker_role")


@dataclass
class IsRoleInSession(ContextFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="is_role_in_session")
