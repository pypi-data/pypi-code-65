import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "cdk8s-aws-alb-ingress-controller",
    "version": "0.0.7",
    "description": "cdk8s-aws-alb-ingress-controller is an CDK8S construct library that provides AWS Alb Ingress Controller Deplyment Configure.",
    "license": "Apache-2.0",
    "url": "https://github.com/guan840912/cdk8s-aws-alb-ingress-controller.git",
    "long_description_content_type": "text/markdown",
    "author": "Neil Kuan<guan840912@gmail.com>",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/guan840912/cdk8s-aws-alb-ingress-controller.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "cdk8s_aws_alb_ingress_controller",
        "cdk8s_aws_alb_ingress_controller._jsii"
    ],
    "package_data": {
        "cdk8s_aws_alb_ingress_controller._jsii": [
            "cdk8s-aws-alb-ingress-controller@0.0.7.jsii.tgz"
        ],
        "cdk8s_aws_alb_ingress_controller": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "cdk8s-plus>=0.30.0, <0.31.0",
        "cdk8s>=0.30.0, <0.31.0",
        "constructs>=3.0.4, <4.0.0",
        "jsii>=1.13.0, <2.0.0",
        "publication>=0.0.3"
    ],
    "classifiers": [
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: JavaScript",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Typing :: Typed",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved"
    ]
}
"""
)

with open("README.md") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
