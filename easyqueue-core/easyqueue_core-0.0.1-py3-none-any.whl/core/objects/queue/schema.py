from easyqueue.core.objects.base.schema import EQObjectSchema
from marshmallow import fields, ValidationError, validates


class QueueSchema(EQObjectSchema):

    MIN_LIMIT = 0

    region = fields.Str(required=True)
    user_id = fields.Str(required=True)
    group = fields.Str(required=True)
    info = fields.Str(required=True)
    tags = fields.List(required=True, cls_or_instance=fields.Str)
    limit = fields.Integer(required=False)
    is_active = fields.Bool(required=True)
    image = fields.Str(required=True, allow_none=True)

    @validates('user_id')
    def validate_user_id(self, data: str):
        self.validate_non_empty(data=data)

    @validates('region')
    def validate_region(self, data: str):
        self.validate_non_empty(data=data)

    @validates('group')
    def validate_group(self, data: str):
        self.validate_non_empty(data=data)

    @validates('tags')
    def validate_tags(self, data: set):
        if not isinstance(data, list):
            raise ValidationError('Invalid type "{}, must be list'.format(type(data)))
        for element in data:
            self.validate_non_empty(data=element)

    @validates('limit')
    def validate_limit(self, data: int):
        if data:
            if data <= self.MIN_LIMIT:
                raise ValidationError('Limit must be greater than 0 (0 no limit)')
