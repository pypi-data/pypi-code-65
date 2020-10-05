import re

from easyqueue.core.objects.base.schema import EQObjectSchema
from marshmallow import fields, validates, ValidationError


class UserSchema(EQObjectSchema):

    MIN_LIMIT = 0
    EMAIL_PATTERN = '[^@]+@[^@]+\.[^@]+'

    email = fields.Str(required=True)
    password = fields.Str(required=True)
    region = fields.Str(required=True)
    is_active = fields.Bool(required=True)
    image = fields.Str(required=True, allow_none=True)

    @validates('email')
    def validate_email(self, data: str):
        self.validate_non_empty(data=data)
        if not re.match(self.EMAIL_PATTERN, data):
            raise ValidationError('Invalid email pattern, must math <name>@<server>.<domain>')

    @validates('password')
    def validate_password(self, data: str):
        self.validate_non_empty(data=data)

    @validates('region')
    def validate_region(self, data: str):
        self.validate_non_empty(data=data)
