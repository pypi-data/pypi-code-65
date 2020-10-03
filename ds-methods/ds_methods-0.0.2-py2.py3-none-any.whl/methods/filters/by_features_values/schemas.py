from datetime import datetime
from numbers import Number
from schema import Schema, And, Or, Optional


options_schema = Schema(
    {
        str: Or(
            And({
                Optional('gte'): Or(Number, datetime),
                Optional('lte'): Or(Number, datetime),
            }, lambda x: 'gte' in x or 'lte' in x),
            {'equal': Or(Number, str, datetime, bool)},
        ),
    },
    ignore_extra_keys=True,
)
