import string

from marshmallow import Schema, fields, ValidationError, validates


class EQObjectSchema(Schema):

    MIN_TIMESTAMP = 1580000000.000000
    MAX_TIMESTAMP = 4101600000.000000
    PUNCTUATION_CHARACTERS = {'_', '-'}
    VALID_CHARACTERS = set(string.ascii_lowercase).union(string.digits).union(PUNCTUATION_CHARACTERS)

    id = fields.Str(required=False)
    identificator = fields.Str(required=True)
    created_at = fields.Integer(required=True)

    @classmethod
    def validate_allowed_characters(cls, data: str, valid_chars=None, punctuation_chars=None):
        valid_chars = valid_chars or cls.VALID_CHARACTERS
        punctuation_chars = punctuation_chars or cls.PUNCTUATION_CHARACTERS
        i = 0
        for char in data:
            if char not in valid_chars:
                raise ValidationError('Invalid character "{}"'.format(char))
            if i > 1 and char in punctuation_chars and data[i - 1] == char:
                raise ValidationError('Invalid double punctuation character "{}"'.format(char))
            i += 1

    @classmethod
    def validate_non_empty(cls, data: iter):
        if not data:
            raise ValidationError('Invalid empty field')

    @validates('id')
    def validate_id(self, data: str):
        self.validate_non_empty(data=data)

    @validates('identificator')
    def validate_identificator(self, data: str):
        self.validate_non_empty(data=data)
        self.validate_allowed_characters(data=data)

    @validates('created_at')
    def validate_created_at(self, data: int):
        if self.MIN_TIMESTAMP > data or data > self.MAX_TIMESTAMP:
            raise ValidationError('Invalid value field')
