import string

from easyqueue.core.objects.base.schema import EQObjectSchema
from marshmallow import fields, ValidationError, validates


class RestServiceSchema(EQObjectSchema):

    MIN_PORT = 1024
    MAX_PORT = 49151
    PUNCTUATION_CHARACTERS = {'_', '-', '/'}
    VALID_CHARACTERS = set(string.ascii_lowercase).union(string.digits).union(PUNCTUATION_CHARACTERS)

    host = fields.Str(required=True)
    port = fields.Integer(required=False, allow_none=True)
    context_path = fields.Str(required=True)

    @validates('host')
    def validate_host(self, data: str):
        self.validate_non_empty(data=data)

    @validates('port')
    def validate_port(self, data: int):
        if data:
            if data <= self.MIN_PORT or data > self.MAX_PORT:
                raise ValidationError('Port must be between {} and {}'.format(self.MIN_PORT, self.MAX_PORT))

    @validates('context_path')
    def validate_context_path(self, data: str):
        self.validate_non_empty(data=data)

        if not data.startswith('/'):
            raise ValidationError('Must start with "/"')

        self.validate_allowed_characters(data=data, valid_chars=self.VALID_CHARACTERS, punctuation_chars=self.PUNCTUATION_CHARACTERS)
