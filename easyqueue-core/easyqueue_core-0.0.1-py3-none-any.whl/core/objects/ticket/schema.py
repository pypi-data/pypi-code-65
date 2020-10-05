from easyqueue.core.objects.base.schema import EQObjectSchema
from marshmallow import fields, validates


class TicketSchema(EQObjectSchema):

    user_id = fields.Str(required=True)
    user_identificator = fields.Str(required=True)
    region = fields.Str(required=True)
    queue_id = fields.Str(required=True)
    queue_identificator = fields.Str(required=True)
    is_active = fields.Bool(required=True)

    @validates('user_id')
    def validate_user_id(self, data: str):
        self.validate_non_empty(data=data)

    @validates('user_identificator')
    def validate_user_identificator(self, data: str):
        self.validate_non_empty(data=data)

    @validates('region')
    def validate_region(self, data: str):
        self.validate_non_empty(data=data)

    @validates('queue_id')
    def validate_queue_id(self, data: str):
        self.validate_non_empty(data=data)

    @validates('queue_identificator')
    def validate_queue_identificator(self, data: set):
        self.validate_non_empty(data=data)
