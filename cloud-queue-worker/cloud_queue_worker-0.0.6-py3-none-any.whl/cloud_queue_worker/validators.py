from typing import Dict
from marshmallow import Schema, fields, validate, validates, ValidationError


class CloudProviderConfigValidator(Schema):
    # TODO: It has to be reworked as soon as we manage multiple cloud provider
    cloud_provider = fields.String(required=True, validate=validate.OneOf(["aws"]))
    region_name = fields.String(required=True)
    aws_access_key_id = fields.String()
    aws_secret_access_key = fields.String()

class CloudQueueWorkerValidator(Schema):
    queue_mapping = fields.Dict(required=True)
    concurrency = fields.Integer(required=True)
    cloud_provider_config = fields.Nested(CloudProviderConfigValidator, required=True)

    @validates("queue_mapping")
    def validate_queue_mapping(self, value: Dict[str, str]):
        if not value:
            raise ValidationError("queue_mapping parameter is missing or empty in the config")
