from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Union

from snowday.objects.base import BaseSnowflakeObject
from snowday.exceptions import (
    InvalidParamsException,
    InvalidWhitespaceException,
    UnsupportedFeatureException,
)
from snowday.types.base import Sql


EDITIONS = ["standard", "enterprise", "business_critical"]

REGIONS = [
    # aws
    "us-east-1",
    "us-east-2",
    "us-west-2",
    "ca-central-1",
    "eu-central-1",
    "eu-west-1",
    "ap-northeast-1",
    "ap-south-1",
    "ap-southeast-1",
    "ap-southeast-2",
    # azure
    "east-us-2",
    "west-us-2",
    "canada-central",
    "us-gov-virginia",
    "west-europe",
    "switzerland-north",
    "southeast-asia",
    "australia-east",
    # gcp
    "us-central1",
    "europe-west2",
    "europe-west4",
]

WAREHOUSE_SIZES = [
    "xsmall",
    "small",
    "medium",
    "large",
    "xlarge",
    "xxlarge",
    "xxxlarge",
]

SCALING_POLICIES = ["economy", "standard"]

RESOURCE_MONITOR_TRIGGER_ACTIONS = ["suspend", "suspend_immediate", "notify"]

RESOURCE_MONITOR_FREQUENCIES = [
    "monthly",
    "daily",
    "weekly",
    "yearly",
    "never",
]

EXTERNAL_OAUTH_TYPES = ["okta", "azure", "ping_federate", "custom"]


@dataclass
class Account:

    name: str
    admin_name: str
    admin_password: str
    email: str
    edition: str
    region: str
    comment: str

    def _validate(self):
        # FIXME! Make me run on init
        if self.edition.lower() not in EDITIONS:
            raise InvalidParamsException(
                f"{self.edition} is not a valid snowflake edition. Options include: {EDITIONS}"
            )
        if self.region.lower() not in REGIONS:
            raise InvalidParamsException(
                f"{self.region} is not a valid snowflake region. Options include: {REGIONS}"
            )
        self.name = self.name.upper()

    @property
    def create(self):
        return Sql(
            statement=(
                f"create account {self.name} "
                f"admin_name={self.admin_name}, admin_password='{self.admin_password}', "
                f"email='{self.email}', edition={self.edition}, "
                f"region='{self.region}' comment='{self.comment}';"
            )
        )

    @property
    def drop(self):
        return Sql(statement=f"drop account {self.name};")

    @property
    def enable_replication(self):
        return Sql(
            statement=f"select system$global_account_set_parameter('{self.name}', 'ENABLE_ACCOUNT_DATABASE_REPLICATION', 'true');"
        )

    @property
    def disable_replication(self):
        return Sql(
            statement=f"select system$global_account_set_parameter('{self.name}', 'ENABLE_ACCOUNT_DATABASE_REPLICATION', 'false');"
        )


@dataclass
class AccountObject(BaseSnowflakeObject):
    pass


@dataclass
class ManagedAccount(BaseSnowflakeObject):
    admin_name: str
    admin_password: str
    comment: str = ""
    type: str = "READER"

    @property
    def resource_type(self):
        return "managed account"

    @property
    def describe(self):
        raise NotImplementedError("describe is not supported on managed accounts")

    @property
    def create_if_not_exists(self):
        raise NotImplementedError(
            "create if not exists is not supported on managed accounts"
        )

    @property
    def create_or_replace(self):
        raise NotImplementedError(
            "create or replace is not supported on managed accounts"
        )


@dataclass
class AwsApiIntegration(AccountObject):
    api_aws_role_arn: str = ""
    api_provider: str = "aws_api_gateway"
    api_allowed_prefixes: List[str] = field(default_factory=list)
    api_blocked_prefixes: List[str] = field(default_factory=list)
    comment: str = ""
    enabled: bool = True

    @property
    def resource_type(self):
        return "api integration"


@dataclass
class NetworkPolicy(AccountObject):
    allowed_ips: List[str] = field(default_factory=list)
    blocked_ips: List[str] = field(default_factory=list)
    comment: str = ""

    @property
    def create_if_not_exists(self):
        raise UnsupportedFeatureException(
            "Create if not exists for snowflake network policies is unsupported."
        )


@dataclass
class ResourceMonitorTrigger:
    on_percent: int
    do: str

    def _validate(self):
        if self.do.lower() not in RESOURCE_MONITOR_TRIGGER_ACTIONS:
            raise InvalidParamsException(
                f"{self.do} is not a supported resource monitor trigger action. Options include: {RESOURCE_MONITOR_TRIGGER_ACTIONS}"
            )

    @property
    def sql(self):
        return f"on {self.on_percent} percent do {self.do}"


@dataclass
class ResourceMonitor(AccountObject):
    triggers: List[ResourceMonitorTrigger]
    credit_quota: int = 1
    frequency: str = "never"
    start_timestamp: Union[datetime, str] = "immediately"
    end_timestamp: datetime = None

    def _validate(self):
        if self.frequency.lower() not in RESOURCE_MONITOR_FREQUENCIES:
            raise InvalidParamsException(
                f"{self.frequency} is not a valid resource monitor frequency. Options include: {RESOURCE_MONITOR_FREQUENCIES}"
            )
        if (
            isinstance(self.start_timestamp, str)
            and self.start_timestamp.lower != "immediately"
        ):
            raise InvalidParamsException(
                f"{self.start_timestamp} is not a valid resource monitor start. It must be 'immediately' or a corresponding datetime."
            )

    @property
    def _settings_str(self):
        end_timestamp_str = f"end_timestamp =  " if self.end_timestamp else ""
        return (
            f"with credit_quota={self.credit_quota} "
            f"frequency={self.frequency} "
            f"start_timestamp={self.start_timestamp} "
            f"{end_timestamp_str}"
            f"triggers {self._format_triggers()}"
        )

    def _format_triggers(self):
        return " ".join([trigger.sql for trigger in self.triggers])

    @property
    def create_if_not_exists(self):
        raise UnsupportedFeatureException(
            "Create if not exists for snowflake resource monitors is unsupported."
        )


@dataclass
class Share(AccountObject):
    comment: str = ""

    @property
    def create_if_not_exists(self):
        raise UnsupportedFeatureException(
            "Create if not exists for snowflake shares is unsupported."
        )


@dataclass
class Warehouse(AccountObject):
    warehouse_size: str = "xsmall"
    auto_suspend: int = 60
    auto_resume: bool = True
    initially_suspended: bool = True
    max_concurrency_level: int = 10
    statement_queued_timeout_in_seconds: int = 600
    statement_timeout_in_seconds: int = 6000
    resource_monitor: ResourceMonitor = None
    min_cluster_count: int = 1
    max_cluster_count: int = 1
    scaling_policy: str = None
    comment: str = ""

    def _validate(self):
        if self.warehouse_size.lower() not in WAREHOUSE_SIZES:
            raise InvalidParamsException(
                f"{self.warehouse_size} is not a valid snowflake warehouse size. Options include: {WAREHOUSE_SIZES}"
            )
        if self.scaling_policy and self.scaling_policy.lower() not in SCALING_POLICIES:
            raise InvalidParamsException(
                f"{self.scaling_policy} is not a valid snowflake scaling policy. Options include: {SCALING_POLICIES}"
            )


@dataclass
class Role(AccountObject):
    comment: str = ""


@dataclass
class User(BaseSnowflakeObject):
    email: str = None
    password: str = None
    login_name: str = None
    display_name: str = None
    first_name: str = None
    middle_name: str = None
    last_name: str = None
    must_change_password: bool = True
    disabled: bool = False
    snowflake_support: bool = False
    days_to_expiry: int = None
    mins_to_unlock: int = None
    default_warehouse: Warehouse = None
    default_role: Role = None
    default_namespace: str = None
    # ext_authn_duo: bool = False # NOTE! CANNOT BE SET DIRECTLY
    # ext_authn_uid: str = None # # NOTE! CANNOT BE SET DIRECTLY
    min_to_bypass_mfa: int = None
    disable_mfa: bool = None
    rsa_public_key: str = None
    rsa_public_key_2: str = None
    abort_detached_query: bool = True
    autocommit: bool = False
    date_input_format: str = None
    date_output_format: str = None
    error_on_nondeterministic_merge: bool = None
    error_on_nondeterministic_update: bool = None
    lock_timeout: int = None
    query_tag: str = None
    rows_per_resultset: int = None
    statement_timeout_in_seconds: int = None
    timestamp_day_is_always_24h: bool = None
    timestamp_input_format: str = None
    timestamp_ltz_output_format: str = None
    timestamp_ntz_output_format: str = None
    timestamp_output_format: str = None
    timestamp_type_mapping: str = None
    timestamp_tz_output_format: str = None
    timezone: str = None
    time_input_format: str = None
    time_output_format: str = None
    transaction_default_isolation_level: str = None
    two_digit_century_start: int = None
    unsupported_ddl_action: str = None
    use_cached_result: bool = None
    comment: str = ""


@dataclass
class AzureNotificationIntegration(AccountObject):
    azure_storage_queue_primary_uri: str
    azure_tenant_id: str
    enabled: bool = True
    type: str = "queue"
    notification_provider: str = "azure_storage_queue"
    comment: str = ""

    @property
    def resource_type(self):
        return "notification integration"


@dataclass
class SecurityIntegrationOAuth(AccountObject):
    external_oauth_type: str
    external_oauth_issuer: str
    external_oauth_token_user_mapping_claim: str
    external_oauth_snowflake_user_mapping_attribute: str  # login_name or email
    enabled: bool = True
    external_oauth_jws_keys_url: str = None  # optional
    external_oauth_rsa_public_key: str = None  # optional pk1
    external_oauth_rsa_public_key_2: str = None  # optional pk2
    external_oauth_audience_list: str = None  # optional
    type: str = "external_oauth"

    def _validate(self):
        if self.external_oauth_type.lower() not in EXTERNAL_OAUTH_TYPES:
            raise InvalidParamsException(
                f"{self.external_oauth_type} is not a valid external oauth type. Options include: {EXTERNAL_OAUTH_TYPES}"
            )

    @property
    def resource_type(self):
        return "security integration"


@dataclass
class SecurityIntegrationOAuthPartnerApp(AccountObject):
    def __post_init__(self):
        raise NotImplementedError(
            "Snowflake Integration for OAuth Partner Apps not implemented. If you'd like to contribute this functionality, it would be wholly welcomed."
        )

    @property
    def resource_type(self):
        return "security integration"


@dataclass
class SecurityIntegrationOAuthCustom(AccountObject):
    def __post_init__(self):
        raise NotImplementedError(
            "Snowflake Integration for custom OAuth not implemented. If you'd like to contribute this functionality, it would be wholly welcomed."
        )

    @property
    def resource_type(self):
        return "security integration"


@dataclass
class SecurityIntegrationSAML2(AccountObject):
    saml2_issuer: str
    saml2_sso_url: str
    saml2_provider: str
    saml2_x509_cert: str
    enabled: bool = True
    saml2_sp_initiated_login_page_label: str = None
    saml2_enable_sp_initiated: str = None
    saml2_snowflake_x509_cert: str = None
    saml2_sign_request: str = None
    saml2_requested_nameid_format: str = None
    type: str = "saml2"

    @property
    def resource_type(self):
        return "security integration"


@dataclass
class SecurityIntegrationSCIM(AccountObject):
    scim_client: str  # okta, azure, or custom
    run_as_role: str  # okta_provisioner, aad_provisioner, generic_scim_provisioner
    network_policy: str = None
    type: str = "saml2"

    @property
    def resource_type(self):
        return "security integration"


@dataclass
class BaseStorageIntegration(AccountObject):

    storage_allowed_locations: List[str]  # required
    storage_blocked_locations: List[str] = field(default_factory=list)
    comment: str = ""
    enabled: bool = True
    type: str = "external_stage"

    @property
    def resource_type(self):
        return "storage integration"


@dataclass
class StorageIntegrationS3(BaseStorageIntegration):
    storage_aws_role_arn: str = ""  # defaulting this is a dirty hack to get around TypeError: non-default argument 'storage_aws_role_arn' follows default argument
    storage_provider: str = "s3"


@dataclass
class StorageIntegrationGCS(BaseStorageIntegration):
    storage_provider: str = "gcs"


@dataclass
class StorageIntegrationAzure(BaseStorageIntegration):
    azure_tenant_id: str = ""
    storage_provider: str = "azure"
