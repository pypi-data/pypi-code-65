# Copyright 2020 Aptpod, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import abc

from intdash._internal import Comparable

from .parser import data, field, filter

__all__ = ["Filter", "Can", "Nmea", "GeneralSensor", "Generic", "Any"]


class Filter(Comparable, metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def _from(elem):
        pass

    @abc.abstractmethod
    def _to(self):
        pass


class Spec(Comparable, metaclass=abc.ABCMeta):
    @staticmethod
    @abc.abstractmethod
    def _from(elem):
        pass

    @abc.abstractmethod
    def _to(self):
        pass


class Can(Filter):
    data_type = data.DataType.can

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return Can(specs=[CanSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.Can(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return Can(
            specs=[
                CanSpec(
                    mask=int.from_bytes(b"\xff\xff\xff\xff", "little"),
                    result=int(x, 16),
                    accept=True,
                )
                for x in ids
            ]
        )


class CanSpec(Spec):
    def __init__(self, mask, result, accept):
        self.mask = mask
        self.result = result
        self.accept = accept

    @staticmethod
    def _from(spec):
        return CanSpec(
            mask=spec.mask.value, result=spec.result.value, accept=spec.accept
        )

    def _to(self):
        spec = filter.CanSpec(
            mask=field.Uint32(value=self.mask),
            result=field.Uint32(value=self.result),
            flags=field.Uint8(0),
        )
        spec.accept = self.accept
        return spec


class Nmea(Filter):
    data_type = data.DataType.nmea

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return Nmea(specs=[NmeaSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.Nmea(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return Nmea(
            specs=[
                NmeaSpec(
                    mask=int.from_bytes(b"\xff\xff\xff\xff\xff", "little"),
                    result=int.from_bytes(x.encode("utf-8"), "little"),
                    accept=True,
                )
                for x in ids
            ]
        )


class NmeaSpec(Spec):
    def __init__(self, mask, result, accept):
        self.mask = mask
        self.result = result
        self.accept = accept

    @staticmethod
    def _from(spec):
        return NmeaSpec(
            mask=spec.mask.value, result=spec.result.value, accept=spec.accept
        )

    def _to(self):
        spec = filter.NmeaSpec(
            mask=field.Uint40(value=self.mask),
            result=field.Uint40(value=self.result),
            flags=field.Uint8(0),
        )
        spec.accept = self.accept
        return spec


class GeneralSensor(Filter):
    data_type = data.DataType.general_sensor

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return GeneralSensor(specs=[GeneralSensorSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.GeneralSensor(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return GeneralSensor(
            specs=[
                GeneralSensorSpec(
                    mask=int.from_bytes(b"\xff\xff", "little"),
                    result=int(x, 16),
                    accept=True,
                )
                for x in ids
            ]
        )


class GeneralSensorSpec(Spec):
    def __init__(self, mask, result, accept):
        self.mask = mask
        self.result = result
        self.accept = accept

    @staticmethod
    def _from(spec):
        return GeneralSensorSpec(
            mask=spec.mask.value, result=spec.result.value, accept=spec.accept
        )

    def _to(self):
        spec = filter.GeneralSensorSpec(
            mask=field.Uint16(value=self.mask),
            result=field.Uint16(value=self.result),
            flags=field.Uint8(0),
        )
        spec.accept = self.accept
        return spec


class Generic(Filter):
    data_type = data.DataType.generic

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return Generic(specs=[GenericSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.Generic(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return Generic(
            specs=[
                GenericSpec(
                    mask=int.from_bytes(b"\xff\xff\xff\xff", "little"),
                    result=int(x, 16),
                    accept=True,
                )
                for x in ids
            ]
        )


class GenericSpec(Spec):
    def __init__(self, mask, result, accept):
        self.mask = mask
        self.result = result
        self.accept = accept

    @staticmethod
    def _from(spec):
        return GenericSpec(
            mask=spec.mask.value, result=spec.result.value, accept=spec.accept
        )

    def _to(self):
        spec = filter.GenericSpec(
            mask=field.Uint32(value=self.mask),
            result=field.Uint32(value=self.result),
            flags=field.Uint8(0),
        )
        spec.accept = self.accept
        return spec


class Float(Filter):
    data_type = data.DataType.float

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return Float(specs=[PrimitiveSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.Float(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return Float(specs=[PrimitiveSpec(label=x) for x in ids])


class Int(Filter):
    data_type = data.DataType.int

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return Int(specs=[PrimitiveSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.Int(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return Int(specs=[PrimitiveSpec(label=x) for x in ids])


class String(Filter):
    data_type = data.DataType.string

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return String(specs=[PrimitiveSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.String(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return String(specs=[PrimitiveSpec(label=x) for x in ids])


class Bytes(Filter):
    data_type = data.DataType.bytes

    def __init__(self, specs):
        self.specs = specs

    @staticmethod
    def _from(filt):
        return Bytes(specs=[PrimitiveSpec._from(x) for x in filt.specs])

    def _to(self):
        return filter.Bytes(
            spec_num=field.Uint8(value=len(self.specs)),
            specs=[x._to() for x in self.specs],
        )

    @staticmethod
    def from_ids(ids):
        return Bytes(specs=[PrimitiveSpec(label=x) for x in ids])


class PrimitiveSpec(Spec):
    def __init__(self, label):
        self.label = label

    @staticmethod
    def _from(spec):
        return PrimitiveSpec(label=spec.label.value)

    def _to(self):
        spec = filter.PrimitiveSpec(
            label_length=field.Uint8(value=len(self.label)),
            label=field.String(value=self.label),
        )
        return spec


class Any(Comparable):
    def __init__(self, data_type):
        self.data_type = data_type


filter2filter = {
    data.DataType.can.value: Can,
    data.DataType.nmea.value: Nmea,
    data.DataType.general_sensor.value: GeneralSensor,
    data.DataType.generic.value: Generic,
    data.DataType.float.value: Float,
    data.DataType.int.value: Int,
    data.DataType.string.value: String,
    data.DataType.bytes.value: Bytes,
}
