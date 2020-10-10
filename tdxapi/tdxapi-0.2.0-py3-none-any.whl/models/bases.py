import json
import pprint
import webbrowser
from datetime import datetime
from enum import Enum

import attr
from dateutil import tz

_pprinter = pprint.PrettyPrinter()


@attr.s
class TdxModel(object):
    # Used to warn users that this object may only have partial data
    # and performing a save() call could result in data loss.
    _partial = attr.ib(default=True, repr=False, cmp=False)
    __tdx_type__ = None

    def docs(self):
        webbrowser.open_new_tab(
            f"https://app.teamdynamix.com/TDWebApi/Home/type/{self.__tdx_type__}"
        )

    @classmethod
    def from_data(cls, data, partial=True):
        """Create an instance of object from TDX json decoded data."""
        # 404 errors will return no data
        if data is None:
            return None

        def model_from_dict(class_, dictionary):
            kwargs = {}

            for field in [f for f in attr.fields(class_) if f.repr]:
                tdx_name = field.metadata["tdx_name"]

                try:
                    val = dictionary[tdx_name]

                    if isinstance(val, str) and val.strip() == "":
                        val = None

                    kwargs[field.name] = val
                except KeyError:
                    pass

            return class_(partial=partial, **kwargs)

        if isinstance(data, dict):
            return model_from_dict(cls, data)

        elif isinstance(data, list):
            return [model_from_dict(cls, d) for d in data]

        else:
            raise ValueError(f"Failed to create {cls.__name__} from {type(data)}")

    def __str__(self):
        return _pprinter.pformat(attr.asdict(self, filter=lambda a, v: a.repr is True))


class TdxModelEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, TdxModel):
            data = {}

            for field in [f for f in attr.fields(o.__class__) if f.repr]:
                value = getattr(o, field.name)
                data[field.metadata["tdx_name"]] = value

            return data

        elif isinstance(o, datetime):
            # If datetime object is timezone unaware convert to local timezone
            if o.tzinfo is None:
                o = o.replace(tzinfo=tz.tzlocal())

            return o.isoformat()

        elif isinstance(o, Enum):
            return o.value

        return json.JSONEncoder.default(self, o)
