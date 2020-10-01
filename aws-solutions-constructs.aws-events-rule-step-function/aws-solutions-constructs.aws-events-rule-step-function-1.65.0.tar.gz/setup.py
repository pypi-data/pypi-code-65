import json
import setuptools

kwargs = json.loads(
    """
{
    "name": "aws-solutions-constructs.aws-events-rule-step-function",
    "version": "1.65.0",
    "description": "CDK Constructs for deploying AWS Events Rule that invokes AWS Step Function",
    "license": "Apache-2.0",
    "url": "https://github.com/awslabs/aws-solutions-constructs.git",
    "long_description_content_type": "text/markdown",
    "author": "Amazon Web Services",
    "bdist_wheel": {
        "universal": true
    },
    "project_urls": {
        "Source": "https://github.com/awslabs/aws-solutions-constructs.git"
    },
    "package_dir": {
        "": "src"
    },
    "packages": [
        "aws_solutions_constructs.aws_events_rule_step_function",
        "aws_solutions_constructs.aws_events_rule_step_function._jsii"
    ],
    "package_data": {
        "aws_solutions_constructs.aws_events_rule_step_function._jsii": [
            "aws-events-rule-step-function@1.65.0.jsii.tgz"
        ],
        "aws_solutions_constructs.aws_events_rule_step_function": [
            "py.typed"
        ]
    },
    "python_requires": ">=3.6",
    "install_requires": [
        "aws-cdk.aws-cloudwatch>=1.65.0, <1.66.0",
        "aws-cdk.aws-events>=1.65.0, <1.66.0",
        "aws-cdk.aws-iam>=1.65.0, <1.66.0",
        "aws-cdk.aws-lambda>=1.65.0, <1.66.0",
        "aws-cdk.aws-logs>=1.65.0, <1.66.0",
        "aws-cdk.aws-stepfunctions-tasks>=1.65.0, <1.66.0",
        "aws-cdk.aws-stepfunctions>=1.65.0, <1.66.0",
        "aws-cdk.core>=1.65.0, <1.66.0",
        "aws-solutions-constructs.core>=1.65.0, <1.66.0",
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
        "License :: OSI Approved"
    ]
}
"""
)

with open("README.md") as fp:
    kwargs["long_description"] = fp.read()


setuptools.setup(**kwargs)
