"""
# aws-kinesisstreams-lambda module

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
|![Python Logo](https://docs.aws.amazon.com/cdk/api/latest/img/python32.png) Python|`aws_solutions_constructs.aws_kinesisstreams_lambda`|
|![Typescript Logo](https://docs.aws.amazon.com/cdk/api/latest/img/typescript32.png) Typescript|`@aws-solutions-constructs/aws-kinesisstreams-lambda`|
|![Java Logo](https://docs.aws.amazon.com/cdk/api/latest/img/java32.png) Java|`software.amazon.awsconstructs.services.kinesisstreamslambda`|

This AWS Solutions Construct deploys a Kinesis Stream and Lambda function with the appropriate resources/properties for interaction and security.

Here is a minimal deployable pattern definition:

```javascript
const { KinesisStreamsToLambda } = require('@aws-solutions-constructs/aws-kinesisstreams-lambda');

new KinesisStreamsToLambda(stack, 'KinesisToLambdaPattern', {
    eventSourceProps: {
        startingPosition: lambda.StartingPosition.TRIM_HORIZON,
        batchSize: 1
    },
    lambdaFunctionProps: {
        runtime: lambda.Runtime.NODEJS_10_X,
        handler: 'index.handler',
        code: lambda.Code.fromAsset(`${__dirname}/lambda`)
    }
});

```

## Initializer

```text
new KinesisStreamsToLambda(scope: Construct, id: string, props: KinesisStreamsToLambdaProps);
```

*Parameters*

* scope [`Construct`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_core.Construct.html)
* id `string`
* props [`KinesisStreamsToLambdaProps`](#pattern-construct-props)

## Pattern Construct Props

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|existingLambdaObj?|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored.|
|lambdaFunctionProps?|[`lambda.FunctionProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.FunctionProps.html)|User provided props to override the default props for the Lambda function.|
|kinesisStreamProps?|[`kinesis.StreamProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.StreamProps.html)|Optional user-provided props to override the default props for the Kinesis stream.|
|existingStreamObj?|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)|Existing instance of Kinesis Stream, if this is set then kinesisStreamProps is ignored.|
|kinesisEventSourceProps?|[`aws-lambda-event-sources.KinesisEventSourceProps`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda-event-sources.KinesisEventSourceProps.html)|Optional user-provided props to override the default props for the Lambda event source mapping.|

## Pattern Properties

| **Name**     | **Type**        | **Description** |
|:-------------|:----------------|-----------------|
|kinesisStream|[`kinesis.Stream`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-kinesis.Stream.html)|Returns an instance of the Kinesis stream created by the pattern.|
|lambdaFunction|[`lambda.Function`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-lambda.Function.html)|Returns an instance of the Lambda function created by the pattern.|
|kinesisStreamRole|[`iam.Role`](https://docs.aws.amazon.com/cdk/api/latest/docs/@aws-cdk_aws-iam.Role.html)|Returns an instance of the iam.Role created by the construct for Kinesis stream.|

## Default settings

Out of the box implementation of the Construct without any override will set the following defaults:

### Amazon Kinesis Stream

* Configure least privilege access IAM role for Kinesis Stream
* Enable server-side encryption for Kinesis Stream using AWS Managed KMS Key

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

import aws_cdk.aws_iam
import aws_cdk.aws_kinesis
import aws_cdk.aws_lambda
import aws_cdk.aws_lambda_event_sources
import aws_cdk.core


class KinesisStreamsToLambda(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@aws-solutions-constructs/aws-kinesisstreams-lambda.KinesisStreamsToLambda",
):
    """
    :summary: The KinesisStreamsToLambda class.
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        kinesis_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.KinesisEventSourceProps] = None,
        kinesis_stream_props: typing.Optional[aws_cdk.aws_kinesis.StreamProps] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
    ) -> None:
        """
        :param scope: - represents the scope for all the resources.
        :param id: - this is a a scope-unique id.
        :param existing_lambda_obj: Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param existing_stream_obj: Existing instance of Kinesis Stream, if this is set then kinesisStreamProps is ignored. Default: - None
        :param kinesis_event_source_props: Optional user-provided props to override the default props for the Lambda event source mapping. Default: - Default props are used.
        :param kinesis_stream_props: Optional user-provided props to override the default props for the Kinesis stream. Default: - Default props are used.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used.

        :access: public
        :since: 0.8.0
        :summary: Constructs a new instance of the KinesisStreamsToLambda class.
        """
        props = KinesisStreamsToLambdaProps(
            existing_lambda_obj=existing_lambda_obj,
            existing_stream_obj=existing_stream_obj,
            kinesis_event_source_props=kinesis_event_source_props,
            kinesis_stream_props=kinesis_stream_props,
            lambda_function_props=lambda_function_props,
        )

        jsii.create(KinesisStreamsToLambda, self, [scope, id, props])

    @builtins.property # type: ignore
    @jsii.member(jsii_name="kinesisStream")
    def kinesis_stream(self) -> aws_cdk.aws_kinesis.Stream:
        return jsii.get(self, "kinesisStream")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="kinesisStreamRole")
    def kinesis_stream_role(self) -> aws_cdk.aws_iam.Role:
        return jsii.get(self, "kinesisStreamRole")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="lambdaFunction")
    def lambda_function(self) -> aws_cdk.aws_lambda.Function:
        return jsii.get(self, "lambdaFunction")


@jsii.data_type(
    jsii_type="@aws-solutions-constructs/aws-kinesisstreams-lambda.KinesisStreamsToLambdaProps",
    jsii_struct_bases=[],
    name_mapping={
        "existing_lambda_obj": "existingLambdaObj",
        "existing_stream_obj": "existingStreamObj",
        "kinesis_event_source_props": "kinesisEventSourceProps",
        "kinesis_stream_props": "kinesisStreamProps",
        "lambda_function_props": "lambdaFunctionProps",
    },
)
class KinesisStreamsToLambdaProps:
    def __init__(
        self,
        *,
        existing_lambda_obj: typing.Optional[aws_cdk.aws_lambda.Function] = None,
        existing_stream_obj: typing.Optional[aws_cdk.aws_kinesis.Stream] = None,
        kinesis_event_source_props: typing.Optional[aws_cdk.aws_lambda_event_sources.KinesisEventSourceProps] = None,
        kinesis_stream_props: typing.Optional[aws_cdk.aws_kinesis.StreamProps] = None,
        lambda_function_props: typing.Optional[aws_cdk.aws_lambda.FunctionProps] = None,
    ) -> None:
        """The properties for the KinesisStreamsToLambda class.

        :param existing_lambda_obj: Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored. Default: - None
        :param existing_stream_obj: Existing instance of Kinesis Stream, if this is set then kinesisStreamProps is ignored. Default: - None
        :param kinesis_event_source_props: Optional user-provided props to override the default props for the Lambda event source mapping. Default: - Default props are used.
        :param kinesis_stream_props: Optional user-provided props to override the default props for the Kinesis stream. Default: - Default props are used.
        :param lambda_function_props: User provided props to override the default props for the Lambda function. Default: - Default props are used.
        """
        if isinstance(kinesis_event_source_props, dict):
            kinesis_event_source_props = aws_cdk.aws_lambda_event_sources.KinesisEventSourceProps(**kinesis_event_source_props)
        if isinstance(kinesis_stream_props, dict):
            kinesis_stream_props = aws_cdk.aws_kinesis.StreamProps(**kinesis_stream_props)
        if isinstance(lambda_function_props, dict):
            lambda_function_props = aws_cdk.aws_lambda.FunctionProps(**lambda_function_props)
        self._values: typing.Dict[str, typing.Any] = {}
        if existing_lambda_obj is not None:
            self._values["existing_lambda_obj"] = existing_lambda_obj
        if existing_stream_obj is not None:
            self._values["existing_stream_obj"] = existing_stream_obj
        if kinesis_event_source_props is not None:
            self._values["kinesis_event_source_props"] = kinesis_event_source_props
        if kinesis_stream_props is not None:
            self._values["kinesis_stream_props"] = kinesis_stream_props
        if lambda_function_props is not None:
            self._values["lambda_function_props"] = lambda_function_props

    @builtins.property
    def existing_lambda_obj(self) -> typing.Optional[aws_cdk.aws_lambda.Function]:
        """Existing instance of Lambda Function object, if this is set then the lambdaFunctionProps is ignored.

        :default: - None
        """
        result = self._values.get("existing_lambda_obj")
        return result

    @builtins.property
    def existing_stream_obj(self) -> typing.Optional[aws_cdk.aws_kinesis.Stream]:
        """Existing instance of Kinesis Stream, if this is set then kinesisStreamProps is ignored.

        :default: - None
        """
        result = self._values.get("existing_stream_obj")
        return result

    @builtins.property
    def kinesis_event_source_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda_event_sources.KinesisEventSourceProps]:
        """Optional user-provided props to override the default props for the Lambda event source mapping.

        :default: - Default props are used.
        """
        result = self._values.get("kinesis_event_source_props")
        return result

    @builtins.property
    def kinesis_stream_props(self) -> typing.Optional[aws_cdk.aws_kinesis.StreamProps]:
        """Optional user-provided props to override the default props for the Kinesis stream.

        :default: - Default props are used.
        """
        result = self._values.get("kinesis_stream_props")
        return result

    @builtins.property
    def lambda_function_props(
        self,
    ) -> typing.Optional[aws_cdk.aws_lambda.FunctionProps]:
        """User provided props to override the default props for the Lambda function.

        :default: - Default props are used.
        """
        result = self._values.get("lambda_function_props")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "KinesisStreamsToLambdaProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "KinesisStreamsToLambda",
    "KinesisStreamsToLambdaProps",
]

publication.publish()
