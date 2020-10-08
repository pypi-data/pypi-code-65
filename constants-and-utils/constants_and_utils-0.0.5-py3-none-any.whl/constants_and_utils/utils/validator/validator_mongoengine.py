try:
    from bson import ObjectId
except ImportError:
    raise ImportError('MongoEngine not installed')
from .basevalidator import BaseValidator


class MongoValidator(BaseValidator):
    def _validate_mongo_id(self, mongo_id, field, value):
        """ Test the ObjectId of a value.

        The rule's arguments are validated against this schema:
        {'type': 'boolean'}
        """
        if mongo_id and not ObjectId.is_valid(value):
            self._error(field, "Is not a valid ID")
