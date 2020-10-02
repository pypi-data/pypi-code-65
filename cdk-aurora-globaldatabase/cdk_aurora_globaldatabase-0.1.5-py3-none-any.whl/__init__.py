"""
[![NPM version](https://badge.fury.io/js/cdk-aurora-globaldatabase.svg)](https://badge.fury.io/js/cdk-aurora-globaldatabase)
[![PyPI version](https://badge.fury.io/py/cdk-aurora-globaldatabase.svg)](https://badge.fury.io/py/cdk-aurora-globaldatabase)
![Release](https://github.com/guan840912/cdk-aurora-globaldatabase/workflows/Release/badge.svg)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk-aurora-globaldatabase?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk-aurora-globaldatabase?label=pypi&color=blue)

# cdk-aurora-globaldatabase

`cdk-aurora-globaldatabase` is an AWS CDK construct library that allows you to create [Amazon Aurora Global Databases](https://aws.amazon.com/rds/aurora/global-database/) with AWS CDK in Typescript or Python.

# Why

**Amazon Aurora Global Databases** is designed for multi-regional Amazon Aurora Database clusters that span across different AWS regions. Due to the lack of native cloudformation support, it has been very challenging to build with cloudformation or AWS CDK with the upstream `aws-rds` construct.

`cdk-aurora-globaldatabase` aims to offload the heavy-lifting and helps you provision and deploy cross-regional **Amazon Aurora Global Databases** simply with just a few CDK statements.

## Now Try It !!!

# Sample for Mysql

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from ..index import GolbalAuroraRDSMaster, InstanceTypeEnum, GolbalAuroraRDSSlaveInfra
from aws_cdk.core import App, Stack, CfnOutput
import aws_cdk.aws_ec2 as ec2
# new app .
mock_app = App()

# setting two region env config .
env_singapro = {"account": process.env.CDK_DEFAULT_ACCOUNT, "region": "ap-southeast-1"}
env_tokyo = {"account": process.env.CDK_DEFAULT_ACCOUNT, "region": "ap-northeast-1"}

# create stack main .
stack_m = Stack(mock_app, "testing-stackM", env=env_tokyo)
vpc_public = ec2.Vpc(stack_m, "defaultVpc",
    nat_gateways=0,
    max_azs=3,
    subnet_configuration=[SubnetConfiguration(
        cidr_mask=26,
        name="masterVPC2",
        subnet_type=ec2.SubnetType.PUBLIC
    )]
)
globaldb_m = GolbalAuroraRDSMaster(stack_m, "golbalAuroraRDSMaster",
    instance_type=InstanceTypeEnum.R5_LARGE,
    vpc=vpc_public,
    rds_password="1qaz2wsx"
)
globaldb_m.rds_cluster.connections.allow_default_port_from(ec2.Peer.ipv4(f"{process.env.MYIP}/32"))

# create stack slave infra or you can give your subnet group.
stack_s = Stack(mock_app, "testing-stackS", env=env_singapro)
vpc_public2 = ec2.Vpc(stack_s, "defaultVpc2",
    nat_gateways=0,
    max_azs=3,
    subnet_configuration=[SubnetConfiguration(
        cidr_mask=26,
        name="secondVPC2",
        subnet_type=ec2.SubnetType.PUBLIC
    )]
)
globaldb_s = GolbalAuroraRDSSlaveInfra(stack_s, "slaveregion", vpc=vpc_public2, subnet_type=ec2.SubnetType.PUBLIC)

# so we need to wait stack slave created first .
stack_m.add_dependency(stack_s)

CfnOutput(stack_m, "password", value=globaldb_m.rds_password)
# add second region cluster
globaldb_m.add_regional_cluster(stack_m, "addregionalrds",
    region="ap-southeast-1",
    db_subnet_group_name=globaldb_s.db_subnet_group.db_subnet_group_name
)
```

# Sample for Postgres

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from ..index import GolbalAuroraRDSMaster, InstanceTypeEnum, GolbalAuroraRDSSlaveInfra
from aws_cdk.core import App, Stack, CfnOutput
import aws_cdk.aws_ec2 as ec2
import aws_cdk.aws_rds as _rds

mock_app = App()
env_singapro = {"account": process.env.CDK_DEFAULT_ACCOUNT, "region": "ap-southeast-1"}
env_tokyo = {"account": process.env.CDK_DEFAULT_ACCOUNT, "region": "ap-northeast-1"}

stack_m = Stack(mock_app, "testing-stackM", env=env_tokyo)
vpc_public = ec2.Vpc(stack_m, "defaultVpc",
    nat_gateways=0,
    max_azs=3,
    subnet_configuration=[SubnetConfiguration(
        cidr_mask=26,
        name="masterVPC2",
        subnet_type=ec2.SubnetType.PUBLIC
    )]
)

# Note if you use postgres , need to give the same value in engineVersion and  dbClusterpPG's engine .
globaldb_m = GolbalAuroraRDSMaster(stack_m, "golbalAuroraRDSMaster",
    instance_type=InstanceTypeEnum.R5_LARGE,
    vpc=vpc_public,
    rds_password="1qaz2wsx",
    engine_version=_rds.DatabaseClusterEngine.aurora_postgres(
        version=_rds.AuroraPostgresEngineVersion.VER_11_7
    ),
    db_clusterp_pG=_rds.ParameterGroup(stack_m, "dbClusterparametergroup",
        engine=_rds.DatabaseClusterEngine.aurora_postgres(
            version=_rds.AuroraPostgresEngineVersion.VER_11_7
        ),
        parameters={
            "rds.force_ssl": "1",
            "rds.log_retention_period": "10080",
            "auto_explain.log_min_duration": "5000",
            "auto_explain.log_verbose": "1",
            "timezone": "UTC+8",
            "shared_preload_libraries": "auto_explain,pg_stat_statements,pg_hint_plan,pgaudit",
            "log_connections": "1",
            "log_statement": "ddl",
            "log_disconnections": "1",
            "log_lock_waits": "1",
            "log_min_duration_statement": "5000",
            "log_rotation_age": "1440",
            "log_rotation_size": "102400",
            "random_page_cost": "1",
            "track_activity_query_size": "16384",
            "idle_in_transaction_session_timeout": "7200000"
        }
    )
)
globaldb_m.rds_cluster.connections.allow_default_port_from(ec2.Peer.ipv4(f"{process.env.MYIP}/32"))

stack_s = Stack(mock_app, "testing-stackS", env=env_singapro)
vpc_public2 = ec2.Vpc(stack_s, "defaultVpc2",
    nat_gateways=0,
    max_azs=3,
    subnet_configuration=[SubnetConfiguration(
        cidr_mask=26,
        name="secondVPC2",
        subnet_type=ec2.SubnetType.PUBLIC
    )]
)
globaldb_s = GolbalAuroraRDSSlaveInfra(stack_s, "slaveregion",
    vpc=vpc_public2, subnet_type=ec2.SubnetType.PUBLIC
)

stack_m.add_dependency(stack_s)

CfnOutput(stack_m, "password", value=globaldb_m.rds_password)
# add second region cluster
globaldb_m.add_regional_cluster(stack_m, "addregionalrds",
    region="ap-southeast-1",
    db_subnet_group_name=globaldb_s.db_subnet_group.db_subnet_group_name
)
```

### To deploy

```bash
cdk deploy
```

### To destroy

```bash
cdk destroy
```
"""
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.aws_ec2
import aws_cdk.aws_rds
import aws_cdk.core


class GolbalAuroraRDSMaster(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSMaster",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        db_clusterp_pg: typing.Optional[aws_cdk.aws_rds.IParameterGroup] = None,
        db_user_name: typing.Optional[builtins.str] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        instance_type: typing.Optional["InstanceTypeEnum"] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        rds_password: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        time_zone: typing.Optional["MySQLtimeZone"] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param db_clusterp_pg: RDS ParameterGroup. Default: - Aurora MySQL ParameterGroup
        :param db_user_name: RDS default Super User Name. Default: - sysadmin
        :param default_database_name: RDS default Database Name. Default: - globaldatabase
        :param deletion_protection: Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param engine_version: RDS Database Cluster Engine . Default: - rds.DatabaseClusterEngine.auroraMysql({version: rds.AuroraMysqlEngineVersion.VER_2_07_1,})
        :param instance_type: RDS Instance Type only can use r4 or r5 type see more https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html#aurora-global-database.limitations. Default: - r5.large
        :param parameters: RDS Parameters. Default: - {time_zone: 'UTC'}
        :param rds_password: return RDS Cluster password.
        :param storage_encrypted: Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param time_zone: RDS time zone. Default: - MySQLtimeZone.UTC
        :param vpc: RDS default VPC. Default: - new VPC
        """
        props = GolbalAuroraRDSMasterProps(
            db_clusterp_pg=db_clusterp_pg,
            db_user_name=db_user_name,
            default_database_name=default_database_name,
            deletion_protection=deletion_protection,
            engine_version=engine_version,
            instance_type=instance_type,
            parameters=parameters,
            rds_password=rds_password,
            storage_encrypted=storage_encrypted,
            time_zone=time_zone,
            vpc=vpc,
        )

        jsii.create(GolbalAuroraRDSMaster, self, [scope, id, props])

    @jsii.member(jsii_name="addRegionalCluster")
    def add_regional_cluster(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        region: builtins.str,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param region: 
        :param db_subnet_group_name: 
        """
        options = RegionalOptions(
            region=region, db_subnet_group_name=db_subnet_group_name
        )

        return jsii.invoke(self, "addRegionalCluster", [scope, id, options])

    @builtins.property # type: ignore
    @jsii.member(jsii_name="clusterEngineVersion")
    def cluster_engine_version(self) -> builtins.str:
        """return RDS Cluster DB Engine Version."""
        return jsii.get(self, "clusterEngineVersion")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="dbClusterpPG")
    def db_clusterp_pg(self) -> aws_cdk.aws_rds.IParameterGroup:
        """return RDS Cluster ParameterGroup."""
        return jsii.get(self, "dbClusterpPG")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="engine")
    def engine(self) -> builtins.str:
        """return RDS Cluster DB Engine ."""
        return jsii.get(self, "engine")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="engineVersion")
    def engine_version(self) -> aws_cdk.aws_rds.IClusterEngine:
        """return RDS Cluster DB Engine Version."""
        return jsii.get(self, "engineVersion")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="globalClusterArn")
    def global_cluster_arn(self) -> builtins.str:
        """return Global RDS Cluster Resource ARN ."""
        return jsii.get(self, "globalClusterArn")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="globalClusterIdentifier")
    def global_cluster_identifier(self) -> builtins.str:
        """return Global RDS Cluster Identifier ."""
        return jsii.get(self, "globalClusterIdentifier")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="rdsCluster")
    def rds_cluster(self) -> aws_cdk.aws_rds.DatabaseCluster:
        """return RDS Cluster."""
        return jsii.get(self, "rdsCluster")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="rdsClusterarn")
    def rds_clusterarn(self) -> builtins.str:
        """return RDS Cluster Resource ARN ."""
        return jsii.get(self, "rdsClusterarn")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="rdsInstanceType")
    def rds_instance_type(self) -> "InstanceTypeEnum":
        """return Global RDS Cluster instance Type ."""
        return jsii.get(self, "rdsInstanceType")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="rdsIsPublic")
    def rds_is_public(self) -> aws_cdk.aws_ec2.SubnetType:
        """return RDS Cluster is Public ?"""
        return jsii.get(self, "rdsIsPublic")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="rdsPassword")
    def rds_password(self) -> typing.Optional[builtins.str]:
        """return RDS Cluster password.

        if not define props.rdsPassword , password will stored in Secret Manager
        Please use this command get password back , "aws secretsmanager get-secret-value --secret-id secret name"
        """
        return jsii.get(self, "rdsPassword")


@jsii.data_type(
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSMasterProps",
    jsii_struct_bases=[],
    name_mapping={
        "db_clusterp_pg": "dbClusterpPG",
        "db_user_name": "dbUserName",
        "default_database_name": "defaultDatabaseName",
        "deletion_protection": "deletionProtection",
        "engine_version": "engineVersion",
        "instance_type": "instanceType",
        "parameters": "parameters",
        "rds_password": "rdsPassword",
        "storage_encrypted": "storageEncrypted",
        "time_zone": "timeZone",
        "vpc": "vpc",
    },
)
class GolbalAuroraRDSMasterProps:
    def __init__(
        self,
        *,
        db_clusterp_pg: typing.Optional[aws_cdk.aws_rds.IParameterGroup] = None,
        db_user_name: typing.Optional[builtins.str] = None,
        default_database_name: typing.Optional[builtins.str] = None,
        deletion_protection: typing.Optional[builtins.bool] = None,
        engine_version: typing.Optional[aws_cdk.aws_rds.IClusterEngine] = None,
        instance_type: typing.Optional["InstanceTypeEnum"] = None,
        parameters: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        rds_password: typing.Optional[builtins.str] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        time_zone: typing.Optional["MySQLtimeZone"] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        """
        :param db_clusterp_pg: RDS ParameterGroup. Default: - Aurora MySQL ParameterGroup
        :param db_user_name: RDS default Super User Name. Default: - sysadmin
        :param default_database_name: RDS default Database Name. Default: - globaldatabase
        :param deletion_protection: Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param engine_version: RDS Database Cluster Engine . Default: - rds.DatabaseClusterEngine.auroraMysql({version: rds.AuroraMysqlEngineVersion.VER_2_07_1,})
        :param instance_type: RDS Instance Type only can use r4 or r5 type see more https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html#aurora-global-database.limitations. Default: - r5.large
        :param parameters: RDS Parameters. Default: - {time_zone: 'UTC'}
        :param rds_password: return RDS Cluster password.
        :param storage_encrypted: Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param time_zone: RDS time zone. Default: - MySQLtimeZone.UTC
        :param vpc: RDS default VPC. Default: - new VPC
        """
        self._values: typing.Dict[str, typing.Any] = {}
        if db_clusterp_pg is not None:
            self._values["db_clusterp_pg"] = db_clusterp_pg
        if db_user_name is not None:
            self._values["db_user_name"] = db_user_name
        if default_database_name is not None:
            self._values["default_database_name"] = default_database_name
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if engine_version is not None:
            self._values["engine_version"] = engine_version
        if instance_type is not None:
            self._values["instance_type"] = instance_type
        if parameters is not None:
            self._values["parameters"] = parameters
        if rds_password is not None:
            self._values["rds_password"] = rds_password
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if time_zone is not None:
            self._values["time_zone"] = time_zone
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def db_clusterp_pg(self) -> typing.Optional[aws_cdk.aws_rds.IParameterGroup]:
        """RDS ParameterGroup.

        :default: - Aurora MySQL ParameterGroup
        """
        result = self._values.get("db_clusterp_pg")
        return result

    @builtins.property
    def db_user_name(self) -> typing.Optional[builtins.str]:
        """RDS default Super User Name.

        :default: - sysadmin
        """
        result = self._values.get("db_user_name")
        return result

    @builtins.property
    def default_database_name(self) -> typing.Optional[builtins.str]:
        """RDS default Database Name.

        :default: - globaldatabase
        """
        result = self._values.get("default_database_name")
        return result

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        """Global RDS Database Cluster Engine Deletion Protection Option .

        :default: - false
        """
        result = self._values.get("deletion_protection")
        return result

    @builtins.property
    def engine_version(self) -> typing.Optional[aws_cdk.aws_rds.IClusterEngine]:
        """RDS Database Cluster Engine .

        :default: - rds.DatabaseClusterEngine.auroraMysql({version: rds.AuroraMysqlEngineVersion.VER_2_07_1,})
        """
        result = self._values.get("engine_version")
        return result

    @builtins.property
    def instance_type(self) -> typing.Optional["InstanceTypeEnum"]:
        """RDS Instance Type only can use r4 or r5 type  see more https://docs.aws.amazon.com/AmazonRDS/latest/AuroraUserGuide/aurora-global-database.html#aurora-global-database.limitations.

        :default: - r5.large
        """
        result = self._values.get("instance_type")
        return result

    @builtins.property
    def parameters(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        """RDS Parameters.

        :default: - {time_zone: 'UTC'}
        """
        result = self._values.get("parameters")
        return result

    @builtins.property
    def rds_password(self) -> typing.Optional[builtins.str]:
        """return RDS Cluster password."""
        result = self._values.get("rds_password")
        return result

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        """Global RDS Database Cluster Engine Storage Encrypted Option .

        :default: - true
        """
        result = self._values.get("storage_encrypted")
        return result

    @builtins.property
    def time_zone(self) -> typing.Optional["MySQLtimeZone"]:
        """RDS time zone.

        :default: - MySQLtimeZone.UTC
        """
        result = self._values.get("time_zone")
        return result

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        """RDS default VPC.

        :default: - new VPC
        """
        result = self._values.get("vpc")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GolbalAuroraRDSMasterProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class GolbalAuroraRDSSlaveInfra(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSSlaveInfra",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        deletion_protection: typing.Optional[builtins.bool] = None,
        stack: typing.Optional[aws_cdk.core.Stack] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param deletion_protection: Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param stack: RDS Stack.
        :param storage_encrypted: Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param subnet_type: Slave region.
        :param vpc: Slave region VPC. Default: - new VPC
        """
        props = GolbalAuroraRDSSlaveInfraProps(
            deletion_protection=deletion_protection,
            stack=stack,
            storage_encrypted=storage_encrypted,
            subnet_type=subnet_type,
            vpc=vpc,
        )

        jsii.create(GolbalAuroraRDSSlaveInfra, self, [scope, id, props])

    @builtins.property # type: ignore
    @jsii.member(jsii_name="dbSubnetGroup")
    def db_subnet_group(self) -> aws_cdk.aws_rds.CfnDBSubnetGroup:
        """GolbalAuroraRDSSlaveInfra subnet group .

        :default: - true
        """
        return jsii.get(self, "dbSubnetGroup")


@jsii.data_type(
    jsii_type="cdk-aurora-globaldatabase.GolbalAuroraRDSSlaveInfraProps",
    jsii_struct_bases=[],
    name_mapping={
        "deletion_protection": "deletionProtection",
        "stack": "stack",
        "storage_encrypted": "storageEncrypted",
        "subnet_type": "subnetType",
        "vpc": "vpc",
    },
)
class GolbalAuroraRDSSlaveInfraProps:
    def __init__(
        self,
        *,
        deletion_protection: typing.Optional[builtins.bool] = None,
        stack: typing.Optional[aws_cdk.core.Stack] = None,
        storage_encrypted: typing.Optional[builtins.bool] = None,
        subnet_type: typing.Optional[aws_cdk.aws_ec2.SubnetType] = None,
        vpc: typing.Optional[aws_cdk.aws_ec2.IVpc] = None,
    ) -> None:
        """
        :param deletion_protection: Global RDS Database Cluster Engine Deletion Protection Option . Default: - false
        :param stack: RDS Stack.
        :param storage_encrypted: Global RDS Database Cluster Engine Storage Encrypted Option . Default: - true
        :param subnet_type: Slave region.
        :param vpc: Slave region VPC. Default: - new VPC
        """
        self._values: typing.Dict[str, typing.Any] = {}
        if deletion_protection is not None:
            self._values["deletion_protection"] = deletion_protection
        if stack is not None:
            self._values["stack"] = stack
        if storage_encrypted is not None:
            self._values["storage_encrypted"] = storage_encrypted
        if subnet_type is not None:
            self._values["subnet_type"] = subnet_type
        if vpc is not None:
            self._values["vpc"] = vpc

    @builtins.property
    def deletion_protection(self) -> typing.Optional[builtins.bool]:
        """Global RDS Database Cluster Engine Deletion Protection Option .

        :default: - false
        """
        result = self._values.get("deletion_protection")
        return result

    @builtins.property
    def stack(self) -> typing.Optional[aws_cdk.core.Stack]:
        """RDS Stack."""
        result = self._values.get("stack")
        return result

    @builtins.property
    def storage_encrypted(self) -> typing.Optional[builtins.bool]:
        """Global RDS Database Cluster Engine Storage Encrypted Option .

        :default: - true
        """
        result = self._values.get("storage_encrypted")
        return result

    @builtins.property
    def subnet_type(self) -> typing.Optional[aws_cdk.aws_ec2.SubnetType]:
        """Slave region."""
        result = self._values.get("subnet_type")
        return result

    @builtins.property
    def vpc(self) -> typing.Optional[aws_cdk.aws_ec2.IVpc]:
        """Slave region VPC.

        :default: - new VPC
        """
        result = self._values.get("vpc")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "GolbalAuroraRDSSlaveInfraProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="cdk-aurora-globaldatabase.InstanceTypeEnum")
class InstanceTypeEnum(enum.Enum):
    R4_LARGE = "R4_LARGE"
    """db Instance Type r4.large."""
    R4_XLARGE = "R4_XLARGE"
    """db Instance Type r4.xlarge."""
    R4_2XLARGE = "R4_2XLARGE"
    """db Instance Type r4.2xlarge."""
    R4_4XLARGE = "R4_4XLARGE"
    """db Instance Type r4.4xlarge."""
    R4_8XLARGE = "R4_8XLARGE"
    """db Instance Type r4.8xlarge."""
    R4_16XLARGE = "R4_16XLARGE"
    """db Instance Type r4.16xlarge."""
    R5_LARGE = "R5_LARGE"
    """db Instance Type r5.large."""
    R5_XLARGE = "R5_XLARGE"
    """db Instance Type r5.xlarge."""
    R5_2XLARGE = "R5_2XLARGE"
    """db Instance Type r5.2xlarge."""
    R5_4XLARGE = "R5_4XLARGE"
    """db Instance Type r5.4xlarge."""
    R5_8XLARGE = "R5_8XLARGE"
    """db Instance Type r5.8xlarge."""
    R5_12XLARGE = "R5_12XLARGE"
    """db Instance Type r5.12xlarge."""
    R5_16XLARGE = "R5_16XLARGE"
    """db Instance Type r5.16xlarge."""
    R5_24XLARGE = "R5_24XLARGE"
    """db Instance Type r5.24xlarge."""


@jsii.enum(jsii_type="cdk-aurora-globaldatabase.MySQLtimeZone")
class MySQLtimeZone(enum.Enum):
    UTC = "UTC"
    """TIME ZONE UTC."""
    ASIA_TAIPEI = "ASIA_TAIPEI"
    """TIME ZONE Asia/Taipei."""
    AFRICA_CAIRO = "AFRICA_CAIRO"
    """TIME ZONE Africa/Cairo."""
    ASIA_BANGKOK = "ASIA_BANGKOK"
    """TIME ZONE Asia/Bangkok."""
    AUSTRALIA_DARWIN = "AUSTRALIA_DARWIN"
    """TIME ZONE Australia/Darwin."""
    AFRICA_CASABLANCA = "AFRICA_CASABLANCA"
    """TIME ZONE Africa/Casablanca."""
    ASIA_BEIRUT = "ASIA_BEIRUT"
    """TIME ZONE Asia/Beirut."""
    AUSTRALIA_HOBART = "AUSTRALIA_HOBART"
    """TIME ZONE Australia/Hobart."""
    AFRICA_HARARE = "AFRICA_HARARE"
    """TIME ZONE Africa/Harare."""
    ASIA_CALCUTTA = "ASIA_CALCUTTA"
    """TIME ZONE Asia/Calcutta."""
    AUSTRALIA_PERTH = "AUSTRALIA_PERTH"
    """TIME ZONE Australia/Perth."""
    AFRICA_MONROVIA = "AFRICA_MONROVIA"
    """TIME ZONE Africa/Monrovia."""
    ASIA_DAMASCUS = "ASIA_DAMASCUS"
    """TIME ZONE Asia/Damascus."""
    AUSTRALIA_SYDNEY = "AUSTRALIA_SYDNEY"
    """TIME ZONE Australia/Sydney."""
    AFRICA_NAIROBI = "AFRICA_NAIROBI"
    """TIME ZONE Africa/Nairobi."""
    ASIA_DHAKA = "ASIA_DHAKA"
    """TIME ZONE Asia/Dhaka."""
    BRAZIL_EAST = "BRAZIL_EAST"
    """TIME ZONE Brazil/East."""
    AFRICA_TRIPOLI = "AFRICA_TRIPOLI"
    """TIME ZONE Africa/Tripoli."""
    ASIA_IRKUTSK = "ASIA_IRKUTSK"
    """TIME ZONE Asia/Irkutsk."""
    CANADA_NEWFOUNDLAND = "CANADA_NEWFOUNDLAND"
    """TIME ZONE Canada/Newfoundland."""
    AFRICA_WINDHOEK = "AFRICA_WINDHOEK"
    """TIME ZONE Africa/Windhoek."""
    ASIA_JERUSALEM = "ASIA_JERUSALEM"
    """TIME ZONE Asia/Jerusalem."""
    CANADA_SASKATCHEWAN = "CANADA_SASKATCHEWAN"
    """TIME ZONE Canada/Saskatchewan."""
    AMERICA_ARAGUAINA = "AMERICA_ARAGUAINA"
    """TIME ZONE America/Araguaina."""
    ASIA_KABUL = "ASIA_KABUL"
    """TIME ZONE Asia/Kabul."""
    EUROPE_AMSTERDAM = "EUROPE_AMSTERDAM"
    """TIME ZONE Europe/Amsterdam."""
    AMERICA_ASUNCION = "AMERICA_ASUNCION"
    """TIME ZONE America/Asuncion."""
    ASIA_KARACHI = "ASIA_KARACHI"
    """TIME ZONE Asia/Karachi."""
    EUROPE_ATHENS = "EUROPE_ATHENS"
    """TIME ZONE Europe/Athens."""
    AMERICA_BOGOTA = "AMERICA_BOGOTA"
    """TIME ZONE America/Bogota."""
    ASIA_KATHMANDU = "ASIA_KATHMANDU"
    """TIME ZONE Asia/Kathmandu."""
    EUROPE_DUBLIN = "EUROPE_DUBLIN"
    """TIME ZONE Europe/Dublin."""
    AMERICA_CARACAS = "AMERICA_CARACAS"
    """TIME ZONE America/Caracas."""
    ASIA_KRASNOYARSK = "ASIA_KRASNOYARSK"
    """TIME ZONE Asia/Krasnoyarsk."""
    EUROPE_HELSINKI = "EUROPE_HELSINKI"
    """TIME ZONE Europe/Helsinki."""
    AMERICA_CHIHUAHUA = "AMERICA_CHIHUAHUA"
    """TIME ZONE America/Chihuahua."""
    ASIA_MAGADAN = "ASIA_MAGADAN"
    """TIME ZONE Asia/Magadan."""
    EUROPE_ISTANBUL = "EUROPE_ISTANBUL"
    """TIME ZONE Europe/Istanbul."""
    AMERICA_CUIABA = "AMERICA_CUIABA"
    """TIME ZONE America/Cuiaba."""
    ASIA_MUSCAT = "ASIA_MUSCAT"
    """TIME ZONE Asia/Muscat."""
    EUROPE_KALININGRAD = "EUROPE_KALININGRAD"
    """TIME ZONE Europe/Kaliningrad."""
    AMERICA_DENVER = "AMERICA_DENVER"
    """TIME ZONE America/Denver."""
    ASIA_NOVOSIBIRSK = "ASIA_NOVOSIBIRSK"
    """TIME ZONE Asia/Novosibirsk."""
    EUROPE_MOSCOW = "EUROPE_MOSCOW"
    """TIME ZONE Europe/Moscow'."""
    AMERICA_FORTALEZA = "AMERICA_FORTALEZA"
    """TIME ZONE America/Fortaleza."""
    ASIA_RIYADH = "ASIA_RIYADH"
    """TIME ZONE Asia/Riyadh."""
    EUROPE_PARIS = "EUROPE_PARIS"
    """TIME ZONE Europe/Paris."""
    AMERICA_GUATEMALA = "AMERICA_GUATEMALA"
    """TIME ZONE America/Guatemala."""
    ASIA_SEOUL = "ASIA_SEOUL"
    """TIME ZONE Asia/Seoul."""
    EUROPE_PRAGUE = "EUROPE_PRAGUE"
    """TIME ZONE Europe/Prague."""
    AMERICA_HALIFAX = "AMERICA_HALIFAX"
    """TIME ZONE America/Halifax."""
    ASIA_SHANGHAI = "ASIA_SHANGHAI"
    """TIME ZONE Asia/Shanghai."""
    EUROPE_SARAJEVO = "EUROPE_SARAJEVO"
    """TIME ZONE Europe/Sarajevo."""
    AMERICA_MANAUS = "AMERICA_MANAUS"
    """TIME ZONE America/Manaus."""
    ASIA_SINGAPORE = "ASIA_SINGAPORE"
    """TIME ZONE Asia/Singapore."""
    PACIFIC_AUCKLAND = "PACIFIC_AUCKLAND"
    """TIME ZONE Pacific/Auckland."""
    AMERICA_MATAMOROS = "AMERICA_MATAMOROS"
    """TIME ZONE America/Matamoros."""
    PACIFIC_FIJI = "PACIFIC_FIJI"
    """TIME ZONE Pacific/Fiji."""
    AMERICA_MONTERREY = "AMERICA_MONTERREY"
    """TIME ZONE America/Monterrey."""
    ASIA_TEHRAN = "ASIA_TEHRAN"
    """TIME ZONE Asia/Tehran."""
    PACIFIC_GUAM = "PACIFIC_GUAM"
    """TIME ZONE Pacific/Guam."""
    AMERICA_MONTEVIDEO = "AMERICA_MONTEVIDEO"
    """TIME ZONE America/Montevideo."""
    ASIA_TOKYO = "ASIA_TOKYO"
    """TIME ZONE Asia/Tokyo."""
    PACIFIC_HONOLULU = "PACIFIC_HONOLULU"
    """TIME ZONE Pacific/Honolulu."""
    AMERICA_PHOENIX = "AMERICA_PHOENIX"
    """TIME ZONE America/Phoenix."""
    ASIA_ULAANBAATAR = "ASIA_ULAANBAATAR"
    """TIME ZONE Asia/Ulaanbaatar."""
    PACIFIC_SAMOA = "PACIFIC_SAMOA"
    """TIME ZONE Pacific/Samoa."""
    AMERICA_SANTIAGO = "AMERICA_SANTIAGO"
    """TIME ZONE America/Santiago."""
    ASIA_VLADIVOSTOK = "ASIA_VLADIVOSTOK"
    """TIME ZONE Asia/Vladivostok."""
    US_ALASKA = "US_ALASKA"
    """TIME ZONE US/Alaska."""
    AMERICA_TIJUANA = "AMERICA_TIJUANA"
    """TIME ZONE America/Tijuana."""
    ASIA_YAKUTSK = "ASIA_YAKUTSK"
    """TIME ZONE Asia/Yakutsk."""
    US_CENTRAL = "US_CENTRAL"
    """TIME ZONE US/Central."""
    ASIA_AMMAN = "ASIA_AMMAN"
    """TIME ZONE Asia/Amman."""
    ASIA_YEREVAN = "ASIA_YEREVAN"
    """TIME ZONE Asia/Yerevan."""
    US_EASTERN = "US_EASTERN"
    """TIME ZONE US/Eastern."""
    ASIA_ASHGABAT = "ASIA_ASHGABAT"
    """TIME ZONE Asia/Ashgabat."""
    ATLANTIC_AZORES = "ATLANTIC_AZORES"
    """TIME ZONE Atlantic/Azores."""
    US_EAST_INDIANA = "US_EAST_INDIANA"
    """TIME ZONE US/East-Indiana."""
    ASIA_BAGHDAD = "ASIA_BAGHDAD"
    """TIME ZONE Asia/Baghdad."""
    AUSTRALIA_ADELAIDE = "AUSTRALIA_ADELAIDE"
    """TIME ZONE Australia/Adelaide."""
    US_PACIFIC = "US_PACIFIC"
    """TIME ZONE US/Pacific."""
    ASIA_BAKU = "ASIA_BAKU"
    """TIME ZONE Asia/Baku."""
    AUSTRALIA_BRISBANE = "AUSTRALIA_BRISBANE"
    """TIME ZONE Australia/Brisbane."""


@jsii.data_type(
    jsii_type="cdk-aurora-globaldatabase.RegionalOptions",
    jsii_struct_bases=[],
    name_mapping={"region": "region", "db_subnet_group_name": "dbSubnetGroupName"},
)
class RegionalOptions:
    def __init__(
        self,
        *,
        region: builtins.str,
        db_subnet_group_name: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param region: 
        :param db_subnet_group_name: 
        """
        self._values: typing.Dict[str, typing.Any] = {
            "region": region,
        }
        if db_subnet_group_name is not None:
            self._values["db_subnet_group_name"] = db_subnet_group_name

    @builtins.property
    def region(self) -> builtins.str:
        result = self._values.get("region")
        assert result is not None, "Required property 'region' is missing"
        return result

    @builtins.property
    def db_subnet_group_name(self) -> typing.Optional[builtins.str]:
        result = self._values.get("db_subnet_group_name")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RegionalOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "GolbalAuroraRDSMaster",
    "GolbalAuroraRDSMasterProps",
    "GolbalAuroraRDSSlaveInfra",
    "GolbalAuroraRDSSlaveInfraProps",
    "InstanceTypeEnum",
    "MySQLtimeZone",
    "RegionalOptions",
]

publication.publish()
