import atexit
from contextlib import contextmanager
from typing import Union, Iterator, List

import snowflake.connector as sf_connector

from snowday.exceptions import MustHaveForceOverride
from snowday.logger import get_logger
from snowday.objects.account import (
    Account,
    ManagedAccount,
    AwsApiIntegration,
    NetworkPolicy,
    ResourceMonitor,
    Share,
    Warehouse,
    Role,
    User,
    AzureNotificationIntegration,
    SecurityIntegrationOAuth,
    SecurityIntegrationOAuthPartnerApp,
    SecurityIntegrationOAuthCustom,
    SecurityIntegrationSAML2,
    SecurityIntegrationSCIM,
    StorageIntegrationS3,
    StorageIntegrationGCS,
    StorageIntegrationAzure,
)
from snowday.objects.database import (
    Database,
    DatabaseFromShare,
    DatabaseReplica,
    Schema,
)
from snowday.objects.schema import (
    Task,
    View,
    MaterializedView,
    MaskingPolicy,
    FileFormat,
    InternalStage,
    ExternalStage,
    Pipe,
    Stream,
    Function,
    Procedure,
    Sequence,
)
from snowday.objects.table import Table
from snowday.types.base import Sql, SessionParameter, QueryResult, QueryResultSet

LOG = get_logger()

ALL_OBJS = Union[
    Account,
    ManagedAccount,
    AwsApiIntegration,
    NetworkPolicy,
    ResourceMonitor,
    Share,
    Warehouse,
    Role,
    User,
    AzureNotificationIntegration,
    SecurityIntegrationOAuth,
    SecurityIntegrationOAuthPartnerApp,
    SecurityIntegrationOAuthCustom,
    SecurityIntegrationSAML2,
    SecurityIntegrationSCIM,
    StorageIntegrationS3,
    StorageIntegrationGCS,
    StorageIntegrationAzure,
    Database,
    DatabaseFromShare,
    DatabaseReplica,
    Schema,
    Task,
    View,
    MaterializedView,
    MaskingPolicy,
    FileFormat,
    InternalStage,
    ExternalStage,
    Pipe,
    Stream,
    Function,
    Procedure,
    Sequence,
    Table,
]


UTC = "UTC"
Q_TAG = "[snowday]"
APP = f"PythonConnector {Q_TAG}"

ROLLBACK = Sql(statement="rollback;")
COMMIT = Sql(statement="commit;")


class Connector:
    def __init__(self, **connection_kwargs):
        self.verbose = True
        for k, v in connection_kwargs.items():
            if k.lower() != "password":
                setattr(self, k, v)
            else:
                setattr(self, k, "*" * len(v))
        self.query_tag = Q_TAG
        self.search_path = None
        self.connection = sf_connector.connect(
            application=APP,
            internal_application_name=APP,
            session_parameters={"QUERY_TAG": Q_TAG},
            **connection_kwargs,
        )
        self.cursor = self.connection.cursor(sf_connector.DictCursor)

        def snowstopper() -> None:  # pragma: no cover
            self.cursor.close()
            self.connection.close()

        atexit.register(snowstopper)

    def __enter__(self, **kwargs):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.verbose:
            LOG.info(COMMIT.statement)
        self.cursor.execute(COMMIT.statement)

    def enable_verbose(self) -> None:
        self.verbose = True

    def disable_verbose(self) -> None:
        self.verbose = False

    def execute_safe(self, sql: Sql) -> Union[sf_connector.DictCursor, Exception]:
        try:
            if self.verbose:
                LOG.info(sql.statement)
            return self.cursor.execute(sql.statement)
        except Exception as e:
            self.cursor.execute(ROLLBACK.statement)
            if self.verbose:
                LOG.info(ROLLBACK.statement)
                LOG.error(sql.statement)
                LOG.debug(e)
            raise e

    def use(self, subject: Union[Warehouse, Database, Schema]) -> dict:
        """A mechanism for quickly navigating the primary search path.
        """
        if subject.__class__ == Warehouse:
            self.warehouse = subject.fqn
        else:
            self.search_path = subject.fqn
        sql = Sql(statement=f"use {subject.resource_type} {subject.fqn};")
        return self.fetch(sql)

    def set_session_param(self, session_param: SessionParameter) -> None:
        """A mechanism for setting an arbitrary session parameter.
        """
        sql = Sql(
            statement=(
                f"alter session set " f"{session_param.name} = '{session_param.value}';"
            )
        )
        self.execute_safe(sql)

    def set_session_params(self, session_params: List[SessionParameter]) -> None:
        """A mechanism for setting multiple session parameters.
        """
        for session_param in session_params:
            self.set_session_param(session_param)

    def set_query_tag(self, query_tag) -> None:
        """A mechanism for quickly setting query tags.
        """
        q_tag = SessionParameter(name="query_tag", value=f"{query_tag} {Q_TAG}")
        self.query_tag = q_tag
        self.set_session_param(q_tag)

    def set_utc(self) -> None:
        """A mechanism for quickly setting the session timezone to UTC.
        """
        tz = SessionParameter(name="timezone", value=UTC)
        self.set_session_param(tz)

    def fetchone(self, sql: Sql) -> QueryResult:
        return QueryResult(result=self.execute_safe(sql).fetchone())

    def fetch(self, sql: Sql) -> QueryResult:
        """An alias for fetchone
        """
        return self.fetchone(sql)

    def fetch_raw(self, sql: str) -> QueryResult:
        """A way to execute raw sql and fetch the first result
        """
        sql = Sql(statement=sql)
        return self.fetch(sql)

    def _fetchall(self, sql: Sql) -> dict:
        return self.execute_safe(sql).fetchall()

    def yield_all(self, sql: Sql) -> Iterator[QueryResult]:
        for result in self._fetchall(sql):
            yield QueryResult(result=result)

    def yield_all_raw(self, sql: str) -> Iterator[QueryResult]:
        sql = Sql(statement=sql)
        for result in self.yield_all(sql):
            yield result

    def commit(self) -> QueryResult:
        sql = Sql(statement="commit;")
        if self.verbose:
            LOG.info(sql.statement)
        return QueryResult(result=self.cursor.execute(sql.statement).fetchone())

    def rollback(self) -> QueryResult:
        sql = Sql(statement="rollback;")
        if self.verbose:
            LOG.info(sql.statement)
        return QueryResult(result=self.cursor.execute(sql.statement).fetchone())

    def create(self, obj: ALL_OBJS) -> QueryResult:
        return self.fetch(obj.create)

    def create_if_not_exists(self, obj: ALL_OBJS) -> QueryResult:
        return self.fetch(obj.create_if_not_exists)

    def create_or_replace(self, obj: ALL_OBJS) -> QueryResult:
        return self.fetch(obj.create_or_replace)

    def drop(self, obj: ALL_OBJS, force: bool = False) -> QueryResult:
        if force:
            return self.fetch(obj.drop)
        else:
            raise MustHaveForceOverride(
                f"Dropping {obj} must be forced. Please provide force=True argument."
            )

    def describe(self, obj: ALL_OBJS) -> QueryResult:
        return self.fetch(obj.describe)

    ########################################################################
    # Grant helpers
    ########################################################################

    def grant(self, grant) -> QueryResult:
        return self.fetch(grant.assign)

    def revoke(self, grant) -> QueryResult:
        return self.fetch(grant.revoke)
