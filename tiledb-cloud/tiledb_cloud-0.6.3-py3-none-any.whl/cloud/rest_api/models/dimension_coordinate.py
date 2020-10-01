# coding: utf-8

"""
    TileDB Storage Platform API

    TileDB Storage Platform REST API  # noqa: E501

    The version of the OpenAPI document: 2.0.4
    Generated by: https://openapi-generator.tech
"""


import pprint
import re  # noqa: F401

import six


class DimensionCoordinate(object):
    """NOTE: This class is auto generated by OpenAPI Generator.
    Ref: https://openapi-generator.tech

    Do not edit the class manually.
    """

    """
    Attributes:
      openapi_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    openapi_types = {
        "int8": "int",
        "uint8": "int",
        "int16": "int",
        "uint16": "int",
        "int32": "int",
        "uint32": "int",
        "int64": "int",
        "uint64": "int",
        "float32": "float",
        "float64": "float",
    }

    attribute_map = {
        "int8": "int8",
        "uint8": "uint8",
        "int16": "int16",
        "uint16": "uint16",
        "int32": "int32",
        "uint32": "uint32",
        "int64": "int64",
        "uint64": "uint64",
        "float32": "float32",
        "float64": "float64",
    }

    def __init__(
        self,
        int8=None,
        uint8=None,
        int16=None,
        uint16=None,
        int32=None,
        uint32=None,
        int64=None,
        uint64=None,
        float32=None,
        float64=None,
    ):  # noqa: E501
        """DimensionCoordinate - a model defined in OpenAPI"""  # noqa: E501

        self._int8 = None
        self._uint8 = None
        self._int16 = None
        self._uint16 = None
        self._int32 = None
        self._uint32 = None
        self._int64 = None
        self._uint64 = None
        self._float32 = None
        self._float64 = None
        self.discriminator = None

        if int8 is not None:
            self.int8 = int8
        if uint8 is not None:
            self.uint8 = uint8
        if int16 is not None:
            self.int16 = int16
        if uint16 is not None:
            self.uint16 = uint16
        if int32 is not None:
            self.int32 = int32
        if uint32 is not None:
            self.uint32 = uint32
        if int64 is not None:
            self.int64 = int64
        if uint64 is not None:
            self.uint64 = uint64
        if float32 is not None:
            self.float32 = float32
        if float64 is not None:
            self.float64 = float64

    @property
    def int8(self):
        """Gets the int8 of this DimensionCoordinate.  # noqa: E501


        :return: The int8 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._int8

    @int8.setter
    def int8(self, int8):
        """Sets the int8 of this DimensionCoordinate.


        :param int8: The int8 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._int8 = int8

    @property
    def uint8(self):
        """Gets the uint8 of this DimensionCoordinate.  # noqa: E501


        :return: The uint8 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._uint8

    @uint8.setter
    def uint8(self, uint8):
        """Sets the uint8 of this DimensionCoordinate.


        :param uint8: The uint8 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._uint8 = uint8

    @property
    def int16(self):
        """Gets the int16 of this DimensionCoordinate.  # noqa: E501


        :return: The int16 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._int16

    @int16.setter
    def int16(self, int16):
        """Sets the int16 of this DimensionCoordinate.


        :param int16: The int16 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._int16 = int16

    @property
    def uint16(self):
        """Gets the uint16 of this DimensionCoordinate.  # noqa: E501


        :return: The uint16 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._uint16

    @uint16.setter
    def uint16(self, uint16):
        """Sets the uint16 of this DimensionCoordinate.


        :param uint16: The uint16 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._uint16 = uint16

    @property
    def int32(self):
        """Gets the int32 of this DimensionCoordinate.  # noqa: E501


        :return: The int32 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._int32

    @int32.setter
    def int32(self, int32):
        """Sets the int32 of this DimensionCoordinate.


        :param int32: The int32 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._int32 = int32

    @property
    def uint32(self):
        """Gets the uint32 of this DimensionCoordinate.  # noqa: E501


        :return: The uint32 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._uint32

    @uint32.setter
    def uint32(self, uint32):
        """Sets the uint32 of this DimensionCoordinate.


        :param uint32: The uint32 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._uint32 = uint32

    @property
    def int64(self):
        """Gets the int64 of this DimensionCoordinate.  # noqa: E501


        :return: The int64 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._int64

    @int64.setter
    def int64(self, int64):
        """Sets the int64 of this DimensionCoordinate.


        :param int64: The int64 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._int64 = int64

    @property
    def uint64(self):
        """Gets the uint64 of this DimensionCoordinate.  # noqa: E501


        :return: The uint64 of this DimensionCoordinate.  # noqa: E501
        :rtype: int
        """
        return self._uint64

    @uint64.setter
    def uint64(self, uint64):
        """Sets the uint64 of this DimensionCoordinate.


        :param uint64: The uint64 of this DimensionCoordinate.  # noqa: E501
        :type: int
        """

        self._uint64 = uint64

    @property
    def float32(self):
        """Gets the float32 of this DimensionCoordinate.  # noqa: E501


        :return: The float32 of this DimensionCoordinate.  # noqa: E501
        :rtype: float
        """
        return self._float32

    @float32.setter
    def float32(self, float32):
        """Sets the float32 of this DimensionCoordinate.


        :param float32: The float32 of this DimensionCoordinate.  # noqa: E501
        :type: float
        """

        self._float32 = float32

    @property
    def float64(self):
        """Gets the float64 of this DimensionCoordinate.  # noqa: E501


        :return: The float64 of this DimensionCoordinate.  # noqa: E501
        :rtype: float
        """
        return self._float64

    @float64.setter
    def float64(self, float64):
        """Sets the float64 of this DimensionCoordinate.


        :param float64: The float64 of this DimensionCoordinate.  # noqa: E501
        :type: float
        """

        self._float64 = float64

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.openapi_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(
                    map(lambda x: x.to_dict() if hasattr(x, "to_dict") else x, value)
                )
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(
                    map(
                        lambda item: (item[0], item[1].to_dict())
                        if hasattr(item[1], "to_dict")
                        else item,
                        value.items(),
                    )
                )
            else:
                result[attr] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, DimensionCoordinate):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
