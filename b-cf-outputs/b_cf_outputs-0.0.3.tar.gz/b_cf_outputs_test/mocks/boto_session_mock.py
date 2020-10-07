import boto3

from b_cf_outputs_test.mocks.cloud_formation_mock import CloudFormationMock


class BotoSessionMock(boto3.session.Session):
    def client(self, *args, **kwargs):
        return CloudFormationMock()
