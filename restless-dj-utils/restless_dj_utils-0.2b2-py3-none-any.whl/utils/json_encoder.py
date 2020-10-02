"""JSON encoders"""
import json

from restless.serializers import JSONSerializer as rJSONSerializer
from restless.utils import MoreTypesJSONEncoder

try:
    from uuid import UUID
except ImportError:
    UUID = None

try:
    from datetime import datetime
except ImportError:
    datetime = None


class JSONEncoder(MoreTypesJSONEncoder):
    """Custom JSON envoder"""

    def default(self, data):
        if datetime and isinstance(data, datetime):
            return data.strftime("%Y-%m-%dT%H:%M:%SZ")
        if UUID and isinstance(data, UUID):
            return str(data)
        if isinstance(data, bytes):
            return str(data, encoding="utf-8")
        return super().default(data)


class JSONSerializer(rJSONSerializer):
    """Custom JSON serializer"""

    def serialize(self, data):
        return json.dumps(data, cls=JSONEncoder)
