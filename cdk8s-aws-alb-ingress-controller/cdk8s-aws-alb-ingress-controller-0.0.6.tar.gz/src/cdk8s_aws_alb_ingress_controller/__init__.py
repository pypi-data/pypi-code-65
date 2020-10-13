"""
[![NPM version](https://badge.fury.io/js/cdk8s-aws-alb-ingress-controller.svg)](https://badge.fury.io/js/cdk8s-aws-alb-ingress-controller)
[![PyPI version](https://badge.fury.io/py/cdk8s-aws-alb-ingress-controller.svg)](https://badge.fury.io/py/cdk8s-aws-alb-ingress-controller)
![Release](https://github.com/guan840912/cdk8s-aws-alb-ingress-controller/workflows/Release/badge.svg)

![Downloads](https://img.shields.io/badge/-DOWNLOADS:-brightgreen?color=gray)
![npm](https://img.shields.io/npm/dt/cdk8s-aws-alb-ingress-controller?label=npm&color=orange)
![PyPI](https://img.shields.io/pypi/dm/cdk8s-aws-alb-ingress-controller?label=pypi&color=blue)

# cdk8s-aws-alb-ingress-controller

> [aws alb ingress controller](https://github.com/kubernetes-sigs/aws-alb-ingress-controller) constructs for cdk8s

Basic implementation of a [aws alb ingress controller](https://github.com/kubernetes-sigs/aws-alb-ingress-controller) construct for cdk8s. Contributions are welcome!

## Usage

```python
# Example automatically generated without compilation. See https://github.com/aws/jsii/issues/826
from cdk8s import App, Chart
from constructs import Construct
from cdk8s_aws_alb_ingress_controller import AlbIngressController

class MyChart(Chart):
    def __init__(self, scope, name):
        super().__init__(scope, name)
        AlbIngressController(self, "albingresscntroller",
            cluster_name="EKScluster"
        )
app = App()
MyChart(app, "testcdk8s")
app.synth()
```

## License

Distributed under the [Apache 2.0](./LICENSE) license.
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

import constructs


class AlbIngressController(
    constructs.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="cdk8s-aws-alb-ingress-controller.AlbIngressController",
):
    """Generate alb-ingress-controller config yaml.

    see https://github.com/kubernetes-sigs/aws-alb-ingress-controller/blob/master/docs/examples
    """

    def __init__(
        self,
        scope: constructs.Construct,
        id: builtins.str,
        *,
        cluster_name: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.List["EnvVar"]] = None,
        image: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        replicas: typing.Optional[jsii.Number] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param cluster_name: Kubernetes Cluster Name for alb-ingress-controller. Default: - None
        :param args: Another Args for alb-ingress-controller. Default: - None
        :param env: Another Args for alb-ingress-controller. Default: - None
        :param image: Default image for alb-ingress-controller. Default: - docker.io/amazon/aws-alb-ingress-controller:v1.1.9
        :param labels: Extra labels to associate with resources. Default: - none
        :param namespace: Default Namespace for alb-ingress-controller. Default: - kube-system
        :param replicas: Replicas for alb-ingress-controller. Default: - 1
        :param service_account_name: Default Service Account Name for alb-ingress-controller. Default: - alb-ingress-controller
        """
        options = AlbIngressControllerOptions(
            cluster_name=cluster_name,
            args=args,
            env=env,
            image=image,
            labels=labels,
            namespace=namespace,
            replicas=replicas,
            service_account_name=service_account_name,
        )

        jsii.create(AlbIngressController, self, [scope, id, options])

    @builtins.property # type: ignore
    @jsii.member(jsii_name="clusterName")
    def cluster_name(self) -> builtins.str:
        """Kubernetes Cluster Name for alb-ingress-controller."""
        return jsii.get(self, "clusterName")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="deploymentName")
    def deployment_name(self) -> builtins.str:
        """Kubernetes Deployment Name for alb-ingress-controller."""
        return jsii.get(self, "deploymentName")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="namespace")
    def namespace(self) -> builtins.str:
        """Namespace for alb-ingress-controller.

        :default: - kube-system
        """
        return jsii.get(self, "namespace")

    @builtins.property # type: ignore
    @jsii.member(jsii_name="serviceAccountName")
    def service_account_name(self) -> builtins.str:
        """Service Account Name for alb-ingress-controller."""
        return jsii.get(self, "serviceAccountName")


@jsii.data_type(
    jsii_type="cdk8s-aws-alb-ingress-controller.AlbIngressControllerOptions",
    jsii_struct_bases=[],
    name_mapping={
        "cluster_name": "clusterName",
        "args": "args",
        "env": "env",
        "image": "image",
        "labels": "labels",
        "namespace": "namespace",
        "replicas": "replicas",
        "service_account_name": "serviceAccountName",
    },
)
class AlbIngressControllerOptions:
    def __init__(
        self,
        *,
        cluster_name: builtins.str,
        args: typing.Optional[typing.List[builtins.str]] = None,
        env: typing.Optional[typing.List["EnvVar"]] = None,
        image: typing.Optional[builtins.str] = None,
        labels: typing.Optional[typing.Mapping[builtins.str, builtins.str]] = None,
        namespace: typing.Optional[builtins.str] = None,
        replicas: typing.Optional[jsii.Number] = None,
        service_account_name: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param cluster_name: Kubernetes Cluster Name for alb-ingress-controller. Default: - None
        :param args: Another Args for alb-ingress-controller. Default: - None
        :param env: Another Args for alb-ingress-controller. Default: - None
        :param image: Default image for alb-ingress-controller. Default: - docker.io/amazon/aws-alb-ingress-controller:v1.1.9
        :param labels: Extra labels to associate with resources. Default: - none
        :param namespace: Default Namespace for alb-ingress-controller. Default: - kube-system
        :param replicas: Replicas for alb-ingress-controller. Default: - 1
        :param service_account_name: Default Service Account Name for alb-ingress-controller. Default: - alb-ingress-controller
        """
        self._values: typing.Dict[str, typing.Any] = {
            "cluster_name": cluster_name,
        }
        if args is not None:
            self._values["args"] = args
        if env is not None:
            self._values["env"] = env
        if image is not None:
            self._values["image"] = image
        if labels is not None:
            self._values["labels"] = labels
        if namespace is not None:
            self._values["namespace"] = namespace
        if replicas is not None:
            self._values["replicas"] = replicas
        if service_account_name is not None:
            self._values["service_account_name"] = service_account_name

    @builtins.property
    def cluster_name(self) -> builtins.str:
        """Kubernetes Cluster Name for alb-ingress-controller.

        :default: - None
        """
        result = self._values.get("cluster_name")
        assert result is not None, "Required property 'cluster_name' is missing"
        return result

    @builtins.property
    def args(self) -> typing.Optional[typing.List[builtins.str]]:
        """Another Args for alb-ingress-controller.

        :default: - None
        """
        result = self._values.get("args")
        return result

    @builtins.property
    def env(self) -> typing.Optional[typing.List["EnvVar"]]:
        """Another Args for alb-ingress-controller.

        :default: - None
        """
        result = self._values.get("env")
        return result

    @builtins.property
    def image(self) -> typing.Optional[builtins.str]:
        """Default image for alb-ingress-controller.

        :default: - docker.io/amazon/aws-alb-ingress-controller:v1.1.9
        """
        result = self._values.get("image")
        return result

    @builtins.property
    def labels(self) -> typing.Optional[typing.Mapping[builtins.str, builtins.str]]:
        """Extra labels to associate with resources.

        :default: - none
        """
        result = self._values.get("labels")
        return result

    @builtins.property
    def namespace(self) -> typing.Optional[builtins.str]:
        """Default Namespace for alb-ingress-controller.

        :default: - kube-system
        """
        result = self._values.get("namespace")
        return result

    @builtins.property
    def replicas(self) -> typing.Optional[jsii.Number]:
        """Replicas for alb-ingress-controller.

        :default: - 1
        """
        result = self._values.get("replicas")
        return result

    @builtins.property
    def service_account_name(self) -> typing.Optional[builtins.str]:
        """Default Service Account Name for alb-ingress-controller.

        :default: - alb-ingress-controller
        """
        result = self._values.get("service_account_name")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "AlbIngressControllerOptions(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.data_type(
    jsii_type="cdk8s-aws-alb-ingress-controller.EnvVar",
    jsii_struct_bases=[],
    name_mapping={"name": "name", "value": "value"},
)
class EnvVar:
    def __init__(
        self,
        *,
        name: builtins.str,
        value: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param name: Name of the environment variable. Must be a C_IDENTIFIER.
        :param value: Variable references $(VAR_NAME) are expanded using the previous defined environment variables in the container and any service environment variables. If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Defaults to "". Default: .
        """
        self._values: typing.Dict[str, typing.Any] = {
            "name": name,
        }
        if value is not None:
            self._values["value"] = value

    @builtins.property
    def name(self) -> builtins.str:
        """Name of the environment variable.

        Must be a C_IDENTIFIER.

        :schema: io.k8s.api.core.v1.EnvVar#name
        """
        result = self._values.get("name")
        assert result is not None, "Required property 'name' is missing"
        return result

    @builtins.property
    def value(self) -> typing.Optional[builtins.str]:
        """Variable references $(VAR_NAME) are expanded using the previous defined environment variables in the container and any service environment variables.

        If a variable cannot be resolved, the reference in the input string will be unchanged. The $(VAR_NAME) syntax can be escaped with a double $$, ie: $$(VAR_NAME). Escaped references will never be expanded, regardless of whether the variable exists or not. Defaults to "".

        :default: .

        :schema: io.k8s.api.core.v1.EnvVar#value
        """
        result = self._values.get("value")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "EnvVar(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


__all__ = [
    "AlbIngressController",
    "AlbIngressControllerOptions",
    "EnvVar",
]

publication.publish()
