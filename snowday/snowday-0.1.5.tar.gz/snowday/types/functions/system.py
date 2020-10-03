from dataclasses import dataclass
from typing import Union, List

from snowday.objects.account import (
    SecurityIntegrationSAML2,
    SecurityIntegrationSCIM,
    SecurityIntegrationOAuth,
    SecurityIntegrationOAuthCustom,
    SecurityIntegrationOAuthPartnerApp,
)
from snowday.objects.database import DatabaseReplica
from snowday.objects.schema import Stream, Pipe, View, Task
from snowday.objects.table import Table, ACCEPTED_TABLE_COLUMNS
from snowday.types.base import (
    Sql,
    Session,
    Transaction,
    Query,
    ExplainJson,
    TimeUnit,
    SnsTopic,
)


@dataclass
class SystemFunction:
    pass


@dataclass
class AbortSession(SystemFunction):
    session: Session

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$abort_session({session.id})")


@dataclass
class AbortTransaction(SystemFunction):
    transaction: Transaction

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$abort_transaction({transaction.id})")


@dataclass
class CancelAllQueries(SystemFunction):
    session: Session

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$cancel_all_queries({session.id})")


@dataclass
class CancelQuery(SystemFunction):
    query: Query

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$cancel_query({query.id})")


@dataclass
class ClusteringDepth(SystemFunction):
    table: Table
    columns: List[Union[ACCEPTED_TABLE_COLUMNS]] = None
    predicate: Sql = None

    @property
    def sql(self) -> Sql:
        # FIXME! Write the appropriate sql here.
        return f""


@dataclass
class ClusteringInformation(SystemFunction):
    table: Table
    columns: List[Union[ACCEPTED_TABLE_COLUMNS]] = None

    @property
    def sql(self) -> Sql:
        # FIXME! Write the appropriate sql here.
        return f""


@dataclass
class CurrentUserTaskName(SystemFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="system$current_user_task_name()")


@dataclass
class DatabaseRefreshHistory(SystemFunction):
    database_replica: DatabaseReplica

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=f"system$database_refresh_history('{database_replica.fqn}')"
        )


@dataclass
class DatabaseRefreshProgress(SystemFunction):
    database_replica: DatabaseReplica

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=f"system$database_refresh_progress('{database_replica.fqn}')"
        )


@dataclass
class DatabaseRefreshProgressByJob(SystemFunction):
    query: Query

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$database_refresh_progress_by_job('{query.id}')")


@dataclass
class EstimateSearchOptimizationCosts(SystemFunction):
    table: Table

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=f"system$estimate_search_optimization_costs('{table.fqn}')"
        )


@dataclass
class ExplainJsonToText(SystemFunction):
    explain_json: ExplainJson

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"")


@dataclass
class ExplainPlanJson(SystemFunction):
    subject: Union[Sql, Query]

    @property
    def sql(self) -> Sql:
        delimiter = "'" if isinstance(self.subject, Query) else "$$"
        subject = (
            self.subject.statement if isinstance(self.subject, Sql) else self.subject.id
        )
        return Sql(
            statement=f"system$explain_plan_json({delimiter}{subject}{delimiter})"
        )


@dataclass
class GenerateSAML2Csr(SystemFunction):
    security_integration: SecurityIntegrationSAML2
    distinguished_name: str = None

    @property
    def sql(self) -> Sql:
        param = f"'{self.security_integration.fqn}'"
        if self.distinguished_name:
            param = param + f", '{self.distinguished_name}'"
        return Sql(statement=f"system$generate_saml_csr({param})")


@dataclass
class GenerateSCIMAccessToken(SystemFunction):
    security_integration: SecurityIntegrationSCIM

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=f"system$generate_scim_access_token('{self.security_integration.fqn}')"
        )


@dataclass
class GetAwsSnsIamPolicy(SystemFunction):
    sns_topic: SnsTopic

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$get_aws_sns_iam_policy('{self.sns_topic.arn}')")


@dataclass
class GetPredecessorReturnValue(SystemFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$get_predecessor_return_value()")


@dataclass
class GetPrivatelinkConfig(SystemFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$get_privatelink_config()")


@dataclass
class GetSnowflakePlatformInfo(SystemFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$get_snowflake_platform_info()")


@dataclass
class LastChangeCommitTime(SystemFunction):
    subject: Union[Table, View]

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$last_change_commit_time('{self.subject.fqn}')")


@dataclass
class MigrateSAMLIdpRegistration(SystemFunction):
    security_integration: SecurityIntegrationSAML2
    issuer: str

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=f"system$migrate_saml_idp_registration('{self.security_integration.fqn}', '{self.issuer}')"
        )


@dataclass
class PipeForceResume(SystemFunction):
    pipe: Pipe

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$pipe_force_resume('{self.pipe.fqn}')")


@dataclass
class PipeStatus(SystemFunction):
    pipe: Pipe

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$pipe_status('{self.pipe.fqn}')")


@dataclass
class SetReturnValue(SystemFunction):
    return_value: str

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$set_return_value('{self.return_value}')")


@dataclass
class ShowOAuthClientSecrets(SystemFunction):
    security_integration: Union[
        SecurityIntegrationOAuth,
        SecurityIntegrationOAuthCustom,
        SecurityIntegrationOAuthPartnerApp,
    ]

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=f"system$show_oauth_client_secrets('{security_integration.fqn}')"
        )


@dataclass
class StreamGetTableTimestamp(SystemFunction):
    stream: Stream

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$stream_get_table_timestamp('{stream.fqn}')")


@dataclass
class StreamHasData(SystemFunction):
    stream: Stream

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$stream_has_data('{stream.fqn}')")


@dataclass
class TaskDependentsEnable(SystemFunction):
    task: Task

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$task_dependents_enable('{task.fqn}')")


@dataclass
class UserTaskCancelOngoingExecutions(SystemFunction):
    task: Task

    @property
    def sql(self) -> Sql:
        return Sql(
            statement=f"system$user_task_cancel_ongoing_executions('{task.fqn}')"
        )


@dataclass
class VerifyExternalOAuthToken(SystemFunction):
    access_token: str

    @property
    def sql(self) -> Sql:
        return Sql(statement=f"system$verify_external_oauth_token('{access_token}')")


@dataclass
class Wait(SystemFunction):
    duration: int
    time_unit: TimeUnit = None

    @property
    def sql(self) -> Sql:
        wait = f"{self.duration}"
        if self.time_unit:
            wait = f"{wait}, '{self.time_unit.unit}'"
        return Sql(statement=f"system$wait({wait})")


@dataclass
class Whitelist(SystemFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="system$whitelist()")


@dataclass
class WhitelistPrivateLink(SystemFunction):
    @property
    def sql(self) -> Sql:
        return Sql(statement="system$whitelist_privatelink()")
