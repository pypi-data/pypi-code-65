"""
# aws-dynamodb-stream-lambda module

<!--BEGIN STABILITY BANNER-->---


![Stability: Experimental](https://img.shields.io/badge/stability-Experimental-important.svg?style=for-the-badge)

> All classes are under active development and subject to non-backward compatible changes or removal in any
> future version. These are not subject to the [Semantic Versioning](https://semver.org/) model.
> This means that while you may use them, you may need to update your source code when upgrading to a newer version of this package.

---
<!--END STABILITY BANNER-->

| **Reference Documentation**:| <span style="font-weight: normal">https://docs.aws.amazon.com/solutions/latest/constructs/</span>|
|:-------------|:-------------|

<div style="height:8px"></div>

| **Language**     | **Package**        |
|:-------------|-----------------|
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_dynamodb_stream_lambda`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-dynamodb-stream-lambda`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.dynamodbstreamlambda`|

This AWS Solutions Construct implements a pattern Amazon DynamoDB table with stream to invoke the AWS Lambda function  with the least privileged permissions.

Here is a minimal deployable pattern definition in Typescript:

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from aws_solutions_constructs.aws_dynamodb_stream_lambda import DynamoDBStreamToLambdaProps, DynamoDBStreamToLambda

DynamoDBStreamToLambda(self, "test-dynamodb-stream-lambda",
    lambda_function_props=FunctionProps(
        code=lambda_.Code.from_asset(f"{__dirname}/lambda"),
        runtime=lambda_.Runtime.NODEJS_12_X,
        handler="index.handler"
    )
)
```

## Initializer

```text
new DynamoDBStreamToLambda(scope: Construct, id: string, props: DynamoDBStreamToLambdaProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`DynamoDBStreamToLambdaProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|dynamoTableProps?|[`dynamodb.TableProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.TableProps.html)|Optional user provided props to override the default props for DynamoDB Table|
|existingTableObj?|[`dynamodb.Table`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.Table.html)|Existing instance of DynamoDB table object, If this is set then the dynamoTableProps is ignored|
|dynamoEventSourceProps?|[`aws-lambda-event-sources.DynamoEventSourceProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda-event-sources.DynamoEventSourceProps.html)|Optional user provided props to override the default props for DynamoDB Event Source|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|dynamoTable|[`dynamodb.Table`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-dynamodb.Table.html)|Returns an instance of dynamodb.Table created by the construct|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of lambda.Function created by the construct|

## Lambda Function

This pattern requires a lambda function that can post data into the Elasticsearch. A sample function is provided [here](https://github.com/awslabs/aws-solutions-constructs/blob/master/source/patterns/%40aws-solutions-constructs/aws-dynamodb-stream-lambda-elasticsearch-kibana/test/lambda/index.js).

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon DynamoDB Table

* Set the billing mode for DynamoDB Table to On-Demand (Pay per request)
* Enable server-side encryption for DynamoDB Table using AWS managed KMS Key
* Creates a partition key called 'id' for DynamoDB Table
* Retain the Table when deleting the CloudFormation stack
* Enable continuous backups and point-in-time recovery

### AWS Lambda Function

* Configure least privilege access IAM role for Lambda function
* Enable reusing connections with Keep-Alive for NodeJs Lambda function
* Enable X-Ray Tracing

## Architecture

![Architecture Diagram](architecture.png)

---


© Copyright 2020 Amazon.com, Inc. or its affiliates. All Rights Reserved.
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

import aws_cdk.aws_dynamodb
import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_event_sources
import aws_cdk.core


class DynamoDBStreamToLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-dynamodb-stream-lambda.DynamoDBStreamToLambda",
):
    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        dynamo_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps] = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_table_obj: typing.Optional[aws_cdk.aws_dynamodb.Table] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
    ) -> None:
        """
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param dynamo_event_source_props: Optional user provided props to override the default props. Default: - Default props are used
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param existing_table_obj: Existing instance of DynamoDB table object, If this is set then the dynamoTableProps is ignored. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the LambdaToDynamoDB class.
        """
        props = DynamoDBStreamToLambdaProps(
            dynamo_event_source_props=dynamo_event_source_props,
            dynamo_table_props=dynamo_table_props,
            existing_lambda_obj=existing_lambda_obj,
            existing_table_obj=existing_table_obj,
            lambda_function_props=lambda_function_props,
        )

        jsii.create(DynamoDBStreamToLambda, self, [scope, id, props])

    @builtins.property # type: ignore
    @jsii.member(jsii_name="dynamoTable")
    def dynamo_table(self) -> aws_cdk.aws_dynamodb.Table:
        return jsii.get(self, "dynamoTable")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return jsii.get(self, "lambdaFunction")


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-dynamodb-stream-lambda.DynamoDBStreamToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "dynamo_event_source_props": "dynamoEventSourceProps",
        "dynamo_table_props": "dynamoTableProps",
        "existing_lambda_obj": "existingLambdaObj",
        "existing_table_obj": "existingTableObj",
        "lambda_function_props": "lambdaFunctionProps",
    },
)
class DynamoDBStreamToLambdaProps:
    def __init__(
        self,
        *,
        dynamo_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps] = None,
        dynamo_table_props: typing.Optional[aws_cdk.aws_dynamodb.TableProps] = None,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_table_obj: typing.Optional[aws_cdk.aws_dynamodb.Table] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
    ) -> None:
        """
        :param dynamo_event_source_props: Optional user provided props to override the default props. Default: - Default props are used
        :param dynamo_table_props: Optional user provided props to override the default props. Default: - Default props are used
        :param existing_lambda_obj: Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param existing_table_obj: Existing instance of DynamoDB table object, If this is set then the dynamoTableProps is ignored. Default: - None
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used

        :summary: The properties for the DynamoDBStreamToLambda Construct
        """
        if isinstance(dynamo_event_source_props, dict):
            dynamo_event_source_props = aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps(**dynamo_event_source_props)
        if isinstance(dynamo_table_props, dict):
            dynamo_table_props = aws_cdk.aws_dynamodb.TableProps(**dynamo_table_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if dynamo_event_source_props is not None:
            self._values["dynamo_event_source_props"] = dynamo_event_source_props
        if dynamo_table_props is not None:
            self._values["dynamo_table_props"] = dynamo_table_props
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_table_obj is not None:
            self._values["existing_table_obj"] = existing_table_obj
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props

    @builtins.property
    def dynamo_event_source_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda_event_sources.DynamoEventSourceProps]:
        """Optional user provided props to override the default props.

        :default: - Default props are used
        """
        result = self._values.get("dynamo_event_source_props")
        return result

    @builtins.property
    def dynamo_table_props(self) -> typing.Optional[aws_cdk.aws_dynamodb.TableProps]:
        """Optional user provided props to override the default props.

        :default: - Default props are used
        """
        result = self._values.get("dynamo_table_props")
        return result

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        """Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored.

        :default: - None
        """
        result = self._values.get("existing_lambda_obj")
        return result

    @builtins.property
    def existing_table_obj(self) -> typing.Optional[aws_cdk.aws_dynamodb.Table]:
        """Existing instance of DynamoDB table object, If this is set then the dynamoTableProps is ignored.

        :default: - None
        """
        result = self._values.get("existing_table_obj")
        return result

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        """User provided props to override the default props for the Lambda function.

        :default: - Default props are used
        """
        result = self._values.get("lambda_function_props")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "DynamoDBStreamToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "DynamoDBStreamToLambda",
    "DynamoDBStreamToLambdaProps",
]

publication.publish()
