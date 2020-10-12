import logging

from prtg_pyprobe.utils.validators import validate


class SensorDefinitionGroup(object):
    class SensorDefinitionGroupField(object):
        def __init__(self, field_type: str, name: str, caption: str, **kwargs):
            self._field_type = field_type
            self._name = name
            self._caption = caption
            self._kwargs = kwargs

        @property
        @validate
        def data(self) -> dict:
            field = {
                "type": self._field_type,
                "name": self._name,
                "caption": self._caption,
            }
            for k, v in self._kwargs.items():
                field[k] = v
            return field

    def __init__(self, name: str, caption: str):
        self._name = name
        self._caption = caption
        self._fields = []

    @property
    @validate
    def data(self) -> dict:
        group = {"name": self._name, "caption": self._caption, "fields": self._fields}
        return group

    def add_field_timeout(self, default: int, minimum: int, maximum: int):
        timeout = self.SensorDefinitionGroupField(
            field_type="integer",
            name="timeout",
            caption="Timeout (in s)",
            required="1",
            default=default,
            minimum=minimum,
            maximum=maximum,
            help=f"If the reply takes longer than this value the request is aborted "
            f"and an error message is triggered. Maximum value is {maximum} sec. (= {maximum / 60} minutes)",
        )
        self._fields.append(timeout.data)

    def add_field(self, field_type: str, name: str, caption: str, **kwargs):
        field = self.SensorDefinitionGroupField(field_type=field_type, name=name, caption=caption, **kwargs)
        self._fields.append(field.data)


class SensorDefinition(object):
    class NotASensorDefinitionGroupError(Exception):
        def __init__(self):
            super().__init__("Group has to be of type SensorDefinitionGroup.")

    def __init__(
        self,
        kind: str,
        name: str,
        description: str,
        sensor_help: str,
        tag: str,
        default: str = None,
    ):
        self._kind = kind
        self._name = name
        self._description = description
        self._help = sensor_help
        self._tag = tag
        self._default = default
        self._groups = []

    @property
    @validate
    def data(self) -> dict:
        definition = {
            "name": self._name,
            "kind": self._kind,
            "description": self._description,
            "help": self._help,
            "tag": self._tag,
            "groups": self._groups,
        }
        if self._default:
            definition["default"] = self._default
        logging.debug(f"Sensor Definition for sensor {self._name}: {str(definition)}")
        return definition

    def add_group(self, group: SensorDefinitionGroup):
        if isinstance(group, SensorDefinitionGroup):
            self._groups.append(group.data)
        else:
            raise self.NotASensorDefinitionGroupError


class SensorData(object):
    class SensorDataChannel(object):
        def __init__(self, name: str, mode: str, value, **kwargs):
            self._name = name
            self._mode = mode
            self._value = value
            self._kwargs = kwargs

        @property
        @validate
        def data(self) -> dict:
            channel = {"name": self._name, "mode": self._mode, "value": self._value}
            for k, v in self._kwargs.items():
                channel[k] = v
            return channel

    def __init__(self, sensor_id: str):
        self._sensor_id = sensor_id
        self._message = None
        self._error = None
        self._error_code = None
        self._channel_list = []

    @property
    def message(self) -> str:
        return self._message

    @message.setter
    def message(self, value: str = None):
        self._message = value

    @property
    def error(self) -> str:
        return self._error

    @error.setter
    def error(self, value: str = None):
        self._error = value

    @property
    def error_code(self) -> int:
        return self._error_code

    @error_code.setter
    def error_code(self, value: int = None):
        self._error_code = value

    @property
    @validate
    def data(self) -> dict:
        sensordata = {"sensorid": self._sensor_id, "message": self._message}
        if self._error and self._error_code:
            sensordata["error"] = self._error
            sensordata["code"] = self._error_code
            return sensordata
        if len(self._channel_list) > 0:
            sensordata["channel"] = self._channel_list
        logging.debug(f"Monitoring data for sensorid {self._sensor_id}: {str(sensordata)}")
        return sensordata

    def add_channel(self, name: str, mode: str, value, **kwargs):
        channel = self.SensorDataChannel(name=name, mode=mode, value=value, **kwargs)
        self._channel_list.append(channel.data)
