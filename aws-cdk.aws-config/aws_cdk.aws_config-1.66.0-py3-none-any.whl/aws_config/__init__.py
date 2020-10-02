"""
## AWS Config Construct Library

<!--BEGIN STABILITY BANNER-->---


![cfn-resources: Stable](https://img.shields.io/badge/cfn--resources-stable-success.svg?style=for-the-badge)

> All classes with the `Cfn` prefix in this module ([CFN Resources](https://docs.aws.amazon.com/cdk/latest/guide/constructs.html#constructs_lib)) are always stable and safe to use.

![cdk-constructs: Developer Preview](https://img.shields.io/badge/cdk--constructs-developer--preview-informational.svg?style=for-the-badge)

> The APIs of higher level constructs in this module are in **developer preview** before they become stable. We will only make breaking changes to address unforeseen API issues. Therefore, these APIs are not subject to [Semantic Versioning](https://semver.org/), and breaking changes will be announced in release notes. This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

This module is part of the [AWS Cloud Development Kit](https://github.com/aws/aws-cdk) project.

Supported:

* Config rules

Not supported

* Configuration recorder
* Delivery channel
* Aggregation

### Initial Setup

Before using the constructs provided in this module, you need to setup
AWS Config in the region you plan on using it in. This setup includes:

* `ConfigurationRecorder`: Configure which resources will be recorded for config changes.
* `DeliveryChannel`: Configure where to store the recorded data.

Following are the guides to setup AWS Config:

* [Using the AWS Console](https://docs.aws.amazon.com/config/latest/developerguide/gs-console.html)
* [Using the AWS CLI](https://docs.aws.amazon.com/config/latest/developerguide/gs-cli.html)

### Rules

#### AWS managed rules

To set up a managed rule, define a `ManagedRule` and specify its identifier:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
ManagedRule(self, "AccessKeysRotated",
    identifier="ACCESS_KEYS_ROTATED"
)
```

Available identifiers and parameters are listed in the [List of AWS Config Managed Rules](https://docs.aws.amazon.com/config/latest/developerguide/managed-rules-by-aws-config.html).

Higher level constructs for managed rules are available, see [Managed Rules](https://github.com/aws/aws-cdk/blob/master/packages/%40aws-cdk/aws-config/lib/managed-rules.ts). Prefer to use those constructs when available (PRs welcome to add more of those).

#### Custom rules

To set up a custom rule, define a `CustomRule` and specify the Lambda Function to run and the trigger types:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
CustomRule(self, "CustomRule",
    lambda_function=my_fn,
    configuration_changes=True,
    periodic=True
)
```

#### Restricting the scope

By default rules are triggered by changes to all [resources](https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources). Use the `scopeToResource()`, `scopeToResources()` or `scopeToTag()` methods to restrict the scope of both managed and custom rules:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
ssh_rule = ManagedRule(self, "SSH",
    identifier="INCOMING_SSH_DISABLED"
)

# Restrict to a specific security group
rule.scope_to_resource("AWS::EC2::SecurityGroup", "sg-1234567890abcdefgh")

custom_rule = CustomRule(self, "CustomRule",
    lambda_function=my_fn,
    configuration_changes=True
)

# Restrict to a specific tag
custom_rule.scope_to_tag("Cost Center", "MyApp")
```

Only one type of scope restriction can be added to a rule (the last call to `scopeToXxx()` sets the scope).

#### Events

To define Amazon CloudWatch event rules, use the `onComplianceChange()` or `onReEvaluationStatus()` methods:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
rule = CloudFormationStackDriftDetectionCheck(self, "Drift")
rule.on_compliance_change("TopicEvent",
    target=targets.SnsTopic(topic)
)
```

#### Example

Creating custom and managed rules with scope restriction and events:

```python
# Example automatically generated. See https://github.com/aws/jsii/issues/826
# A custom rule that runs on configuration changes of EC2 instances
fn = lambda_.Function(self, "CustomFunction",
    code=lambda_.AssetCode.from_inline("exports.handler = (event) => console.log(event);"),
    handler="index.handler",
    runtime=lambda_.Runtime.NODEJS_10_X
)

custom_rule = config.CustomRule(self, "Custom",
    configuration_changes=True,
    lambda_function=fn
)

custom_rule.scope_to_resource("AWS::EC2::Instance")

# A rule to detect stacks drifts
drift_rule = config.CloudFormationStackDriftDetectionCheck(self, "Drift")

# Topic for compliance events
compliance_topic = sns.Topic(self, "ComplianceTopic")

# Send notification on compliance change
drift_rule.on_compliance_change("ComplianceChange",
    target=targets.SnsTopic(compliance_topic)
)
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

import aws_cdk.aws_events
import aws_cdk.aws_iam
import aws_cdk.aws_lambda
import aws_cdk.aws_sns
import aws_cdk.core
import constructs


@jsii.implements(aws_cdk.core.IInspectable)
class CfnAggregationAuthorization(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnAggregationAuthorization",
):
    """A CloudFormation ``AWS::Config::AggregationAuthorization``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html
    :cloudformationResource: AWS::Config::AggregationAuthorization
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        authorized_account_id: builtins.str,
        authorized_aws_region: builtins.str,
        tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        """Create a new ``AWS::Config::AggregationAuthorization``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param authorized_account_id: ``AWS::Config::AggregationAuthorization.AuthorizedAccountId``.
        :param authorized_aws_region: ``AWS::Config::AggregationAuthorization.AuthorizedAwsRegion``.
        :param tags: ``AWS::Config::AggregationAuthorization.Tags``.
        """
        props = CfnAggregationAuthorizationProps(
            authorized_account_id=authorized_account_id,
            authorized_aws_region=authorized_aws_region,
            tags=tags,
        )

        jsii.create(CfnAggregationAuthorization, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Config::AggregationAuthorization.Tags``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-tags
        """
        return jsii.get(self, "tags")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="authorizedAccountId")
    def authorized_account_id(self) -> builtins.str:
        """``AWS::Config::AggregationAuthorization.AuthorizedAccountId``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-authorizedaccountid
        """
        return jsii.get(self, "authorizedAccountId")

    @authorized_account_id.setter # type: ignore
    def authorized_account_id(self, value: builtins.str) -> None:
        jsii.set(self, "authorizedAccountId", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="authorizedAwsRegion")
    def authorized_aws_region(self) -> builtins.str:
        """``AWS::Config::AggregationAuthorization.AuthorizedAwsRegion``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-authorizedawsregion
        """
        return jsii.get(self, "authorizedAwsRegion")

    @authorized_aws_region.setter # type: ignore
    def authorized_aws_region(self, value: builtins.str) -> None:
        jsii.set(self, "authorizedAwsRegion", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnAggregationAuthorizationProps",
    jsii_struct_bases=[],
    name_mapping={
        "authorized_account_id": "authorizedAccountId",
        "authorized_aws_region": "authorizedAwsRegion",
        "tags": "tags",
    },
)
class CfnAggregationAuthorizationProps:
    def __init__(
        self,
        *,
        authorized_account_id: builtins.str,
        authorized_aws_region: builtins.str,
        tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::AggregationAuthorization``.

        :param authorized_account_id: ``AWS::Config::AggregationAuthorization.AuthorizedAccountId``.
        :param authorized_aws_region: ``AWS::Config::AggregationAuthorization.AuthorizedAwsRegion``.
        :param tags: ``AWS::Config::AggregationAuthorization.Tags``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "authorized_account_id": authorized_account_id,
            "authorized_aws_region": authorized_aws_region,
        }
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def authorized_account_id(self) -> builtins.str:
        """``AWS::Config::AggregationAuthorization.AuthorizedAccountId``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-authorizedaccountid
        """
        result = self._values.get("authorized_account_id")
        assert result is not None, "Required property 'authorized_account_id' is missing"
        return result

    @builtins.property
    def authorized_aws_region(self) -> builtins.str:
        """``AWS::Config::AggregationAuthorization.AuthorizedAwsRegion``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-authorizedawsregion
        """
        result = self._values.get("authorized_aws_region")
        assert result is not None, "Required property 'authorized_aws_region' is missing"
        return result

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Config::AggregationAuthorization.Tags``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-aggregationauthorization.html#cfn-config-aggregationauthorization-tags
        """
        result = self._values.get("tags")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnAggregationAuthorizationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnConfigRule(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnConfigRule",
):
    """A CloudFormation ``AWS::Config::ConfigRule``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html
    :cloudformationResource: AWS::Config::ConfigRule
    """

    def __init__(
        self,
        scope_: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        source: typing.Union["CfnConfigRule.SourceProperty", aws_cdk.core.IResolvable],
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Any = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        scope: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigRule.ScopeProperty"]] = None,
    ) -> None:
        """Create a new ``AWS::Config::ConfigRule``.

        :param scope_: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param source: ``AWS::Config::ConfigRule.Source``.
        :param config_rule_name: ``AWS::Config::ConfigRule.ConfigRuleName``.
        :param description: ``AWS::Config::ConfigRule.Description``.
        :param input_parameters: ``AWS::Config::ConfigRule.InputParameters``.
        :param maximum_execution_frequency: ``AWS::Config::ConfigRule.MaximumExecutionFrequency``.
        :param scope: ``AWS::Config::ConfigRule.Scope``.
        """
        props = CfnConfigRuleProps(
            source=source,
            config_rule_name=config_rule_name,
            description=description,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
            scope=scope,
        )

        jsii.create(CfnConfigRule, self, [scope_, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="attrArn")
    def attr_arn(self) -> builtins.str:
        """
        :cloudformationAttribute: Arn
        """
        return jsii.get(self, "attrArn")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="attrComplianceType")
    def attr_compliance_type(self) -> builtins.str:
        """
        :cloudformationAttribute: Compliance.Type
        """
        return jsii.get(self, "attrComplianceType")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="attrConfigRuleId")
    def attr_config_rule_id(self) -> builtins.str:
        """
        :cloudformationAttribute: ConfigRuleId
        """
        return jsii.get(self, "attrConfigRuleId")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="inputParameters")
    def input_parameters(self) -> typing.Any:
        """``AWS::Config::ConfigRule.InputParameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-inputparameters
        """
        return jsii.get(self, "inputParameters")

    @input_parameters.setter # type: ignore
    def input_parameters(self, value: typing.Any) -> None:
        jsii.set(self, "inputParameters", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="source")
    def source(
        self,
    ) -> typing.Union["CfnConfigRule.SourceProperty", aws_cdk.core.IResolvable]:
        """``AWS::Config::ConfigRule.Source``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-source
        """
        return jsii.get(self, "source")

    @source.setter # type: ignore
    def source(
        self,
        value: typing.Union["CfnConfigRule.SourceProperty", aws_cdk.core.IResolvable],
    ) -> None:
        jsii.set(self, "source", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigRule.ConfigRuleName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-configrulename
        """
        return jsii.get(self, "configRuleName")

    @config_rule_name.setter # type: ignore
    def config_rule_name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "configRuleName", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="description")
    def description(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigRule.Description``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-description
        """
        return jsii.get(self, "description")

    @description.setter # type: ignore
    def description(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "description", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="maximumExecutionFrequency")
    def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigRule.MaximumExecutionFrequency``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-maximumexecutionfrequency
        """
        return jsii.get(self, "maximumExecutionFrequency")

    @maximum_execution_frequency.setter # type: ignore
    def maximum_execution_frequency(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "maximumExecutionFrequency", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="scope")
    def scope(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigRule.ScopeProperty"]]:
        """``AWS::Config::ConfigRule.Scope``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-scope
        """
        return jsii.get(self, "scope")

    @scope.setter # type: ignore
    def scope(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigRule.ScopeProperty"]],
    ) -> None:
        jsii.set(self, "scope", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnConfigRule.ScopeProperty",
        jsii_struct_bases=[],
        name_mapping={
            "compliance_resource_id": "complianceResourceId",
            "compliance_resource_types": "complianceResourceTypes",
            "tag_key": "tagKey",
            "tag_value": "tagValue",
        },
    )
    class ScopeProperty:
        def __init__(
            self,
            *,
            compliance_resource_id: typing.Optional[builtins.str] = None,
            compliance_resource_types: typing.Optional[typing.List[builtins.str]] = None,
            tag_key: typing.Optional[builtins.str] = None,
            tag_value: typing.Optional[builtins.str] = None,
        ) -> None:
            """
            :param compliance_resource_id: ``CfnConfigRule.ScopeProperty.ComplianceResourceId``.
            :param compliance_resource_types: ``CfnConfigRule.ScopeProperty.ComplianceResourceTypes``.
            :param tag_key: ``CfnConfigRule.ScopeProperty.TagKey``.
            :param tag_value: ``CfnConfigRule.ScopeProperty.TagValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if compliance_resource_id is not None:
                self._values["compliance_resource_id"] = compliance_resource_id
            if compliance_resource_types is not None:
                self._values["compliance_resource_types"] = compliance_resource_types
            if tag_key is not None:
                self._values["tag_key"] = tag_key
            if tag_value is not None:
                self._values["tag_value"] = tag_value

        @builtins.property
        def compliance_resource_id(self) -> typing.Optional[builtins.str]:
            """``CfnConfigRule.ScopeProperty.ComplianceResourceId``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-complianceresourceid
            """
            result = self._values.get("compliance_resource_id")
            return result

        @builtins.property
        def compliance_resource_types(
            self,
        ) -> typing.Optional[typing.List[builtins.str]]:
            """``CfnConfigRule.ScopeProperty.ComplianceResourceTypes``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-complianceresourcetypes
            """
            result = self._values.get("compliance_resource_types")
            return result

        @builtins.property
        def tag_key(self) -> typing.Optional[builtins.str]:
            """``CfnConfigRule.ScopeProperty.TagKey``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-tagkey
            """
            result = self._values.get("tag_key")
            return result

        @builtins.property
        def tag_value(self) -> typing.Optional[builtins.str]:
            """``CfnConfigRule.ScopeProperty.TagValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-scope.html#cfn-config-configrule-scope-tagvalue
            """
            result = self._values.get("tag_value")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ScopeProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnConfigRule.SourceDetailProperty",
        jsii_struct_bases=[],
        name_mapping={
            "event_source": "eventSource",
            "message_type": "messageType",
            "maximum_execution_frequency": "maximumExecutionFrequency",
        },
    )
    class SourceDetailProperty:
        def __init__(
            self,
            *,
            event_source: builtins.str,
            message_type: builtins.str,
            maximum_execution_frequency: typing.Optional[builtins.str] = None,
        ) -> None:
            """
            :param event_source: ``CfnConfigRule.SourceDetailProperty.EventSource``.
            :param message_type: ``CfnConfigRule.SourceDetailProperty.MessageType``.
            :param maximum_execution_frequency: ``CfnConfigRule.SourceDetailProperty.MaximumExecutionFrequency``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "event_source": event_source,
                "message_type": message_type,
            }
            if maximum_execution_frequency is not None:
                self._values["maximum_execution_frequency"] = maximum_execution_frequency

        @builtins.property
        def event_source(self) -> builtins.str:
            """``CfnConfigRule.SourceDetailProperty.EventSource``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html#cfn-config-configrule-source-sourcedetail-eventsource
            """
            result = self._values.get("event_source")
            assert result is not None, "Required property 'event_source' is missing"
            return result

        @builtins.property
        def message_type(self) -> builtins.str:
            """``CfnConfigRule.SourceDetailProperty.MessageType``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html#cfn-config-configrule-source-sourcedetail-messagetype
            """
            result = self._values.get("message_type")
            assert result is not None, "Required property 'message_type' is missing"
            return result

        @builtins.property
        def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
            """``CfnConfigRule.SourceDetailProperty.MaximumExecutionFrequency``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source-sourcedetails.html#cfn-config-configrule-sourcedetail-maximumexecutionfrequency
            """
            result = self._values.get("maximum_execution_frequency")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SourceDetailProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnConfigRule.SourceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "owner": "owner",
            "source_identifier": "sourceIdentifier",
            "source_details": "sourceDetails",
        },
    )
    class SourceProperty:
        def __init__(
            self,
            *,
            owner: builtins.str,
            source_identifier: builtins.str,
            source_details: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigRule.SourceDetailProperty"]]]] = None,
        ) -> None:
            """
            :param owner: ``CfnConfigRule.SourceProperty.Owner``.
            :param source_identifier: ``CfnConfigRule.SourceProperty.SourceIdentifier``.
            :param source_details: ``CfnConfigRule.SourceProperty.SourceDetails``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "owner": owner,
                "source_identifier": source_identifier,
            }
            if source_details is not None:
                self._values["source_details"] = source_details

        @builtins.property
        def owner(self) -> builtins.str:
            """``CfnConfigRule.SourceProperty.Owner``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html#cfn-config-configrule-source-owner
            """
            result = self._values.get("owner")
            assert result is not None, "Required property 'owner' is missing"
            return result

        @builtins.property
        def source_identifier(self) -> builtins.str:
            """``CfnConfigRule.SourceProperty.SourceIdentifier``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html#cfn-config-configrule-source-sourceidentifier
            """
            result = self._values.get("source_identifier")
            assert result is not None, "Required property 'source_identifier' is missing"
            return result

        @builtins.property
        def source_details(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigRule.SourceDetailProperty"]]]]:
            """``CfnConfigRule.SourceProperty.SourceDetails``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configrule-source.html#cfn-config-configrule-source-sourcedetails
            """
            result = self._values.get("source_details")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SourceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnConfigRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "source": "source",
        "config_rule_name": "configRuleName",
        "description": "description",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "scope": "scope",
    },
)
class CfnConfigRuleProps:
    def __init__(
        self,
        *,
        source: typing.Union[CfnConfigRule.SourceProperty, aws_cdk.core.IResolvable],
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Any = None,
        maximum_execution_frequency: typing.Optional[builtins.str] = None,
        scope: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnConfigRule.ScopeProperty]] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::ConfigRule``.

        :param source: ``AWS::Config::ConfigRule.Source``.
        :param config_rule_name: ``AWS::Config::ConfigRule.ConfigRuleName``.
        :param description: ``AWS::Config::ConfigRule.Description``.
        :param input_parameters: ``AWS::Config::ConfigRule.InputParameters``.
        :param maximum_execution_frequency: ``AWS::Config::ConfigRule.MaximumExecutionFrequency``.
        :param scope: ``AWS::Config::ConfigRule.Scope``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "source": source,
        }
        if config_rule_name is not None:
            self._values["config_rule_name"] = config_rule_name
        if description is not None:
            self._values["description"] = description
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if scope is not None:
            self._values["scope"] = scope

    @builtins.property
    def source(
        self,
    ) -> typing.Union[CfnConfigRule.SourceProperty, aws_cdk.core.IResolvable]:
        """``AWS::Config::ConfigRule.Source``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-source
        """
        result = self._values.get("source")
        assert result is not None, "Required property 'source' is missing"
        return result

    @builtins.property
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigRule.ConfigRuleName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-configrulename
        """
        result = self._values.get("config_rule_name")
        return result

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigRule.Description``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-description
        """
        result = self._values.get("description")
        return result

    @builtins.property
    def input_parameters(self) -> typing.Any:
        """``AWS::Config::ConfigRule.InputParameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-inputparameters
        """
        result = self._values.get("input_parameters")
        return result

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigRule.MaximumExecutionFrequency``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-maximumexecutionfrequency
        """
        result = self._values.get("maximum_execution_frequency")
        return result

    @builtins.property
    def scope(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnConfigRule.ScopeProperty]]:
        """``AWS::Config::ConfigRule.Scope``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configrule.html#cfn-config-configrule-scope
        """
        result = self._values.get("scope")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnConfigRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnConfigurationAggregator(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregator",
):
    """A CloudFormation ``AWS::Config::ConfigurationAggregator``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html
    :cloudformationResource: AWS::Config::ConfigurationAggregator
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        configuration_aggregator_name: builtins.str,
        account_aggregation_sources: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAggregator.AccountAggregationSourceProperty"]]]] = None,
        organization_aggregation_source: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAggregator.OrganizationAggregationSourceProperty"]] = None,
        tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        """Create a new ``AWS::Config::ConfigurationAggregator``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param configuration_aggregator_name: ``AWS::Config::ConfigurationAggregator.ConfigurationAggregatorName``.
        :param account_aggregation_sources: ``AWS::Config::ConfigurationAggregator.AccountAggregationSources``.
        :param organization_aggregation_source: ``AWS::Config::ConfigurationAggregator.OrganizationAggregationSource``.
        :param tags: ``AWS::Config::ConfigurationAggregator.Tags``.
        """
        props = CfnConfigurationAggregatorProps(
            configuration_aggregator_name=configuration_aggregator_name,
            account_aggregation_sources=account_aggregation_sources,
            organization_aggregation_source=organization_aggregation_source,
            tags=tags,
        )

        jsii.create(CfnConfigurationAggregator, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="tags")
    def tags(self) -> aws_cdk.core.TagManager:
        """``AWS::Config::ConfigurationAggregator.Tags``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-tags
        """
        return jsii.get(self, "tags")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configurationAggregatorName")
    def configuration_aggregator_name(self) -> builtins.str:
        """``AWS::Config::ConfigurationAggregator.ConfigurationAggregatorName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-configurationaggregatorname
        """
        return jsii.get(self, "configurationAggregatorName")

    @configuration_aggregator_name.setter # type: ignore
    def configuration_aggregator_name(self, value: builtins.str) -> None:
        jsii.set(self, "configurationAggregatorName", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="accountAggregationSources")
    def account_aggregation_sources(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAggregator.AccountAggregationSourceProperty"]]]]:
        """``AWS::Config::ConfigurationAggregator.AccountAggregationSources``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-accountaggregationsources
        """
        return jsii.get(self, "accountAggregationSources")

    @account_aggregation_sources.setter # type: ignore
    def account_aggregation_sources(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAggregator.AccountAggregationSourceProperty"]]]],
    ) -> None:
        jsii.set(self, "accountAggregationSources", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="organizationAggregationSource")
    def organization_aggregation_source(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAggregator.OrganizationAggregationSourceProperty"]]:
        """``AWS::Config::ConfigurationAggregator.OrganizationAggregationSource``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-organizationaggregationsource
        """
        return jsii.get(self, "organizationAggregationSource")

    @organization_aggregation_source.setter # type: ignore
    def organization_aggregation_source(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationAggregator.OrganizationAggregationSourceProperty"]],
    ) -> None:
        jsii.set(self, "organizationAggregationSource", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregator.AccountAggregationSourceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "account_ids": "accountIds",
            "all_aws_regions": "allAwsRegions",
            "aws_regions": "awsRegions",
        },
    )
    class AccountAggregationSourceProperty:
        def __init__(
            self,
            *,
            account_ids: typing.List[builtins.str],
            all_aws_regions: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            aws_regions: typing.Optional[typing.List[builtins.str]] = None,
        ) -> None:
            """
            :param account_ids: ``CfnConfigurationAggregator.AccountAggregationSourceProperty.AccountIds``.
            :param all_aws_regions: ``CfnConfigurationAggregator.AccountAggregationSourceProperty.AllAwsRegions``.
            :param aws_regions: ``CfnConfigurationAggregator.AccountAggregationSourceProperty.AwsRegions``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "account_ids": account_ids,
            }
            if all_aws_regions is not None:
                self._values["all_aws_regions"] = all_aws_regions
            if aws_regions is not None:
                self._values["aws_regions"] = aws_regions

        @builtins.property
        def account_ids(self) -> typing.List[builtins.str]:
            """``CfnConfigurationAggregator.AccountAggregationSourceProperty.AccountIds``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html#cfn-config-configurationaggregator-accountaggregationsource-accountids
            """
            result = self._values.get("account_ids")
            assert result is not None, "Required property 'account_ids' is missing"
            return result

        @builtins.property
        def all_aws_regions(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            """``CfnConfigurationAggregator.AccountAggregationSourceProperty.AllAwsRegions``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html#cfn-config-configurationaggregator-accountaggregationsource-allawsregions
            """
            result = self._values.get("all_aws_regions")
            return result

        @builtins.property
        def aws_regions(self) -> typing.Optional[typing.List[builtins.str]]:
            """``CfnConfigurationAggregator.AccountAggregationSourceProperty.AwsRegions``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-accountaggregationsource.html#cfn-config-configurationaggregator-accountaggregationsource-awsregions
            """
            result = self._values.get("aws_regions")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "AccountAggregationSourceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregator.OrganizationAggregationSourceProperty",
        jsii_struct_bases=[],
        name_mapping={
            "role_arn": "roleArn",
            "all_aws_regions": "allAwsRegions",
            "aws_regions": "awsRegions",
        },
    )
    class OrganizationAggregationSourceProperty:
        def __init__(
            self,
            *,
            role_arn: builtins.str,
            all_aws_regions: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            aws_regions: typing.Optional[typing.List[builtins.str]] = None,
        ) -> None:
            """
            :param role_arn: ``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.RoleArn``.
            :param all_aws_regions: ``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.AllAwsRegions``.
            :param aws_regions: ``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.AwsRegions``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "role_arn": role_arn,
            }
            if all_aws_regions is not None:
                self._values["all_aws_regions"] = all_aws_regions
            if aws_regions is not None:
                self._values["aws_regions"] = aws_regions

        @builtins.property
        def role_arn(self) -> builtins.str:
            """``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.RoleArn``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html#cfn-config-configurationaggregator-organizationaggregationsource-rolearn
            """
            result = self._values.get("role_arn")
            assert result is not None, "Required property 'role_arn' is missing"
            return result

        @builtins.property
        def all_aws_regions(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            """``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.AllAwsRegions``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html#cfn-config-configurationaggregator-organizationaggregationsource-allawsregions
            """
            result = self._values.get("all_aws_regions")
            return result

        @builtins.property
        def aws_regions(self) -> typing.Optional[typing.List[builtins.str]]:
            """``CfnConfigurationAggregator.OrganizationAggregationSourceProperty.AwsRegions``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationaggregator-organizationaggregationsource.html#cfn-config-configurationaggregator-organizationaggregationsource-awsregions
            """
            result = self._values.get("aws_regions")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OrganizationAggregationSourceProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnConfigurationAggregatorProps",
    jsii_struct_bases=[],
    name_mapping={
        "configuration_aggregator_name": "configurationAggregatorName",
        "account_aggregation_sources": "accountAggregationSources",
        "organization_aggregation_source": "organizationAggregationSource",
        "tags": "tags",
    },
)
class CfnConfigurationAggregatorProps:
    def __init__(
        self,
        *,
        configuration_aggregator_name: builtins.str,
        account_aggregation_sources: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnConfigurationAggregator.AccountAggregationSourceProperty]]]] = None,
        organization_aggregation_source: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnConfigurationAggregator.OrganizationAggregationSourceProperty]] = None,
        tags: typing.Optional[typing.List[aws_cdk.core.CfnTag]] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::ConfigurationAggregator``.

        :param configuration_aggregator_name: ``AWS::Config::ConfigurationAggregator.ConfigurationAggregatorName``.
        :param account_aggregation_sources: ``AWS::Config::ConfigurationAggregator.AccountAggregationSources``.
        :param organization_aggregation_source: ``AWS::Config::ConfigurationAggregator.OrganizationAggregationSource``.
        :param tags: ``AWS::Config::ConfigurationAggregator.Tags``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "configuration_aggregator_name": configuration_aggregator_name,
        }
        if account_aggregation_sources is not None:
            self._values["account_aggregation_sources"] = account_aggregation_sources
        if organization_aggregation_source is not None:
            self._values["organization_aggregation_source"] = organization_aggregation_source
        if tags is not None:
            self._values["tags"] = tags

    @builtins.property
    def configuration_aggregator_name(self) -> builtins.str:
        """``AWS::Config::ConfigurationAggregator.ConfigurationAggregatorName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-configurationaggregatorname
        """
        result = self._values.get("configuration_aggregator_name")
        assert result is not None, "Required property 'configuration_aggregator_name' is missing"
        return result

    @builtins.property
    def account_aggregation_sources(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnConfigurationAggregator.AccountAggregationSourceProperty]]]]:
        """``AWS::Config::ConfigurationAggregator.AccountAggregationSources``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-accountaggregationsources
        """
        result = self._values.get("account_aggregation_sources")
        return result

    @builtins.property
    def organization_aggregation_source(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnConfigurationAggregator.OrganizationAggregationSourceProperty]]:
        """``AWS::Config::ConfigurationAggregator.OrganizationAggregationSource``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-organizationaggregationsource
        """
        result = self._values.get("organization_aggregation_source")
        return result

    @builtins.property
    def tags(self) -> typing.Optional[typing.List[aws_cdk.core.CfnTag]]:
        """``AWS::Config::ConfigurationAggregator.Tags``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationaggregator.html#cfn-config-configurationaggregator-tags
        """
        result = self._values.get("tags")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnConfigurationAggregatorProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnConfigurationRecorder(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnConfigurationRecorder",
):
    """A CloudFormation ``AWS::Config::ConfigurationRecorder``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html
    :cloudformationResource: AWS::Config::ConfigurationRecorder
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        role_arn: builtins.str,
        name: typing.Optional[builtins.str] = None,
        recording_group: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationRecorder.RecordingGroupProperty"]] = None,
    ) -> None:
        """Create a new ``AWS::Config::ConfigurationRecorder``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param role_arn: ``AWS::Config::ConfigurationRecorder.RoleARN``.
        :param name: ``AWS::Config::ConfigurationRecorder.Name``.
        :param recording_group: ``AWS::Config::ConfigurationRecorder.RecordingGroup``.
        """
        props = CfnConfigurationRecorderProps(
            role_arn=role_arn, name=name, recording_group=recording_group
        )

        jsii.create(CfnConfigurationRecorder, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="roleArn")
    def role_arn(self) -> builtins.str:
        """``AWS::Config::ConfigurationRecorder.RoleARN``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-rolearn
        """
        return jsii.get(self, "roleArn")

    @role_arn.setter # type: ignore
    def role_arn(self, value: builtins.str) -> None:
        jsii.set(self, "roleArn", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigurationRecorder.Name``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-name
        """
        return jsii.get(self, "name")

    @name.setter # type: ignore
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="recordingGroup")
    def recording_group(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationRecorder.RecordingGroupProperty"]]:
        """``AWS::Config::ConfigurationRecorder.RecordingGroup``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-recordinggroup
        """
        return jsii.get(self, "recordingGroup")

    @recording_group.setter # type: ignore
    def recording_group(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnConfigurationRecorder.RecordingGroupProperty"]],
    ) -> None:
        jsii.set(self, "recordingGroup", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnConfigurationRecorder.RecordingGroupProperty",
        jsii_struct_bases=[],
        name_mapping={
            "all_supported": "allSupported",
            "include_global_resource_types": "includeGlobalResourceTypes",
            "resource_types": "resourceTypes",
        },
    )
    class RecordingGroupProperty:
        def __init__(
            self,
            *,
            all_supported: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            include_global_resource_types: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
            resource_types: typing.Optional[typing.List[builtins.str]] = None,
        ) -> None:
            """
            :param all_supported: ``CfnConfigurationRecorder.RecordingGroupProperty.AllSupported``.
            :param include_global_resource_types: ``CfnConfigurationRecorder.RecordingGroupProperty.IncludeGlobalResourceTypes``.
            :param resource_types: ``CfnConfigurationRecorder.RecordingGroupProperty.ResourceTypes``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if all_supported is not None:
                self._values["all_supported"] = all_supported
            if include_global_resource_types is not None:
                self._values["include_global_resource_types"] = include_global_resource_types
            if resource_types is not None:
                self._values["resource_types"] = resource_types

        @builtins.property
        def all_supported(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            """``CfnConfigurationRecorder.RecordingGroupProperty.AllSupported``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html#cfn-config-configurationrecorder-recordinggroup-allsupported
            """
            result = self._values.get("all_supported")
            return result

        @builtins.property
        def include_global_resource_types(
            self,
        ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
            """``CfnConfigurationRecorder.RecordingGroupProperty.IncludeGlobalResourceTypes``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html#cfn-config-configurationrecorder-recordinggroup-includeglobalresourcetypes
            """
            result = self._values.get("include_global_resource_types")
            return result

        @builtins.property
        def resource_types(self) -> typing.Optional[typing.List[builtins.str]]:
            """``CfnConfigurationRecorder.RecordingGroupProperty.ResourceTypes``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-configurationrecorder-recordinggroup.html#cfn-config-configurationrecorder-recordinggroup-resourcetypes
            """
            result = self._values.get("resource_types")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RecordingGroupProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnConfigurationRecorderProps",
    jsii_struct_bases=[],
    name_mapping={
        "role_arn": "roleArn",
        "name": "name",
        "recording_group": "recordingGroup",
    },
)
class CfnConfigurationRecorderProps:
    def __init__(
        self,
        *,
        role_arn: builtins.str,
        name: typing.Optional[builtins.str] = None,
        recording_group: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnConfigurationRecorder.RecordingGroupProperty]] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::ConfigurationRecorder``.

        :param role_arn: ``AWS::Config::ConfigurationRecorder.RoleARN``.
        :param name: ``AWS::Config::ConfigurationRecorder.Name``.
        :param recording_group: ``AWS::Config::ConfigurationRecorder.RecordingGroup``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "role_arn": role_arn,
        }
        if name is not None:
            self._values["name"] = name
        if recording_group is not None:
            self._values["recording_group"] = recording_group

    @builtins.property
    def role_arn(self) -> builtins.str:
        """``AWS::Config::ConfigurationRecorder.RoleARN``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-rolearn
        """
        result = self._values.get("role_arn")
        assert result is not None, "Required property 'role_arn' is missing"
        return result

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConfigurationRecorder.Name``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-name
        """
        result = self._values.get("name")
        return result

    @builtins.property
    def recording_group(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnConfigurationRecorder.RecordingGroupProperty]]:
        """``AWS::Config::ConfigurationRecorder.RecordingGroup``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-configurationrecorder.html#cfn-config-configurationrecorder-recordinggroup
        """
        result = self._values.get("recording_group")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnConfigurationRecorderProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnConformancePack(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnConformancePack",
):
    """A CloudFormation ``AWS::Config::ConformancePack``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html
    :cloudformationResource: AWS::Config::ConformancePack
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        conformance_pack_name: builtins.str,
        delivery_s3_bucket: builtins.str,
        conformance_pack_input_parameters: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConformancePack.ConformancePackInputParameterProperty"]]]] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        """Create a new ``AWS::Config::ConformancePack``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param conformance_pack_name: ``AWS::Config::ConformancePack.ConformancePackName``.
        :param delivery_s3_bucket: ``AWS::Config::ConformancePack.DeliveryS3Bucket``.
        :param conformance_pack_input_parameters: ``AWS::Config::ConformancePack.ConformancePackInputParameters``.
        :param delivery_s3_key_prefix: ``AWS::Config::ConformancePack.DeliveryS3KeyPrefix``.
        :param template_body: ``AWS::Config::ConformancePack.TemplateBody``.
        :param template_s3_uri: ``AWS::Config::ConformancePack.TemplateS3Uri``.
        """
        props = CfnConformancePackProps(
            conformance_pack_name=conformance_pack_name,
            delivery_s3_bucket=delivery_s3_bucket,
            conformance_pack_input_parameters=conformance_pack_input_parameters,
            delivery_s3_key_prefix=delivery_s3_key_prefix,
            template_body=template_body,
            template_s3_uri=template_s3_uri,
        )

        jsii.create(CfnConformancePack, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="conformancePackName")
    def conformance_pack_name(self) -> builtins.str:
        """``AWS::Config::ConformancePack.ConformancePackName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-conformancepackname
        """
        return jsii.get(self, "conformancePackName")

    @conformance_pack_name.setter # type: ignore
    def conformance_pack_name(self, value: builtins.str) -> None:
        jsii.set(self, "conformancePackName", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="deliveryS3Bucket")
    def delivery_s3_bucket(self) -> builtins.str:
        """``AWS::Config::ConformancePack.DeliveryS3Bucket``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-deliverys3bucket
        """
        return jsii.get(self, "deliveryS3Bucket")

    @delivery_s3_bucket.setter # type: ignore
    def delivery_s3_bucket(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryS3Bucket", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="conformancePackInputParameters")
    def conformance_pack_input_parameters(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConformancePack.ConformancePackInputParameterProperty"]]]]:
        """``AWS::Config::ConformancePack.ConformancePackInputParameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-conformancepackinputparameters
        """
        return jsii.get(self, "conformancePackInputParameters")

    @conformance_pack_input_parameters.setter # type: ignore
    def conformance_pack_input_parameters(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnConformancePack.ConformancePackInputParameterProperty"]]]],
    ) -> None:
        jsii.set(self, "conformancePackInputParameters", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="deliveryS3KeyPrefix")
    def delivery_s3_key_prefix(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConformancePack.DeliveryS3KeyPrefix``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-deliverys3keyprefix
        """
        return jsii.get(self, "deliveryS3KeyPrefix")

    @delivery_s3_key_prefix.setter # type: ignore
    def delivery_s3_key_prefix(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "deliveryS3KeyPrefix", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConformancePack.TemplateBody``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-templatebody
        """
        return jsii.get(self, "templateBody")

    @template_body.setter # type: ignore
    def template_body(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "templateBody", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="templateS3Uri")
    def template_s3_uri(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConformancePack.TemplateS3Uri``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-templates3uri
        """
        return jsii.get(self, "templateS3Uri")

    @template_s3_uri.setter # type: ignore
    def template_s3_uri(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "templateS3Uri", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnConformancePack.ConformancePackInputParameterProperty",
        jsii_struct_bases=[],
        name_mapping={
            "parameter_name": "parameterName",
            "parameter_value": "parameterValue",
        },
    )
    class ConformancePackInputParameterProperty:
        def __init__(
            self,
            *,
            parameter_name: builtins.str,
            parameter_value: builtins.str,
        ) -> None:
            """
            :param parameter_name: ``CfnConformancePack.ConformancePackInputParameterProperty.ParameterName``.
            :param parameter_value: ``CfnConformancePack.ConformancePackInputParameterProperty.ParameterValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-conformancepack-conformancepackinputparameter.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
            }

        @builtins.property
        def parameter_name(self) -> builtins.str:
            """``CfnConformancePack.ConformancePackInputParameterProperty.ParameterName``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-conformancepack-conformancepackinputparameter.html#cfn-config-conformancepack-conformancepackinputparameter-parametername
            """
            result = self._values.get("parameter_name")
            assert result is not None, "Required property 'parameter_name' is missing"
            return result

        @builtins.property
        def parameter_value(self) -> builtins.str:
            """``CfnConformancePack.ConformancePackInputParameterProperty.ParameterValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-conformancepack-conformancepackinputparameter.html#cfn-config-conformancepack-conformancepackinputparameter-parametervalue
            """
            result = self._values.get("parameter_value")
            assert result is not None, "Required property 'parameter_value' is missing"
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConformancePackInputParameterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnConformancePackProps",
    jsii_struct_bases=[],
    name_mapping={
        "conformance_pack_name": "conformancePackName",
        "delivery_s3_bucket": "deliveryS3Bucket",
        "conformance_pack_input_parameters": "conformancePackInputParameters",
        "delivery_s3_key_prefix": "deliveryS3KeyPrefix",
        "template_body": "templateBody",
        "template_s3_uri": "templateS3Uri",
    },
)
class CfnConformancePackProps:
    def __init__(
        self,
        *,
        conformance_pack_name: builtins.str,
        delivery_s3_bucket: builtins.str,
        conformance_pack_input_parameters: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnConformancePack.ConformancePackInputParameterProperty]]]] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::ConformancePack``.

        :param conformance_pack_name: ``AWS::Config::ConformancePack.ConformancePackName``.
        :param delivery_s3_bucket: ``AWS::Config::ConformancePack.DeliveryS3Bucket``.
        :param conformance_pack_input_parameters: ``AWS::Config::ConformancePack.ConformancePackInputParameters``.
        :param delivery_s3_key_prefix: ``AWS::Config::ConformancePack.DeliveryS3KeyPrefix``.
        :param template_body: ``AWS::Config::ConformancePack.TemplateBody``.
        :param template_s3_uri: ``AWS::Config::ConformancePack.TemplateS3Uri``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "conformance_pack_name": conformance_pack_name,
            "delivery_s3_bucket": delivery_s3_bucket,
        }
        if conformance_pack_input_parameters is not None:
            self._values["conformance_pack_input_parameters"] = conformance_pack_input_parameters
        if delivery_s3_key_prefix is not None:
            self._values["delivery_s3_key_prefix"] = delivery_s3_key_prefix
        if template_body is not None:
            self._values["template_body"] = template_body
        if template_s3_uri is not None:
            self._values["template_s3_uri"] = template_s3_uri

    @builtins.property
    def conformance_pack_name(self) -> builtins.str:
        """``AWS::Config::ConformancePack.ConformancePackName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-conformancepackname
        """
        result = self._values.get("conformance_pack_name")
        assert result is not None, "Required property 'conformance_pack_name' is missing"
        return result

    @builtins.property
    def delivery_s3_bucket(self) -> builtins.str:
        """``AWS::Config::ConformancePack.DeliveryS3Bucket``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-deliverys3bucket
        """
        result = self._values.get("delivery_s3_bucket")
        assert result is not None, "Required property 'delivery_s3_bucket' is missing"
        return result

    @builtins.property
    def conformance_pack_input_parameters(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnConformancePack.ConformancePackInputParameterProperty]]]]:
        """``AWS::Config::ConformancePack.ConformancePackInputParameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-conformancepackinputparameters
        """
        result = self._values.get("conformance_pack_input_parameters")
        return result

    @builtins.property
    def delivery_s3_key_prefix(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConformancePack.DeliveryS3KeyPrefix``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-deliverys3keyprefix
        """
        result = self._values.get("delivery_s3_key_prefix")
        return result

    @builtins.property
    def template_body(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConformancePack.TemplateBody``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-templatebody
        """
        result = self._values.get("template_body")
        return result

    @builtins.property
    def template_s3_uri(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::ConformancePack.TemplateS3Uri``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-conformancepack.html#cfn-config-conformancepack-templates3uri
        """
        result = self._values.get("template_s3_uri")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnConformancePackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnDeliveryChannel(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnDeliveryChannel",
):
    """A CloudFormation ``AWS::Config::DeliveryChannel``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html
    :cloudformationResource: AWS::Config::DeliveryChannel
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        s3_bucket_name: builtins.str,
        config_snapshot_delivery_properties: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty"]] = None,
        name: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        """Create a new ``AWS::Config::DeliveryChannel``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param s3_bucket_name: ``AWS::Config::DeliveryChannel.S3BucketName``.
        :param config_snapshot_delivery_properties: ``AWS::Config::DeliveryChannel.ConfigSnapshotDeliveryProperties``.
        :param name: ``AWS::Config::DeliveryChannel.Name``.
        :param s3_key_prefix: ``AWS::Config::DeliveryChannel.S3KeyPrefix``.
        :param sns_topic_arn: ``AWS::Config::DeliveryChannel.SnsTopicARN``.
        """
        props = CfnDeliveryChannelProps(
            s3_bucket_name=s3_bucket_name,
            config_snapshot_delivery_properties=config_snapshot_delivery_properties,
            name=name,
            s3_key_prefix=s3_key_prefix,
            sns_topic_arn=sns_topic_arn,
        )

        jsii.create(CfnDeliveryChannel, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="s3BucketName")
    def s3_bucket_name(self) -> builtins.str:
        """``AWS::Config::DeliveryChannel.S3BucketName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-s3bucketname
        """
        return jsii.get(self, "s3BucketName")

    @s3_bucket_name.setter # type: ignore
    def s3_bucket_name(self, value: builtins.str) -> None:
        jsii.set(self, "s3BucketName", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configSnapshotDeliveryProperties")
    def config_snapshot_delivery_properties(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty"]]:
        """``AWS::Config::DeliveryChannel.ConfigSnapshotDeliveryProperties``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-configsnapshotdeliveryproperties
        """
        return jsii.get(self, "configSnapshotDeliveryProperties")

    @config_snapshot_delivery_properties.setter # type: ignore
    def config_snapshot_delivery_properties(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty"]],
    ) -> None:
        jsii.set(self, "configSnapshotDeliveryProperties", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="name")
    def name(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::DeliveryChannel.Name``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-name
        """
        return jsii.get(self, "name")

    @name.setter # type: ignore
    def name(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "name", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="s3KeyPrefix")
    def s3_key_prefix(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::DeliveryChannel.S3KeyPrefix``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-s3keyprefix
        """
        return jsii.get(self, "s3KeyPrefix")

    @s3_key_prefix.setter # type: ignore
    def s3_key_prefix(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "s3KeyPrefix", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="snsTopicArn")
    def sns_topic_arn(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::DeliveryChannel.SnsTopicARN``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-snstopicarn
        """
        return jsii.get(self, "snsTopicArn")

    @sns_topic_arn.setter # type: ignore
    def sns_topic_arn(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "snsTopicArn", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty",
        jsii_struct_bases=[],
        name_mapping={"delivery_frequency": "deliveryFrequency"},
    )
    class ConfigSnapshotDeliveryPropertiesProperty:
        def __init__(
            self,
            *,
            delivery_frequency: typing.Optional[builtins.str] = None,
        ) -> None:
            """
            :param delivery_frequency: ``CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty.DeliveryFrequency``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-deliverychannel-configsnapshotdeliveryproperties.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if delivery_frequency is not None:
                self._values["delivery_frequency"] = delivery_frequency

        @builtins.property
        def delivery_frequency(self) -> typing.Optional[builtins.str]:
            """``CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty.DeliveryFrequency``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-deliverychannel-configsnapshotdeliveryproperties.html#cfn-config-deliverychannel-configsnapshotdeliveryproperties-deliveryfrequency
            """
            result = self._values.get("delivery_frequency")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConfigSnapshotDeliveryPropertiesProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnDeliveryChannelProps",
    jsii_struct_bases=[],
    name_mapping={
        "s3_bucket_name": "s3BucketName",
        "config_snapshot_delivery_properties": "configSnapshotDeliveryProperties",
        "name": "name",
        "s3_key_prefix": "s3KeyPrefix",
        "sns_topic_arn": "snsTopicArn",
    },
)
class CfnDeliveryChannelProps:
    def __init__(
        self,
        *,
        s3_bucket_name: builtins.str,
        config_snapshot_delivery_properties: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty]] = None,
        name: typing.Optional[builtins.str] = None,
        s3_key_prefix: typing.Optional[builtins.str] = None,
        sns_topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::DeliveryChannel``.

        :param s3_bucket_name: ``AWS::Config::DeliveryChannel.S3BucketName``.
        :param config_snapshot_delivery_properties: ``AWS::Config::DeliveryChannel.ConfigSnapshotDeliveryProperties``.
        :param name: ``AWS::Config::DeliveryChannel.Name``.
        :param s3_key_prefix: ``AWS::Config::DeliveryChannel.S3KeyPrefix``.
        :param sns_topic_arn: ``AWS::Config::DeliveryChannel.SnsTopicARN``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "s3_bucket_name": s3_bucket_name,
        }
        if config_snapshot_delivery_properties is not None:
            self._values["config_snapshot_delivery_properties"] = config_snapshot_delivery_properties
        if name is not None:
            self._values["name"] = name
        if s3_key_prefix is not None:
            self._values["s3_key_prefix"] = s3_key_prefix
        if sns_topic_arn is not None:
            self._values["sns_topic_arn"] = sns_topic_arn

    @builtins.property
    def s3_bucket_name(self) -> builtins.str:
        """``AWS::Config::DeliveryChannel.S3BucketName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-s3bucketname
        """
        result = self._values.get("s3_bucket_name")
        assert result is not None, "Required property 's3_bucket_name' is missing"
        return result

    @builtins.property
    def config_snapshot_delivery_properties(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnDeliveryChannel.ConfigSnapshotDeliveryPropertiesProperty]]:
        """``AWS::Config::DeliveryChannel.ConfigSnapshotDeliveryProperties``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-configsnapshotdeliveryproperties
        """
        result = self._values.get("config_snapshot_delivery_properties")
        return result

    @builtins.property
    def name(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::DeliveryChannel.Name``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-name
        """
        result = self._values.get("name")
        return result

    @builtins.property
    def s3_key_prefix(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::DeliveryChannel.S3KeyPrefix``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-s3keyprefix
        """
        result = self._values.get("s3_key_prefix")
        return result

    @builtins.property
    def sns_topic_arn(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::DeliveryChannel.SnsTopicARN``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-deliverychannel.html#cfn-config-deliverychannel-snstopicarn
        """
        result = self._values.get("sns_topic_arn")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnDeliveryChannelProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnOrganizationConfigRule(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnOrganizationConfigRule",
):
    """A CloudFormation ``AWS::Config::OrganizationConfigRule``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html
    :cloudformationResource: AWS::Config::OrganizationConfigRule
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        organization_config_rule_name: builtins.str,
        excluded_accounts: typing.Optional[typing.List[builtins.str]] = None,
        organization_custom_rule_metadata: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty"]] = None,
        organization_managed_rule_metadata: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty"]] = None,
    ) -> None:
        """Create a new ``AWS::Config::OrganizationConfigRule``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param organization_config_rule_name: ``AWS::Config::OrganizationConfigRule.OrganizationConfigRuleName``.
        :param excluded_accounts: ``AWS::Config::OrganizationConfigRule.ExcludedAccounts``.
        :param organization_custom_rule_metadata: ``AWS::Config::OrganizationConfigRule.OrganizationCustomRuleMetadata``.
        :param organization_managed_rule_metadata: ``AWS::Config::OrganizationConfigRule.OrganizationManagedRuleMetadata``.
        """
        props = CfnOrganizationConfigRuleProps(
            organization_config_rule_name=organization_config_rule_name,
            excluded_accounts=excluded_accounts,
            organization_custom_rule_metadata=organization_custom_rule_metadata,
            organization_managed_rule_metadata=organization_managed_rule_metadata,
        )

        jsii.create(CfnOrganizationConfigRule, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="organizationConfigRuleName")
    def organization_config_rule_name(self) -> builtins.str:
        """``AWS::Config::OrganizationConfigRule.OrganizationConfigRuleName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-organizationconfigrulename
        """
        return jsii.get(self, "organizationConfigRuleName")

    @organization_config_rule_name.setter # type: ignore
    def organization_config_rule_name(self, value: builtins.str) -> None:
        jsii.set(self, "organizationConfigRuleName", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="excludedAccounts")
    def excluded_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        """``AWS::Config::OrganizationConfigRule.ExcludedAccounts``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-excludedaccounts
        """
        return jsii.get(self, "excludedAccounts")

    @excluded_accounts.setter # type: ignore
    def excluded_accounts(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "excludedAccounts", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="organizationCustomRuleMetadata")
    def organization_custom_rule_metadata(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty"]]:
        """``AWS::Config::OrganizationConfigRule.OrganizationCustomRuleMetadata``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata
        """
        return jsii.get(self, "organizationCustomRuleMetadata")

    @organization_custom_rule_metadata.setter # type: ignore
    def organization_custom_rule_metadata(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty"]],
    ) -> None:
        jsii.set(self, "organizationCustomRuleMetadata", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="organizationManagedRuleMetadata")
    def organization_managed_rule_metadata(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty"]]:
        """``AWS::Config::OrganizationConfigRule.OrganizationManagedRuleMetadata``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata
        """
        return jsii.get(self, "organizationManagedRuleMetadata")

    @organization_managed_rule_metadata.setter # type: ignore
    def organization_managed_rule_metadata(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty"]],
    ) -> None:
        jsii.set(self, "organizationManagedRuleMetadata", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "lambda_function_arn": "lambdaFunctionArn",
            "organization_config_rule_trigger_types": "organizationConfigRuleTriggerTypes",
            "description": "description",
            "input_parameters": "inputParameters",
            "maximum_execution_frequency": "maximumExecutionFrequency",
            "resource_id_scope": "resourceIdScope",
            "resource_types_scope": "resourceTypesScope",
            "tag_key_scope": "tagKeyScope",
            "tag_value_scope": "tagValueScope",
        },
    )
    class OrganizationCustomRuleMetadataProperty:
        def __init__(
            self,
            *,
            lambda_function_arn: builtins.str,
            organization_config_rule_trigger_types: typing.List[builtins.str],
            description: typing.Optional[builtins.str] = None,
            input_parameters: typing.Optional[builtins.str] = None,
            maximum_execution_frequency: typing.Optional[builtins.str] = None,
            resource_id_scope: typing.Optional[builtins.str] = None,
            resource_types_scope: typing.Optional[typing.List[builtins.str]] = None,
            tag_key_scope: typing.Optional[builtins.str] = None,
            tag_value_scope: typing.Optional[builtins.str] = None,
        ) -> None:
            """
            :param lambda_function_arn: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.LambdaFunctionArn``.
            :param organization_config_rule_trigger_types: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.OrganizationConfigRuleTriggerTypes``.
            :param description: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.Description``.
            :param input_parameters: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.InputParameters``.
            :param maximum_execution_frequency: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.MaximumExecutionFrequency``.
            :param resource_id_scope: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.ResourceIdScope``.
            :param resource_types_scope: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.ResourceTypesScope``.
            :param tag_key_scope: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.TagKeyScope``.
            :param tag_value_scope: ``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.TagValueScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "lambda_function_arn": lambda_function_arn,
                "organization_config_rule_trigger_types": organization_config_rule_trigger_types,
            }
            if description is not None:
                self._values["description"] = description
            if input_parameters is not None:
                self._values["input_parameters"] = input_parameters
            if maximum_execution_frequency is not None:
                self._values["maximum_execution_frequency"] = maximum_execution_frequency
            if resource_id_scope is not None:
                self._values["resource_id_scope"] = resource_id_scope
            if resource_types_scope is not None:
                self._values["resource_types_scope"] = resource_types_scope
            if tag_key_scope is not None:
                self._values["tag_key_scope"] = tag_key_scope
            if tag_value_scope is not None:
                self._values["tag_value_scope"] = tag_value_scope

        @builtins.property
        def lambda_function_arn(self) -> builtins.str:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.LambdaFunctionArn``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-lambdafunctionarn
            """
            result = self._values.get("lambda_function_arn")
            assert result is not None, "Required property 'lambda_function_arn' is missing"
            return result

        @builtins.property
        def organization_config_rule_trigger_types(self) -> typing.List[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.OrganizationConfigRuleTriggerTypes``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-organizationconfigruletriggertypes
            """
            result = self._values.get("organization_config_rule_trigger_types")
            assert result is not None, "Required property 'organization_config_rule_trigger_types' is missing"
            return result

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.Description``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-description
            """
            result = self._values.get("description")
            return result

        @builtins.property
        def input_parameters(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.InputParameters``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-inputparameters
            """
            result = self._values.get("input_parameters")
            return result

        @builtins.property
        def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.MaximumExecutionFrequency``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-maximumexecutionfrequency
            """
            result = self._values.get("maximum_execution_frequency")
            return result

        @builtins.property
        def resource_id_scope(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.ResourceIdScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-resourceidscope
            """
            result = self._values.get("resource_id_scope")
            return result

        @builtins.property
        def resource_types_scope(self) -> typing.Optional[typing.List[builtins.str]]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.ResourceTypesScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-resourcetypesscope
            """
            result = self._values.get("resource_types_scope")
            return result

        @builtins.property
        def tag_key_scope(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.TagKeyScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-tagkeyscope
            """
            result = self._values.get("tag_key_scope")
            return result

        @builtins.property
        def tag_value_scope(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty.TagValueScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationcustomrulemetadata.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata-tagvaluescope
            """
            result = self._values.get("tag_value_scope")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OrganizationCustomRuleMetadataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty",
        jsii_struct_bases=[],
        name_mapping={
            "rule_identifier": "ruleIdentifier",
            "description": "description",
            "input_parameters": "inputParameters",
            "maximum_execution_frequency": "maximumExecutionFrequency",
            "resource_id_scope": "resourceIdScope",
            "resource_types_scope": "resourceTypesScope",
            "tag_key_scope": "tagKeyScope",
            "tag_value_scope": "tagValueScope",
        },
    )
    class OrganizationManagedRuleMetadataProperty:
        def __init__(
            self,
            *,
            rule_identifier: builtins.str,
            description: typing.Optional[builtins.str] = None,
            input_parameters: typing.Optional[builtins.str] = None,
            maximum_execution_frequency: typing.Optional[builtins.str] = None,
            resource_id_scope: typing.Optional[builtins.str] = None,
            resource_types_scope: typing.Optional[typing.List[builtins.str]] = None,
            tag_key_scope: typing.Optional[builtins.str] = None,
            tag_value_scope: typing.Optional[builtins.str] = None,
        ) -> None:
            """
            :param rule_identifier: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.RuleIdentifier``.
            :param description: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.Description``.
            :param input_parameters: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.InputParameters``.
            :param maximum_execution_frequency: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.MaximumExecutionFrequency``.
            :param resource_id_scope: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.ResourceIdScope``.
            :param resource_types_scope: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.ResourceTypesScope``.
            :param tag_key_scope: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.TagKeyScope``.
            :param tag_value_scope: ``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.TagValueScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "rule_identifier": rule_identifier,
            }
            if description is not None:
                self._values["description"] = description
            if input_parameters is not None:
                self._values["input_parameters"] = input_parameters
            if maximum_execution_frequency is not None:
                self._values["maximum_execution_frequency"] = maximum_execution_frequency
            if resource_id_scope is not None:
                self._values["resource_id_scope"] = resource_id_scope
            if resource_types_scope is not None:
                self._values["resource_types_scope"] = resource_types_scope
            if tag_key_scope is not None:
                self._values["tag_key_scope"] = tag_key_scope
            if tag_value_scope is not None:
                self._values["tag_value_scope"] = tag_value_scope

        @builtins.property
        def rule_identifier(self) -> builtins.str:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.RuleIdentifier``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-ruleidentifier
            """
            result = self._values.get("rule_identifier")
            assert result is not None, "Required property 'rule_identifier' is missing"
            return result

        @builtins.property
        def description(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.Description``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-description
            """
            result = self._values.get("description")
            return result

        @builtins.property
        def input_parameters(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.InputParameters``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-inputparameters
            """
            result = self._values.get("input_parameters")
            return result

        @builtins.property
        def maximum_execution_frequency(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.MaximumExecutionFrequency``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-maximumexecutionfrequency
            """
            result = self._values.get("maximum_execution_frequency")
            return result

        @builtins.property
        def resource_id_scope(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.ResourceIdScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-resourceidscope
            """
            result = self._values.get("resource_id_scope")
            return result

        @builtins.property
        def resource_types_scope(self) -> typing.Optional[typing.List[builtins.str]]:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.ResourceTypesScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-resourcetypesscope
            """
            result = self._values.get("resource_types_scope")
            return result

        @builtins.property
        def tag_key_scope(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.TagKeyScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-tagkeyscope
            """
            result = self._values.get("tag_key_scope")
            return result

        @builtins.property
        def tag_value_scope(self) -> typing.Optional[builtins.str]:
            """``CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty.TagValueScope``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconfigrule-organizationmanagedrulemetadata.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata-tagvaluescope
            """
            result = self._values.get("tag_value_scope")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "OrganizationManagedRuleMetadataProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnOrganizationConfigRuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "organization_config_rule_name": "organizationConfigRuleName",
        "excluded_accounts": "excludedAccounts",
        "organization_custom_rule_metadata": "organizationCustomRuleMetadata",
        "organization_managed_rule_metadata": "organizationManagedRuleMetadata",
    },
)
class CfnOrganizationConfigRuleProps:
    def __init__(
        self,
        *,
        organization_config_rule_name: builtins.str,
        excluded_accounts: typing.Optional[typing.List[builtins.str]] = None,
        organization_custom_rule_metadata: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty]] = None,
        organization_managed_rule_metadata: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty]] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::OrganizationConfigRule``.

        :param organization_config_rule_name: ``AWS::Config::OrganizationConfigRule.OrganizationConfigRuleName``.
        :param excluded_accounts: ``AWS::Config::OrganizationConfigRule.ExcludedAccounts``.
        :param organization_custom_rule_metadata: ``AWS::Config::OrganizationConfigRule.OrganizationCustomRuleMetadata``.
        :param organization_managed_rule_metadata: ``AWS::Config::OrganizationConfigRule.OrganizationManagedRuleMetadata``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "organization_config_rule_name": organization_config_rule_name,
        }
        if excluded_accounts is not None:
            self._values["excluded_accounts"] = excluded_accounts
        if organization_custom_rule_metadata is not None:
            self._values["organization_custom_rule_metadata"] = organization_custom_rule_metadata
        if organization_managed_rule_metadata is not None:
            self._values["organization_managed_rule_metadata"] = organization_managed_rule_metadata

    @builtins.property
    def organization_config_rule_name(self) -> builtins.str:
        """``AWS::Config::OrganizationConfigRule.OrganizationConfigRuleName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-organizationconfigrulename
        """
        result = self._values.get("organization_config_rule_name")
        assert result is not None, "Required property 'organization_config_rule_name' is missing"
        return result

    @builtins.property
    def excluded_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        """``AWS::Config::OrganizationConfigRule.ExcludedAccounts``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-excludedaccounts
        """
        result = self._values.get("excluded_accounts")
        return result

    @builtins.property
    def organization_custom_rule_metadata(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnOrganizationConfigRule.OrganizationCustomRuleMetadataProperty]]:
        """``AWS::Config::OrganizationConfigRule.OrganizationCustomRuleMetadata``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-organizationcustomrulemetadata
        """
        result = self._values.get("organization_custom_rule_metadata")
        return result

    @builtins.property
    def organization_managed_rule_metadata(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnOrganizationConfigRule.OrganizationManagedRuleMetadataProperty]]:
        """``AWS::Config::OrganizationConfigRule.OrganizationManagedRuleMetadata``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconfigrule.html#cfn-config-organizationconfigrule-organizationmanagedrulemetadata
        """
        result = self._values.get("organization_managed_rule_metadata")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnOrganizationConfigRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnOrganizationConformancePack(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnOrganizationConformancePack",
):
    """A CloudFormation ``AWS::Config::OrganizationConformancePack``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html
    :cloudformationResource: AWS::Config::OrganizationConformancePack
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        delivery_s3_bucket: builtins.str,
        organization_conformance_pack_name: builtins.str,
        conformance_pack_input_parameters: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConformancePack.ConformancePackInputParameterProperty"]]]] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.List[builtins.str]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        """Create a new ``AWS::Config::OrganizationConformancePack``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param delivery_s3_bucket: ``AWS::Config::OrganizationConformancePack.DeliveryS3Bucket``.
        :param organization_conformance_pack_name: ``AWS::Config::OrganizationConformancePack.OrganizationConformancePackName``.
        :param conformance_pack_input_parameters: ``AWS::Config::OrganizationConformancePack.ConformancePackInputParameters``.
        :param delivery_s3_key_prefix: ``AWS::Config::OrganizationConformancePack.DeliveryS3KeyPrefix``.
        :param excluded_accounts: ``AWS::Config::OrganizationConformancePack.ExcludedAccounts``.
        :param template_body: ``AWS::Config::OrganizationConformancePack.TemplateBody``.
        :param template_s3_uri: ``AWS::Config::OrganizationConformancePack.TemplateS3Uri``.
        """
        props = CfnOrganizationConformancePackProps(
            delivery_s3_bucket=delivery_s3_bucket,
            organization_conformance_pack_name=organization_conformance_pack_name,
            conformance_pack_input_parameters=conformance_pack_input_parameters,
            delivery_s3_key_prefix=delivery_s3_key_prefix,
            excluded_accounts=excluded_accounts,
            template_body=template_body,
            template_s3_uri=template_s3_uri,
        )

        jsii.create(CfnOrganizationConformancePack, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="deliveryS3Bucket")
    def delivery_s3_bucket(self) -> builtins.str:
        """``AWS::Config::OrganizationConformancePack.DeliveryS3Bucket``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-deliverys3bucket
        """
        return jsii.get(self, "deliveryS3Bucket")

    @delivery_s3_bucket.setter # type: ignore
    def delivery_s3_bucket(self, value: builtins.str) -> None:
        jsii.set(self, "deliveryS3Bucket", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="organizationConformancePackName")
    def organization_conformance_pack_name(self) -> builtins.str:
        """``AWS::Config::OrganizationConformancePack.OrganizationConformancePackName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-organizationconformancepackname
        """
        return jsii.get(self, "organizationConformancePackName")

    @organization_conformance_pack_name.setter # type: ignore
    def organization_conformance_pack_name(self, value: builtins.str) -> None:
        jsii.set(self, "organizationConformancePackName", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="conformancePackInputParameters")
    def conformance_pack_input_parameters(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConformancePack.ConformancePackInputParameterProperty"]]]]:
        """``AWS::Config::OrganizationConformancePack.ConformancePackInputParameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-conformancepackinputparameters
        """
        return jsii.get(self, "conformancePackInputParameters")

    @conformance_pack_input_parameters.setter # type: ignore
    def conformance_pack_input_parameters(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, "CfnOrganizationConformancePack.ConformancePackInputParameterProperty"]]]],
    ) -> None:
        jsii.set(self, "conformancePackInputParameters", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="deliveryS3KeyPrefix")
    def delivery_s3_key_prefix(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::OrganizationConformancePack.DeliveryS3KeyPrefix``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-deliverys3keyprefix
        """
        return jsii.get(self, "deliveryS3KeyPrefix")

    @delivery_s3_key_prefix.setter # type: ignore
    def delivery_s3_key_prefix(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "deliveryS3KeyPrefix", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="excludedAccounts")
    def excluded_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        """``AWS::Config::OrganizationConformancePack.ExcludedAccounts``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-excludedaccounts
        """
        return jsii.get(self, "excludedAccounts")

    @excluded_accounts.setter # type: ignore
    def excluded_accounts(
        self,
        value: typing.Optional[typing.List[builtins.str]],
    ) -> None:
        jsii.set(self, "excludedAccounts", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="templateBody")
    def template_body(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::OrganizationConformancePack.TemplateBody``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-templatebody
        """
        return jsii.get(self, "templateBody")

    @template_body.setter # type: ignore
    def template_body(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "templateBody", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="templateS3Uri")
    def template_s3_uri(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::OrganizationConformancePack.TemplateS3Uri``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-templates3uri
        """
        return jsii.get(self, "templateS3Uri")

    @template_s3_uri.setter # type: ignore
    def template_s3_uri(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "templateS3Uri", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnOrganizationConformancePack.ConformancePackInputParameterProperty",
        jsii_struct_bases=[],
        name_mapping={
            "parameter_name": "parameterName",
            "parameter_value": "parameterValue",
        },
    )
    class ConformancePackInputParameterProperty:
        def __init__(
            self,
            *,
            parameter_name: builtins.str,
            parameter_value: builtins.str,
        ) -> None:
            """
            :param parameter_name: ``CfnOrganizationConformancePack.ConformancePackInputParameterProperty.ParameterName``.
            :param parameter_value: ``CfnOrganizationConformancePack.ConformancePackInputParameterProperty.ParameterValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconformancepack-conformancepackinputparameter.html
            """
            self._values: typing.Dict[str, typing.Any] = {
                "parameter_name": parameter_name,
                "parameter_value": parameter_value,
            }

        @builtins.property
        def parameter_name(self) -> builtins.str:
            """``CfnOrganizationConformancePack.ConformancePackInputParameterProperty.ParameterName``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconformancepack-conformancepackinputparameter.html#cfn-config-organizationconformancepack-conformancepackinputparameter-parametername
            """
            result = self._values.get("parameter_name")
            assert result is not None, "Required property 'parameter_name' is missing"
            return result

        @builtins.property
        def parameter_value(self) -> builtins.str:
            """``CfnOrganizationConformancePack.ConformancePackInputParameterProperty.ParameterValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-organizationconformancepack-conformancepackinputparameter.html#cfn-config-organizationconformancepack-conformancepackinputparameter-parametervalue
            """
            result = self._values.get("parameter_value")
            assert result is not None, "Required property 'parameter_value' is missing"
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ConformancePackInputParameterProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnOrganizationConformancePackProps",
    jsii_struct_bases=[],
    name_mapping={
        "delivery_s3_bucket": "deliveryS3Bucket",
        "organization_conformance_pack_name": "organizationConformancePackName",
        "conformance_pack_input_parameters": "conformancePackInputParameters",
        "delivery_s3_key_prefix": "deliveryS3KeyPrefix",
        "excluded_accounts": "excludedAccounts",
        "template_body": "templateBody",
        "template_s3_uri": "templateS3Uri",
    },
)
class CfnOrganizationConformancePackProps:
    def __init__(
        self,
        *,
        delivery_s3_bucket: builtins.str,
        organization_conformance_pack_name: builtins.str,
        conformance_pack_input_parameters: typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnOrganizationConformancePack.ConformancePackInputParameterProperty]]]] = None,
        delivery_s3_key_prefix: typing.Optional[builtins.str] = None,
        excluded_accounts: typing.Optional[typing.List[builtins.str]] = None,
        template_body: typing.Optional[builtins.str] = None,
        template_s3_uri: typing.Optional[builtins.str] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::OrganizationConformancePack``.

        :param delivery_s3_bucket: ``AWS::Config::OrganizationConformancePack.DeliveryS3Bucket``.
        :param organization_conformance_pack_name: ``AWS::Config::OrganizationConformancePack.OrganizationConformancePackName``.
        :param conformance_pack_input_parameters: ``AWS::Config::OrganizationConformancePack.ConformancePackInputParameters``.
        :param delivery_s3_key_prefix: ``AWS::Config::OrganizationConformancePack.DeliveryS3KeyPrefix``.
        :param excluded_accounts: ``AWS::Config::OrganizationConformancePack.ExcludedAccounts``.
        :param template_body: ``AWS::Config::OrganizationConformancePack.TemplateBody``.
        :param template_s3_uri: ``AWS::Config::OrganizationConformancePack.TemplateS3Uri``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "delivery_s3_bucket": delivery_s3_bucket,
            "organization_conformance_pack_name": organization_conformance_pack_name,
        }
        if conformance_pack_input_parameters is not None:
            self._values["conformance_pack_input_parameters"] = conformance_pack_input_parameters
        if delivery_s3_key_prefix is not None:
            self._values["delivery_s3_key_prefix"] = delivery_s3_key_prefix
        if excluded_accounts is not None:
            self._values["excluded_accounts"] = excluded_accounts
        if template_body is not None:
            self._values["template_body"] = template_body
        if template_s3_uri is not None:
            self._values["template_s3_uri"] = template_s3_uri

    @builtins.property
    def delivery_s3_bucket(self) -> builtins.str:
        """``AWS::Config::OrganizationConformancePack.DeliveryS3Bucket``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-deliverys3bucket
        """
        result = self._values.get("delivery_s3_bucket")
        assert result is not None, "Required property 'delivery_s3_bucket' is missing"
        return result

    @builtins.property
    def organization_conformance_pack_name(self) -> builtins.str:
        """``AWS::Config::OrganizationConformancePack.OrganizationConformancePackName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-organizationconformancepackname
        """
        result = self._values.get("organization_conformance_pack_name")
        assert result is not None, "Required property 'organization_conformance_pack_name' is missing"
        return result

    @builtins.property
    def conformance_pack_input_parameters(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, typing.List[typing.Union[aws_cdk.core.IResolvable, CfnOrganizationConformancePack.ConformancePackInputParameterProperty]]]]:
        """``AWS::Config::OrganizationConformancePack.ConformancePackInputParameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-conformancepackinputparameters
        """
        result = self._values.get("conformance_pack_input_parameters")
        return result

    @builtins.property
    def delivery_s3_key_prefix(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::OrganizationConformancePack.DeliveryS3KeyPrefix``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-deliverys3keyprefix
        """
        result = self._values.get("delivery_s3_key_prefix")
        return result

    @builtins.property
    def excluded_accounts(self) -> typing.Optional[typing.List[builtins.str]]:
        """``AWS::Config::OrganizationConformancePack.ExcludedAccounts``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-excludedaccounts
        """
        result = self._values.get("excluded_accounts")
        return result

    @builtins.property
    def template_body(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::OrganizationConformancePack.TemplateBody``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-templatebody
        """
        result = self._values.get("template_body")
        return result

    @builtins.property
    def template_s3_uri(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::OrganizationConformancePack.TemplateS3Uri``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-organizationconformancepack.html#cfn-config-organizationconformancepack-templates3uri
        """
        result = self._values.get("template_s3_uri")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnOrganizationConformancePackProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(aws_cdk.core.IInspectable)
class CfnRemediationConfiguration(
    aws_cdk.core.CfnResource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CfnRemediationConfiguration",
):
    """A CloudFormation ``AWS::Config::RemediationConfiguration``.

    :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html
    :cloudformationResource: AWS::Config::RemediationConfiguration
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        config_rule_name: builtins.str,
        target_id: builtins.str,
        target_type: builtins.str,
        automatic: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        execution_controls: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.ExecutionControlsProperty"]] = None,
        maximum_automatic_attempts: typing.Optional[jsii.Number] = None,
        parameters: typing.Any = None,
        resource_type: typing.Optional[builtins.str] = None,
        retry_attempt_seconds: typing.Optional[jsii.Number] = None,
        target_version: typing.Optional[builtins.str] = None,
    ) -> None:
        """Create a new ``AWS::Config::RemediationConfiguration``.

        :param scope: - scope in which this resource is defined.
        :param id: - scoped id of the resource.
        :param config_rule_name: ``AWS::Config::RemediationConfiguration.ConfigRuleName``.
        :param target_id: ``AWS::Config::RemediationConfiguration.TargetId``.
        :param target_type: ``AWS::Config::RemediationConfiguration.TargetType``.
        :param automatic: ``AWS::Config::RemediationConfiguration.Automatic``.
        :param execution_controls: ``AWS::Config::RemediationConfiguration.ExecutionControls``.
        :param maximum_automatic_attempts: ``AWS::Config::RemediationConfiguration.MaximumAutomaticAttempts``.
        :param parameters: ``AWS::Config::RemediationConfiguration.Parameters``.
        :param resource_type: ``AWS::Config::RemediationConfiguration.ResourceType``.
        :param retry_attempt_seconds: ``AWS::Config::RemediationConfiguration.RetryAttemptSeconds``.
        :param target_version: ``AWS::Config::RemediationConfiguration.TargetVersion``.
        """
        props = CfnRemediationConfigurationProps(
            config_rule_name=config_rule_name,
            target_id=target_id,
            target_type=target_type,
            automatic=automatic,
            execution_controls=execution_controls,
            maximum_automatic_attempts=maximum_automatic_attempts,
            parameters=parameters,
            resource_type=resource_type,
            retry_attempt_seconds=retry_attempt_seconds,
            target_version=target_version,
        )

        jsii.create(CfnRemediationConfiguration, self, [scope, id, props])

    @jsii.member(jsii_name="inspect")
    def inspect(self, inspector: aws_cdk.core.TreeInspector) -> None:
        """(experimental) Examines the CloudFormation resource and discloses attributes.

        :param inspector: - tree inspector to collect and process attributes.

        :stability: experimental
        """
        return jsii.invoke(self, "inspect", [inspector])

    @jsii.member(jsii_name="renderProperties")
    def _render_properties(
        self,
        props: typing.Mapping[builtins.str, typing.Any],
    ) -> typing.Mapping[builtins.str, typing.Any]:
        """
        :param props: -
        """
        return jsii.invoke(self, "renderProperties", [props])

    @jsii.python.classproperty # type: ignore
    @jsii.member(jsii_name="CFN_RESOURCE_TYPE_NAME")
    def CFN_RESOURCE_TYPE_NAME(cls) -> builtins.str:
        """The CloudFormation resource type name for this resource class."""
        return jsii.sget(cls, "CFN_RESOURCE_TYPE_NAME")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="cfnProperties")
    def _cfn_properties(self) -> typing.Mapping[builtins.str, typing.Any]:
        return jsii.get(self, "cfnProperties")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> builtins.str:
        """``AWS::Config::RemediationConfiguration.ConfigRuleName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-configrulename
        """
        return jsii.get(self, "configRuleName")

    @config_rule_name.setter # type: ignore
    def config_rule_name(self, value: builtins.str) -> None:
        jsii.set(self, "configRuleName", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="parameters")
    def parameters(self) -> typing.Any:
        """``AWS::Config::RemediationConfiguration.Parameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-parameters
        """
        return jsii.get(self, "parameters")

    @parameters.setter # type: ignore
    def parameters(self, value: typing.Any) -> None:
        jsii.set(self, "parameters", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="targetId")
    def target_id(self) -> builtins.str:
        """``AWS::Config::RemediationConfiguration.TargetId``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-targetid
        """
        return jsii.get(self, "targetId")

    @target_id.setter # type: ignore
    def target_id(self, value: builtins.str) -> None:
        jsii.set(self, "targetId", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="targetType")
    def target_type(self) -> builtins.str:
        """``AWS::Config::RemediationConfiguration.TargetType``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-targettype
        """
        return jsii.get(self, "targetType")

    @target_type.setter # type: ignore
    def target_type(self, value: builtins.str) -> None:
        jsii.set(self, "targetType", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="automatic")
    def automatic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        """``AWS::Config::RemediationConfiguration.Automatic``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-automatic
        """
        return jsii.get(self, "automatic")

    @automatic.setter # type: ignore
    def automatic(
        self,
        value: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]],
    ) -> None:
        jsii.set(self, "automatic", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="executionControls")
    def execution_controls(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.ExecutionControlsProperty"]]:
        """``AWS::Config::RemediationConfiguration.ExecutionControls``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-executioncontrols
        """
        return jsii.get(self, "executionControls")

    @execution_controls.setter # type: ignore
    def execution_controls(
        self,
        value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.ExecutionControlsProperty"]],
    ) -> None:
        jsii.set(self, "executionControls", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="maximumAutomaticAttempts")
    def maximum_automatic_attempts(self) -> typing.Optional[jsii.Number]:
        """``AWS::Config::RemediationConfiguration.MaximumAutomaticAttempts``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-maximumautomaticattempts
        """
        return jsii.get(self, "maximumAutomaticAttempts")

    @maximum_automatic_attempts.setter # type: ignore
    def maximum_automatic_attempts(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "maximumAutomaticAttempts", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="resourceType")
    def resource_type(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::RemediationConfiguration.ResourceType``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-resourcetype
        """
        return jsii.get(self, "resourceType")

    @resource_type.setter # type: ignore
    def resource_type(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "resourceType", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="retryAttemptSeconds")
    def retry_attempt_seconds(self) -> typing.Optional[jsii.Number]:
        """``AWS::Config::RemediationConfiguration.RetryAttemptSeconds``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-retryattemptseconds
        """
        return jsii.get(self, "retryAttemptSeconds")

    @retry_attempt_seconds.setter # type: ignore
    def retry_attempt_seconds(self, value: typing.Optional[jsii.Number]) -> None:
        jsii.set(self, "retryAttemptSeconds", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="targetVersion")
    def target_version(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::RemediationConfiguration.TargetVersion``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-targetversion
        """
        return jsii.get(self, "targetVersion")

    @target_version.setter # type: ignore
    def target_version(self, value: typing.Optional[builtins.str]) -> None:
        jsii.set(self, "targetVersion", value)

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnRemediationConfiguration.ExecutionControlsProperty",
        jsii_struct_bases=[],
        name_mapping={"ssm_controls": "ssmControls"},
    )
    class ExecutionControlsProperty:
        def __init__(
            self,
            *,
            ssm_controls: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.SsmControlsProperty"]] = None,
        ) -> None:
            """
            :param ssm_controls: ``CfnRemediationConfiguration.ExecutionControlsProperty.SsmControls``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-executioncontrols.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if ssm_controls is not None:
                self._values["ssm_controls"] = ssm_controls

        @builtins.property
        def ssm_controls(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.SsmControlsProperty"]]:
            """``CfnRemediationConfiguration.ExecutionControlsProperty.SsmControls``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-executioncontrols.html#cfn-config-remediationconfiguration-executioncontrols-ssmcontrols
            """
            result = self._values.get("ssm_controls")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ExecutionControlsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnRemediationConfiguration.RemediationParameterValueProperty",
        jsii_struct_bases=[],
        name_mapping={
            "resource_value": "resourceValue",
            "static_value": "staticValue",
        },
    )
    class RemediationParameterValueProperty:
        def __init__(
            self,
            *,
            resource_value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.ResourceValueProperty"]] = None,
            static_value: typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.StaticValueProperty"]] = None,
        ) -> None:
            """
            :param resource_value: ``CfnRemediationConfiguration.RemediationParameterValueProperty.ResourceValue``.
            :param static_value: ``CfnRemediationConfiguration.RemediationParameterValueProperty.StaticValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-remediationparametervalue.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if resource_value is not None:
                self._values["resource_value"] = resource_value
            if static_value is not None:
                self._values["static_value"] = static_value

        @builtins.property
        def resource_value(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.ResourceValueProperty"]]:
            """``CfnRemediationConfiguration.RemediationParameterValueProperty.ResourceValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-remediationparametervalue.html#cfn-config-remediationconfiguration-remediationparametervalue-resourcevalue
            """
            result = self._values.get("resource_value")
            return result

        @builtins.property
        def static_value(
            self,
        ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, "CfnRemediationConfiguration.StaticValueProperty"]]:
            """``CfnRemediationConfiguration.RemediationParameterValueProperty.StaticValue``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-remediationparametervalue.html#cfn-config-remediationconfiguration-remediationparametervalue-staticvalue
            """
            result = self._values.get("static_value")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "RemediationParameterValueProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnRemediationConfiguration.ResourceValueProperty",
        jsii_struct_bases=[],
        name_mapping={"value": "value"},
    )
    class ResourceValueProperty:
        def __init__(self, *, value: typing.Optional[builtins.str] = None) -> None:
            """
            :param value: ``CfnRemediationConfiguration.ResourceValueProperty.Value``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-resourcevalue.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if value is not None:
                self._values["value"] = value

        @builtins.property
        def value(self) -> typing.Optional[builtins.str]:
            """``CfnRemediationConfiguration.ResourceValueProperty.Value``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-resourcevalue.html#cfn-config-remediationconfiguration-resourcevalue-value
            """
            result = self._values.get("value")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "ResourceValueProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnRemediationConfiguration.SsmControlsProperty",
        jsii_struct_bases=[],
        name_mapping={
            "concurrent_execution_rate_percentage": "concurrentExecutionRatePercentage",
            "error_percentage": "errorPercentage",
        },
    )
    class SsmControlsProperty:
        def __init__(
            self,
            *,
            concurrent_execution_rate_percentage: typing.Optional[jsii.Number] = None,
            error_percentage: typing.Optional[jsii.Number] = None,
        ) -> None:
            """
            :param concurrent_execution_rate_percentage: ``CfnRemediationConfiguration.SsmControlsProperty.ConcurrentExecutionRatePercentage``.
            :param error_percentage: ``CfnRemediationConfiguration.SsmControlsProperty.ErrorPercentage``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-ssmcontrols.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if concurrent_execution_rate_percentage is not None:
                self._values["concurrent_execution_rate_percentage"] = concurrent_execution_rate_percentage
            if error_percentage is not None:
                self._values["error_percentage"] = error_percentage

        @builtins.property
        def concurrent_execution_rate_percentage(self) -> typing.Optional[jsii.Number]:
            """``CfnRemediationConfiguration.SsmControlsProperty.ConcurrentExecutionRatePercentage``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-ssmcontrols.html#cfn-config-remediationconfiguration-ssmcontrols-concurrentexecutionratepercentage
            """
            result = self._values.get("concurrent_execution_rate_percentage")
            return result

        @builtins.property
        def error_percentage(self) -> typing.Optional[jsii.Number]:
            """``CfnRemediationConfiguration.SsmControlsProperty.ErrorPercentage``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-ssmcontrols.html#cfn-config-remediationconfiguration-ssmcontrols-errorpercentage
            """
            result = self._values.get("error_percentage")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "SsmControlsProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )

    @jsii.data_type(
        jsii_type="@aws-cdk/aws-config.CfnRemediationConfiguration.StaticValueProperty",
        jsii_struct_bases=[],
        name_mapping={"values": "values"},
    )
    class StaticValueProperty:
        def __init__(
            self,
            *,
            values: typing.Optional[typing.List[builtins.str]] = None,
        ) -> None:
            """
            :param values: ``CfnRemediationConfiguration.StaticValueProperty.Values``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-staticvalue.html
            """
            self._values: typing.Dict[str, typing.Any] = {}
            if values is not None:
                self._values["values"] = values

        @builtins.property
        def values(self) -> typing.Optional[typing.List[builtins.str]]:
            """``CfnRemediationConfiguration.StaticValueProperty.Values``.

            :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-config-remediationconfiguration-staticvalue.html#cfn-config-remediationconfiguration-staticvalue-values
            """
            result = self._values.get("values")
            return result

        def __eq__(self, rhs: typing.Any) -> builtins.bool:
            return isinstance(rhs, self.__class__) and rhs._values == self._values

        def __ne__(self, rhs: typing.Any) -> builtins.bool:
            return not (rhs == self)

        def __repr__(self) -> str:
            return "StaticValueProperty(%s)" % ", ".join(
                k + "=" + repr(v) for k, v in self._values.items()
            )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CfnRemediationConfigurationProps",
    jsii_struct_bases=[],
    name_mapping={
        "config_rule_name": "configRuleName",
        "target_id": "targetId",
        "target_type": "targetType",
        "automatic": "automatic",
        "execution_controls": "executionControls",
        "maximum_automatic_attempts": "maximumAutomaticAttempts",
        "parameters": "parameters",
        "resource_type": "resourceType",
        "retry_attempt_seconds": "retryAttemptSeconds",
        "target_version": "targetVersion",
    },
)
class CfnRemediationConfigurationProps:
    def __init__(
        self,
        *,
        config_rule_name: builtins.str,
        target_id: builtins.str,
        target_type: builtins.str,
        automatic: typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]] = None,
        execution_controls: typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnRemediationConfiguration.ExecutionControlsProperty]] = None,
        maximum_automatic_attempts: typing.Optional[jsii.Number] = None,
        parameters: typing.Any = None,
        resource_type: typing.Optional[builtins.str] = None,
        retry_attempt_seconds: typing.Optional[jsii.Number] = None,
        target_version: typing.Optional[builtins.str] = None,
    ) -> None:
        """Properties for defining a ``AWS::Config::RemediationConfiguration``.

        :param config_rule_name: ``AWS::Config::RemediationConfiguration.ConfigRuleName``.
        :param target_id: ``AWS::Config::RemediationConfiguration.TargetId``.
        :param target_type: ``AWS::Config::RemediationConfiguration.TargetType``.
        :param automatic: ``AWS::Config::RemediationConfiguration.Automatic``.
        :param execution_controls: ``AWS::Config::RemediationConfiguration.ExecutionControls``.
        :param maximum_automatic_attempts: ``AWS::Config::RemediationConfiguration.MaximumAutomaticAttempts``.
        :param parameters: ``AWS::Config::RemediationConfiguration.Parameters``.
        :param resource_type: ``AWS::Config::RemediationConfiguration.ResourceType``.
        :param retry_attempt_seconds: ``AWS::Config::RemediationConfiguration.RetryAttemptSeconds``.
        :param target_version: ``AWS::Config::RemediationConfiguration.TargetVersion``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html
        """
        self._values: typing.Dict[str, typing.Any] = {
            "config_rule_name": config_rule_name,
            "target_id": target_id,
            "target_type": target_type,
        }
        if automatic is not None:
            self._values["automatic"] = automatic
        if execution_controls is not None:
            self._values["execution_controls"] = execution_controls
        if maximum_automatic_attempts is not None:
            self._values["maximum_automatic_attempts"] = maximum_automatic_attempts
        if parameters is not None:
            self._values["parameters"] = parameters
        if resource_type is not None:
            self._values["resource_type"] = resource_type
        if retry_attempt_seconds is not None:
            self._values["retry_attempt_seconds"] = retry_attempt_seconds
        if target_version is not None:
            self._values["target_version"] = target_version

    @builtins.property
    def config_rule_name(self) -> builtins.str:
        """``AWS::Config::RemediationConfiguration.ConfigRuleName``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-configrulename
        """
        result = self._values.get("config_rule_name")
        assert result is not None, "Required property 'config_rule_name' is missing"
        return result

    @builtins.property
    def target_id(self) -> builtins.str:
        """``AWS::Config::RemediationConfiguration.TargetId``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-targetid
        """
        result = self._values.get("target_id")
        assert result is not None, "Required property 'target_id' is missing"
        return result

    @builtins.property
    def target_type(self) -> builtins.str:
        """``AWS::Config::RemediationConfiguration.TargetType``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-targettype
        """
        result = self._values.get("target_type")
        assert result is not None, "Required property 'target_type' is missing"
        return result

    @builtins.property
    def automatic(
        self,
    ) -> typing.Optional[typing.Union[builtins.bool, aws_cdk.core.IResolvable]]:
        """``AWS::Config::RemediationConfiguration.Automatic``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-automatic
        """
        result = self._values.get("automatic")
        return result

    @builtins.property
    def execution_controls(
        self,
    ) -> typing.Optional[typing.Union[aws_cdk.core.IResolvable, CfnRemediationConfiguration.ExecutionControlsProperty]]:
        """``AWS::Config::RemediationConfiguration.ExecutionControls``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-executioncontrols
        """
        result = self._values.get("execution_controls")
        return result

    @builtins.property
    def maximum_automatic_attempts(self) -> typing.Optional[jsii.Number]:
        """``AWS::Config::RemediationConfiguration.MaximumAutomaticAttempts``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-maximumautomaticattempts
        """
        result = self._values.get("maximum_automatic_attempts")
        return result

    @builtins.property
    def parameters(self) -> typing.Any:
        """``AWS::Config::RemediationConfiguration.Parameters``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-parameters
        """
        result = self._values.get("parameters")
        return result

    @builtins.property
    def resource_type(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::RemediationConfiguration.ResourceType``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-resourcetype
        """
        result = self._values.get("resource_type")
        return result

    @builtins.property
    def retry_attempt_seconds(self) -> typing.Optional[jsii.Number]:
        """``AWS::Config::RemediationConfiguration.RetryAttemptSeconds``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-retryattemptseconds
        """
        result = self._values.get("retry_attempt_seconds")
        return result

    @builtins.property
    def target_version(self) -> typing.Optional[builtins.str]:
        """``AWS::Config::RemediationConfiguration.TargetVersion``.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-config-remediationconfiguration.html#cfn-config-remediationconfiguration-targetversion
        """
        result = self._values.get("target_version")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CfnRemediationConfigurationProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.interface(jsii_type="@aws-cdk/aws-config.IRule")
class IRule(aws_cdk.core.IResource, typing_extensions.Protocol):
    """(experimental) A config rule.

    :stability: experimental
    """

    @builtins.staticmethod
    def __jsii_proxy_class__():
        return _IRuleProxy

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> builtins.str:
        """(experimental) The name of the rule.

        :stability: experimental
        :attribute: true
        """
        ...

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule compliance events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        ...

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        ...

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        ...


class _IRuleProxy(
    jsii.proxy_for(aws_cdk.core.IResource) # type: ignore
):
    """(experimental) A config rule.

    :stability: experimental
    """

    __jsii_type__: typing.ClassVar[str] = "@aws-cdk/aws-config.IRule"

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> builtins.str:
        """(experimental) The name of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleName")

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule compliance events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onComplianceChange", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onReEvaluationStatus", [id, options])


@jsii.implements(IRule)
class ManagedRule(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.ManagedRule",
):
    """(experimental) A new managed rule.

    :stability: experimental
    :resource: AWS::Config::ConfigRule
    """

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        identifier: builtins.str,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional["MaximumExecutionFrequency"] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param identifier: (experimental) The identifier of the AWS managed rule.
        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        props = ManagedRuleProps(
            identifier=identifier,
            config_rule_name=config_rule_name,
            description=description,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
        )

        jsii.create(ManagedRule, self, [scope, id, props])

    @jsii.member(jsii_name="fromConfigRuleName")
    @builtins.classmethod
    def from_config_rule_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        config_rule_name: builtins.str,
    ) -> IRule:
        """(experimental) Imports an existing rule.

        :param scope: -
        :param id: -
        :param config_rule_name: the name of the rule.

        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromConfigRuleName", [scope, id, config_rule_name])

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule compliance events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onComplianceChange", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onReEvaluationStatus", [id, options])

    @jsii.member(jsii_name="scopeToResource")
    def scope_to_resource(
        self,
        type: builtins.str,
        identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        """(experimental) Restrict scope of changes to a specific resource.

        :param type: the resource type.
        :param identifier: the resource identifier.

        :see: https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        :stability: experimental
        """
        return jsii.invoke(self, "scopeToResource", [type, identifier])

    @jsii.member(jsii_name="scopeToResources")
    def scope_to_resources(self, *types: builtins.str) -> None:
        """(experimental) Restrict scope of changes to specific resource types.

        :param types: resource types.

        :see: https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        :stability: experimental
        """
        return jsii.invoke(self, "scopeToResources", [*types])

    @jsii.member(jsii_name="scopeToTag")
    def scope_to_tag(
        self,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        """(experimental) Restrict scope of changes to a specific tag.

        :param key: the tag key.
        :param value: the tag value.

        :stability: experimental
        """
        return jsii.invoke(self, "scopeToTag", [key, value])

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleArn")
    def config_rule_arn(self) -> builtins.str:
        """(experimental) The arn of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleArn")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleComplianceType")
    def config_rule_compliance_type(self) -> builtins.str:
        """(experimental) The compliance status of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleComplianceType")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleId")
    def config_rule_id(self) -> builtins.str:
        """(experimental) The id of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleId")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> builtins.str:
        """(experimental) The name of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleName")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="isCustomWithChanges")
    def _is_custom_with_changes(self) -> typing.Optional[builtins.bool]:
        """
        :stability: experimental
        """
        return jsii.get(self, "isCustomWithChanges")

    @_is_custom_with_changes.setter # type: ignore
    def _is_custom_with_changes(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "isCustomWithChanges", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="isManaged")
    def _is_managed(self) -> typing.Optional[builtins.bool]:
        """
        :stability: experimental
        """
        return jsii.get(self, "isManaged")

    @_is_managed.setter # type: ignore
    def _is_managed(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "isManaged", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="scope")
    def _scope(self) -> typing.Optional[CfnConfigRule.ScopeProperty]:
        """
        :stability: experimental
        """
        return jsii.get(self, "scope")

    @_scope.setter # type: ignore
    def _scope(self, value: typing.Optional[CfnConfigRule.ScopeProperty]) -> None:
        jsii.set(self, "scope", value)


@jsii.enum(jsii_type="@aws-cdk/aws-config.MaximumExecutionFrequency")
class MaximumExecutionFrequency(enum.Enum):
    """(experimental) The maximum frequency at which the AWS Config rule runs evaluations.

    :stability: experimental
    """

    ONE_HOUR = "ONE_HOUR"
    """(experimental) 1 hour.

    :stability: experimental
    """
    THREE_HOURS = "THREE_HOURS"
    """(experimental) 3 hours.

    :stability: experimental
    """
    SIX_HOURS = "SIX_HOURS"
    """(experimental) 6 hours.

    :stability: experimental
    """
    TWELVE_HOURS = "TWELVE_HOURS"
    """(experimental) 12 hours.

    :stability: experimental
    """
    TWENTY_FOUR_HOURS = "TWENTY_FOUR_HOURS"
    """(experimental) 24 hours.

    :stability: experimental
    """


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.RuleProps",
    jsii_struct_bases=[],
    name_mapping={
        "config_rule_name": "configRuleName",
        "description": "description",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
    },
)
class RuleProps:
    def __init__(
        self,
        *,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
    ) -> None:
        """(experimental) Construction properties for a new rule.

        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        self._values: typing.Dict[str, typing.Any] = {}
        if config_rule_name is not None:
            self._values["config_rule_name"] = config_rule_name
        if description is not None:
            self._values["description"] = description
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency

    @builtins.property
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """(experimental) A name for the AWS Config rule.

        :default: - CloudFormation generated name

        :stability: experimental
        """
        result = self._values.get("config_rule_name")
        return result

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        """(experimental) A description about this AWS Config rule.

        :default: - No description

        :stability: experimental
        """
        result = self._values.get("description")
        return result

    @builtins.property
    def input_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        """(experimental) Input parameter values that are passed to the AWS Config rule.

        :default: - No input parameters

        :stability: experimental
        """
        result = self._values.get("input_parameters")
        return result

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[MaximumExecutionFrequency]:
        """(experimental) The maximum frequency at which the AWS Config rule runs evaluations.

        :default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        result = self._values.get("maximum_execution_frequency")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "RuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class AccessKeysRotated(
    ManagedRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.AccessKeysRotated",
):
    """(experimental) Checks whether the active access keys are rotated within the number of days specified in ``maxAge``.

    :see: https://docs.aws.amazon.com/config/latest/developerguide/access-keys-rotated.html
    :stability: experimental
    :resource: AWS::Config::ConfigRule
    """

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        max_age: typing.Optional[aws_cdk.core.Duration] = None,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param max_age: (experimental) The maximum number of days within which the access keys must be rotated. Default: Duration.days(90)
        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        props = AccessKeysRotatedProps(
            max_age=max_age,
            config_rule_name=config_rule_name,
            description=description,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
        )

        jsii.create(AccessKeysRotated, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.AccessKeysRotatedProps",
    jsii_struct_bases=[RuleProps],
    name_mapping={
        "config_rule_name": "configRuleName",
        "description": "description",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "max_age": "maxAge",
    },
)
class AccessKeysRotatedProps(RuleProps):
    def __init__(
        self,
        *,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
        max_age: typing.Optional[aws_cdk.core.Duration] = None,
    ) -> None:
        """(experimental) Construction properties for a AccessKeysRotated.

        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS
        :param max_age: (experimental) The maximum number of days within which the access keys must be rotated. Default: Duration.days(90)

        :stability: experimental
        """
        self._values: typing.Dict[str, typing.Any] = {}
        if config_rule_name is not None:
            self._values["config_rule_name"] = config_rule_name
        if description is not None:
            self._values["description"] = description
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if max_age is not None:
            self._values["max_age"] = max_age

    @builtins.property
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """(experimental) A name for the AWS Config rule.

        :default: - CloudFormation generated name

        :stability: experimental
        """
        result = self._values.get("config_rule_name")
        return result

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        """(experimental) A description about this AWS Config rule.

        :default: - No description

        :stability: experimental
        """
        result = self._values.get("description")
        return result

    @builtins.property
    def input_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        """(experimental) Input parameter values that are passed to the AWS Config rule.

        :default: - No input parameters

        :stability: experimental
        """
        result = self._values.get("input_parameters")
        return result

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[MaximumExecutionFrequency]:
        """(experimental) The maximum frequency at which the AWS Config rule runs evaluations.

        :default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        result = self._values.get("maximum_execution_frequency")
        return result

    @builtins.property
    def max_age(self) -> typing.Optional[aws_cdk.core.Duration]:
        """(experimental) The maximum number of days within which the access keys must be rotated.

        :default: Duration.days(90)

        :stability: experimental
        """
        result = self._values.get("max_age")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AccessKeysRotatedProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudFormationStackDriftDetectionCheck(
    ManagedRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CloudFormationStackDriftDetectionCheck",
):
    """(experimental) Checks whether your CloudFormation stacks' actual configuration differs, or has drifted, from its expected configuration.

    :see: https://docs.aws.amazon.com/config/latest/developerguide/cloudformation-stack-drift-detection-check.html
    :stability: experimental
    :resource: AWS::Config::ConfigRule
    """

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        own_stack_only: typing.Optional[builtins.bool] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param own_stack_only: (experimental) Whether to check only the stack where this rule is deployed. Default: false
        :param role: (experimental) The IAM role to use for this rule. It must have permissions to detect drift for AWS CloudFormation stacks. Ensure to attach ``config.amazonaws.com`` trusted permissions and ``ReadOnlyAccess`` policy permissions. For specific policy permissions, refer to https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html. Default: - A role will be created
        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        props = CloudFormationStackDriftDetectionCheckProps(
            own_stack_only=own_stack_only,
            role=role,
            config_rule_name=config_rule_name,
            description=description,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
        )

        jsii.create(CloudFormationStackDriftDetectionCheck, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CloudFormationStackDriftDetectionCheckProps",
    jsii_struct_bases=[RuleProps],
    name_mapping={
        "config_rule_name": "configRuleName",
        "description": "description",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "own_stack_only": "ownStackOnly",
        "role": "role",
    },
)
class CloudFormationStackDriftDetectionCheckProps(RuleProps):
    def __init__(
        self,
        *,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
        own_stack_only: typing.Optional[builtins.bool] = None,
        role: typing.Optional[aws_cdk.aws_iam.IRole] = None,
    ) -> None:
        """(experimental) Construction properties for a CloudFormationStackDriftDetectionCheck.

        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS
        :param own_stack_only: (experimental) Whether to check only the stack where this rule is deployed. Default: false
        :param role: (experimental) The IAM role to use for this rule. It must have permissions to detect drift for AWS CloudFormation stacks. Ensure to attach ``config.amazonaws.com`` trusted permissions and ``ReadOnlyAccess`` policy permissions. For specific policy permissions, refer to https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html. Default: - A role will be created

        :stability: experimental
        """
        self._values: typing.Dict[str, typing.Any] = {}
        if config_rule_name is not None:
            self._values["config_rule_name"] = config_rule_name
        if description is not None:
            self._values["description"] = description
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if own_stack_only is not None:
            self._values["own_stack_only"] = own_stack_only
        if role is not None:
            self._values["role"] = role

    @builtins.property
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """(experimental) A name for the AWS Config rule.

        :default: - CloudFormation generated name

        :stability: experimental
        """
        result = self._values.get("config_rule_name")
        return result

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        """(experimental) A description about this AWS Config rule.

        :default: - No description

        :stability: experimental
        """
        result = self._values.get("description")
        return result

    @builtins.property
    def input_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        """(experimental) Input parameter values that are passed to the AWS Config rule.

        :default: - No input parameters

        :stability: experimental
        """
        result = self._values.get("input_parameters")
        return result

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[MaximumExecutionFrequency]:
        """(experimental) The maximum frequency at which the AWS Config rule runs evaluations.

        :default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        result = self._values.get("maximum_execution_frequency")
        return result

    @builtins.property
    def own_stack_only(self) -> typing.Optional[builtins.bool]:
        """(experimental) Whether to check only the stack where this rule is deployed.

        :default: false

        :stability: experimental
        """
        result = self._values.get("own_stack_only")
        return result

    @builtins.property
    def role(self) -> typing.Optional[aws_cdk.aws_iam.IRole]:
        """(experimental) The IAM role to use for this rule.

        It must have permissions to detect drift
        for AWS CloudFormation stacks. Ensure to attach ``config.amazonaws.com`` trusted
        permissions and ``ReadOnlyAccess`` policy permissions. For specific policy permissions,
        refer to https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/using-cfn-stack-drift.html.

        :default: - A role will be created

        :stability: experimental
        """
        result = self._values.get("role")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationStackDriftDetectionCheckProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


class CloudFormationStackNotificationCheck(
    ManagedRule,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CloudFormationStackNotificationCheck",
):
    """(experimental) Checks whether your CloudFormation stacks are sending event notifications to a SNS topic.

    Optionally checks whether specified SNS topics are used.

    :see: https://docs.aws.amazon.com/config/latest/developerguide/cloudformation-stack-notification-check.html
    :stability: experimental
    :resource: AWS::Config::ConfigRule
    """

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        topics: typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]] = None,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param topics: (experimental) A list of allowed topics. At most 5 topics. Default: - No topics.
        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        props = CloudFormationStackNotificationCheckProps(
            topics=topics,
            config_rule_name=config_rule_name,
            description=description,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
        )

        jsii.create(CloudFormationStackNotificationCheck, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CloudFormationStackNotificationCheckProps",
    jsii_struct_bases=[RuleProps],
    name_mapping={
        "config_rule_name": "configRuleName",
        "description": "description",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "topics": "topics",
    },
)
class CloudFormationStackNotificationCheckProps(RuleProps):
    def __init__(
        self,
        *,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
        topics: typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]] = None,
    ) -> None:
        """(experimental) Construction properties for a CloudFormationStackNotificationCheck.

        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS
        :param topics: (experimental) A list of allowed topics. At most 5 topics. Default: - No topics.

        :stability: experimental
        """
        self._values: typing.Dict[str, typing.Any] = {}
        if config_rule_name is not None:
            self._values["config_rule_name"] = config_rule_name
        if description is not None:
            self._values["description"] = description
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if topics is not None:
            self._values["topics"] = topics

    @builtins.property
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """(experimental) A name for the AWS Config rule.

        :default: - CloudFormation generated name

        :stability: experimental
        """
        result = self._values.get("config_rule_name")
        return result

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        """(experimental) A description about this AWS Config rule.

        :default: - No description

        :stability: experimental
        """
        result = self._values.get("description")
        return result

    @builtins.property
    def input_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        """(experimental) Input parameter values that are passed to the AWS Config rule.

        :default: - No input parameters

        :stability: experimental
        """
        result = self._values.get("input_parameters")
        return result

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[MaximumExecutionFrequency]:
        """(experimental) The maximum frequency at which the AWS Config rule runs evaluations.

        :default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        result = self._values.get("maximum_execution_frequency")
        return result

    @builtins.property
    def topics(self) -> typing.Optional[typing.List[aws_cdk.aws_sns.ITopic]]:
        """(experimental) A list of allowed topics.

        At most 5 topics.

        :default: - No topics.

        :stability: experimental
        """
        result = self._values.get("topics")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CloudFormationStackNotificationCheckProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.implements(IRule)
class CustomRule(
    aws_cdk.core.Resource,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-cdk/aws-config.CustomRule",
):
    """(experimental) A new custom rule.

    :stability: experimental
    :resource: AWS::Config::ConfigRule
    """

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        lambda_function: aws_cdk.aws_lambda.IFunction,
        configuration_changes: typing.Optional[builtins.bool] = None,
        periodic: typing.Optional[builtins.bool] = None,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param lambda_function: (experimental) The Lambda function to run.
        :param configuration_changes: (experimental) Whether to run the rule on configuration changes. Default: false
        :param periodic: (experimental) Whether to run the rule on a fixed frequency. Default: false
        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        props = CustomRuleProps(
            lambda_function=lambda_function,
            configuration_changes=configuration_changes,
            periodic=periodic,
            config_rule_name=config_rule_name,
            description=description,
            input_parameters=input_parameters,
            maximum_execution_frequency=maximum_execution_frequency,
        )

        jsii.create(CustomRule, self, [scope, id, props])

    @jsii.member(jsii_name="fromConfigRuleName")
    @builtins.classmethod
    def from_config_rule_name(
        cls,
        scope: constructs.Construct,
        id: builtins.str,
        config_rule_name: builtins.str,
    ) -> IRule:
        """(experimental) Imports an existing rule.

        :param scope: -
        :param id: -
        :param config_rule_name: the name of the rule.

        :stability: experimental
        """
        return jsii.sinvoke(cls, "fromConfigRuleName", [scope, id, config_rule_name])

    @jsii.member(jsii_name="onComplianceChange")
    def on_compliance_change(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule compliance events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onComplianceChange", [id, options])

    @jsii.member(jsii_name="onEvent")
    def on_event(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule events.

        Use
        ``rule.addEventPattern(pattern)`` to specify a filter.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onEvent", [id, options])

    @jsii.member(jsii_name="onReEvaluationStatus")
    def on_re_evaluation_status(
        self,
        id: builtins.str,
        *,
        description: typing.Optional[builtins.str] = None,
        event_pattern: typing.Optional[aws_cdk.aws_events.EventPattern] = None,
        rule_name: typing.Optional[builtins.str] = None,
        target: typing.Optional[aws_cdk.aws_events.IRuleTarget] = None,
    ) -> aws_cdk.aws_events.Rule:
        """(experimental) Defines a CloudWatch event rule which triggers for rule re-evaluation status events.

        :param id: -
        :param description: A description of the rule's purpose. Default: - No description
        :param event_pattern: Additional restrictions for the event to route to the specified target. The method that generates the rule probably imposes some type of event filtering. The filtering implied by what you pass here is added on top of that filtering. Default: - No additional filtering based on an event pattern.
        :param rule_name: A name for the rule. Default: AWS CloudFormation generates a unique physical ID.
        :param target: The target to register for the event. Default: - No target is added to the rule. Use ``addTarget()`` to add a target.

        :stability: experimental
        """
        options = aws_cdk.aws_events.OnEventOptions(
            description=description,
            event_pattern=event_pattern,
            rule_name=rule_name,
            target=target,
        )

        return jsii.invoke(self, "onReEvaluationStatus", [id, options])

    @jsii.member(jsii_name="scopeToResource")
    def scope_to_resource(
        self,
        type: builtins.str,
        identifier: typing.Optional[builtins.str] = None,
    ) -> None:
        """(experimental) Restrict scope of changes to a specific resource.

        :param type: the resource type.
        :param identifier: the resource identifier.

        :see: https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        :stability: experimental
        """
        return jsii.invoke(self, "scopeToResource", [type, identifier])

    @jsii.member(jsii_name="scopeToResources")
    def scope_to_resources(self, *types: builtins.str) -> None:
        """(experimental) Restrict scope of changes to specific resource types.

        :param types: resource types.

        :see: https://docs.aws.amazon.com/config/latest/developerguide/resource-config-reference.html#supported-resources
        :stability: experimental
        """
        return jsii.invoke(self, "scopeToResources", [*types])

    @jsii.member(jsii_name="scopeToTag")
    def scope_to_tag(
        self,
        key: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        """(experimental) Restrict scope of changes to a specific tag.

        :param key: the tag key.
        :param value: the tag value.

        :stability: experimental
        """
        return jsii.invoke(self, "scopeToTag", [key, value])

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleArn")
    def config_rule_arn(self) -> builtins.str:
        """(experimental) The arn of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleArn")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleComplianceType")
    def config_rule_compliance_type(self) -> builtins.str:
        """(experimental) The compliance status of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleComplianceType")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleId")
    def config_rule_id(self) -> builtins.str:
        """(experimental) The id of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleId")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="configRuleName")
    def config_rule_name(self) -> builtins.str:
        """(experimental) The name of the rule.

        :stability: experimental
        :attribute: true
        """
        return jsii.get(self, "configRuleName")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="isCustomWithChanges")
    def _is_custom_with_changes(self) -> typing.Optional[builtins.bool]:
        """
        :stability: experimental
        """
        return jsii.get(self, "isCustomWithChanges")

    @_is_custom_with_changes.setter # type: ignore
    def _is_custom_with_changes(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "isCustomWithChanges", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="isManaged")
    def _is_managed(self) -> typing.Optional[builtins.bool]:
        """
        :stability: experimental
        """
        return jsii.get(self, "isManaged")

    @_is_managed.setter # type: ignore
    def _is_managed(self, value: typing.Optional[builtins.bool]) -> None:
        jsii.set(self, "isManaged", value)

    @builtins.property # type: ignore
    @jsii.member(jsii_name="scope")
    def _scope(self) -> typing.Optional[CfnConfigRule.ScopeProperty]:
        """
        :stability: experimental
        """
        return jsii.get(self, "scope")

    @_scope.setter # type: ignore
    def _scope(self, value: typing.Optional[CfnConfigRule.ScopeProperty]) -> None:
        jsii.set(self, "scope", value)


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.CustomRuleProps",
    jsii_struct_bases=[RuleProps],
    name_mapping={
        "config_rule_name": "configRuleName",
        "description": "description",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "lambda_function": "lambdaFunction",
        "configuration_changes": "configurationChanges",
        "periodic": "periodic",
    },
)
class CustomRuleProps(RuleProps):
    def __init__(
        self,
        *,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
        lambda_function: aws_cdk.aws_lambda.IFunction,
        configuration_changes: typing.Optional[builtins.bool] = None,
        periodic: typing.Optional[builtins.bool] = None,
    ) -> None:
        """(experimental) Construction properties for a CustomRule.

        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS
        :param lambda_function: (experimental) The Lambda function to run.
        :param configuration_changes: (experimental) Whether to run the rule on configuration changes. Default: false
        :param periodic: (experimental) Whether to run the rule on a fixed frequency. Default: false

        :stability: experimental
        """
        self._values: typing.Dict[str, typing.Any] = {
            "lambda_function": lambda_function,
        }
        if config_rule_name is not None:
            self._values["config_rule_name"] = config_rule_name
        if description is not None:
            self._values["description"] = description
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency
        if configuration_changes is not None:
            self._values["configuration_changes"] = configuration_changes
        if periodic is not None:
            self._values["periodic"] = periodic

    @builtins.property
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """(experimental) A name for the AWS Config rule.

        :default: - CloudFormation generated name

        :stability: experimental
        """
        result = self._values.get("config_rule_name")
        return result

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        """(experimental) A description about this AWS Config rule.

        :default: - No description

        :stability: experimental
        """
        result = self._values.get("description")
        return result

    @builtins.property
    def input_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        """(experimental) Input parameter values that are passed to the AWS Config rule.

        :default: - No input parameters

        :stability: experimental
        """
        result = self._values.get("input_parameters")
        return result

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[MaximumExecutionFrequency]:
        """(experimental) The maximum frequency at which the AWS Config rule runs evaluations.

        :default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        result = self._values.get("maximum_execution_frequency")
        return result

    @builtins.property
    def lambda_function(self) -> aws_cdk.aws_lambda.IFunction:
        """(experimental) The Lambda function to run.

        :stability: experimental
        """
        result = self._values.get("lambda_function")
        assert result is not None, "Required property 'lambda_function' is missing"
        return result

    @builtins.property
    def configuration_changes(self) -> typing.Optional[builtins.bool]:
        """(experimental) Whether to run the rule on configuration changes.

        :default: false

        :stability: experimental
        """
        result = self._values.get("configuration_changes")
        return result

    @builtins.property
    def periodic(self) -> typing.Optional[builtins.bool]:
        """(experimental) Whether to run the rule on a fixed frequency.

        :default: false

        :stability: experimental
        """
        result = self._values.get("periodic")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "CustomRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="@aws-cdk/aws-config.ManagedRuleProps",
    jsii_struct_bases=[RuleProps],
    name_mapping={
        "config_rule_name": "configRuleName",
        "description": "description",
        "input_parameters": "inputParameters",
        "maximum_execution_frequency": "maximumExecutionFrequency",
        "identifier": "identifier",
    },
)
class ManagedRuleProps(RuleProps):
    def __init__(
        self,
        *,
        config_rule_name: typing.Optional[builtins.str] = None,
        description: typing.Optional[builtins.str] = None,
        input_parameters: typing.Optional[typing.Mapping[builtins.str, typing.Any]] = None,
        maximum_execution_frequency: typing.Optional[MaximumExecutionFrequency] = None,
        identifier: builtins.str,
    ) -> None:
        """(experimental) Construction properties for a ManagedRule.

        :param config_rule_name: (experimental) A name for the AWS Config rule. Default: - CloudFormation generated name
        :param description: (experimental) A description about this AWS Config rule. Default: - No description
        :param input_parameters: (experimental) Input parameter values that are passed to the AWS Config rule. Default: - No input parameters
        :param maximum_execution_frequency: (experimental) The maximum frequency at which the AWS Config rule runs evaluations. Default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS
        :param identifier: (experimental) The identifier of the AWS managed rule.

        :stability: experimental
        """
        self._values: typing.Dict[str, typing.Any] = {
            "identifier": identifier,
        }
        if config_rule_name is not None:
            self._values["config_rule_name"] = config_rule_name
        if description is not None:
            self._values["description"] = description
        if input_parameters is not None:
            self._values["input_parameters"] = input_parameters
        if maximum_execution_frequency is not None:
            self._values["maximum_execution_frequency"] = maximum_execution_frequency

    @builtins.property
    def config_rule_name(self) -> typing.Optional[builtins.str]:
        """(experimental) A name for the AWS Config rule.

        :default: - CloudFormation generated name

        :stability: experimental
        """
        result = self._values.get("config_rule_name")
        return result

    @builtins.property
    def description(self) -> typing.Optional[builtins.str]:
        """(experimental) A description about this AWS Config rule.

        :default: - No description

        :stability: experimental
        """
        result = self._values.get("description")
        return result

    @builtins.property
    def input_parameters(
        self,
    ) -> typing.Optional[typing.Mapping[builtins.str, typing.Any]]:
        """(experimental) Input parameter values that are passed to the AWS Config rule.

        :default: - No input parameters

        :stability: experimental
        """
        result = self._values.get("input_parameters")
        return result

    @builtins.property
    def maximum_execution_frequency(self) -> typing.Optional[MaximumExecutionFrequency]:
        """(experimental) The maximum frequency at which the AWS Config rule runs evaluations.

        :default: MaximumExecutionFrequency.TWENTY_FOUR_HOURS

        :stability: experimental
        """
        result = self._values.get("maximum_execution_frequency")
        return result

    @builtins.property
    def identifier(self) -> builtins.str:
        """(experimental) The identifier of the AWS managed rule.

        :see: https://docs.aws.amazon.com/config/latest/developerguide/managed-rules-by-aws-config.html
        :stability: experimental
        """
        result = self._values.get("identifier")
        assert result is not None, "Required property 'identifier' is missing"
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "ManagedRuleProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AccessKeysRotated",
    "AccessKeysRotatedProps",
    "CfnAggregationAuthorization",
    "CfnAggregationAuthorizationProps",
    "CfnConfigRule",
    "CfnConfigRuleProps",
    "CfnConfigurationAggregator",
    "CfnConfigurationAggregatorProps",
    "CfnConfigurationRecorder",
    "CfnConfigurationRecorderProps",
    "CfnConformancePack",
    "CfnConformancePackProps",
    "CfnDeliveryChannel",
    "CfnDeliveryChannelProps",
    "CfnOrganizationConfigRule",
    "CfnOrganizationConfigRuleProps",
    "CfnOrganizationConformancePack",
    "CfnOrganizationConformancePackProps",
    "CfnRemediationConfiguration",
    "CfnRemediationConfigurationProps",
    "CloudFormationStackDriftDetectionCheck",
    "CloudFormationStackDriftDetectionCheckProps",
    "CloudFormationStackNotificationCheck",
    "CloudFormationStackNotificationCheckProps",
    "CustomRule",
    "CustomRuleProps",
    "IRule",
    "ManagedRule",
    "ManagedRuleProps",
    "MaximumExecutionFrequency",
    "RuleProps",
]

publication.publish()
