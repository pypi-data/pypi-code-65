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


class UDFInfoVersion(object):
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
        "id": "str",
        "udf_image_uuid": "str",
        "name": "str",
        "version": "str",
        "image_name": "str",
        "_exec": "str",
        "exec_raw": "str",
        "default": "bool",
    }

    attribute_map = {
        "id": "id",
        "udf_image_uuid": "udf_image_uuid",
        "name": "name",
        "version": "version",
        "image_name": "image_name",
        "_exec": "exec",
        "exec_raw": "exec_raw",
        "default": "default",
    }

    def __init__(
        self,
        id=None,
        udf_image_uuid=None,
        name=None,
        version=None,
        image_name=None,
        _exec=None,
        exec_raw=None,
        default=None,
    ):  # noqa: E501
        """UDFInfoVersion - a model defined in OpenAPI"""  # noqa: E501

        self._id = None
        self._udf_image_uuid = None
        self._name = None
        self._version = None
        self._image_name = None
        self.__exec = None
        self._exec_raw = None
        self._default = None
        self.discriminator = None

        if id is not None:
            self.id = id
        if udf_image_uuid is not None:
            self.udf_image_uuid = udf_image_uuid
        if name is not None:
            self.name = name
        if version is not None:
            self.version = version
        if image_name is not None:
            self.image_name = image_name
        if _exec is not None:
            self._exec = _exec
        if exec_raw is not None:
            self.exec_raw = exec_raw
        if default is not None:
            self.default = default

    @property
    def id(self):
        """Gets the id of this UDFInfoVersion.  # noqa: E501

        Unique id of a versioned udf  # noqa: E501

        :return: The id of this UDFInfoVersion.  # noqa: E501
        :rtype: str
        """
        return self._id

    @id.setter
    def id(self, id):
        """Sets the id of this UDFInfoVersion.

        Unique id of a versioned udf  # noqa: E501

        :param id: The id of this UDFInfoVersion.  # noqa: E501
        :type: str
        """

        self._id = id

    @property
    def udf_image_uuid(self):
        """Gets the udf_image_uuid of this UDFInfoVersion.  # noqa: E501

        Unique id of the versioned image used by current udf version  # noqa: E501

        :return: The udf_image_uuid of this UDFInfoVersion.  # noqa: E501
        :rtype: str
        """
        return self._udf_image_uuid

    @udf_image_uuid.setter
    def udf_image_uuid(self, udf_image_uuid):
        """Sets the udf_image_uuid of this UDFInfoVersion.

        Unique id of the versioned image used by current udf version  # noqa: E501

        :param udf_image_uuid: The udf_image_uuid of this UDFInfoVersion.  # noqa: E501
        :type: str
        """

        self._udf_image_uuid = udf_image_uuid

    @property
    def name(self):
        """Gets the name of this UDFInfoVersion.  # noqa: E501

        name of udf version  # noqa: E501

        :return: The name of this UDFInfoVersion.  # noqa: E501
        :rtype: str
        """
        return self._name

    @name.setter
    def name(self, name):
        """Sets the name of this UDFInfoVersion.

        name of udf version  # noqa: E501

        :param name: The name of this UDFInfoVersion.  # noqa: E501
        :type: str
        """

        self._name = name

    @property
    def version(self):
        """Gets the version of this UDFInfoVersion.  # noqa: E501

        Type-specific version  # noqa: E501

        :return: The version of this UDFInfoVersion.  # noqa: E501
        :rtype: str
        """
        return self._version

    @version.setter
    def version(self, version):
        """Sets the version of this UDFInfoVersion.

        Type-specific version  # noqa: E501

        :param version: The version of this UDFInfoVersion.  # noqa: E501
        :type: str
        """

        self._version = version

    @property
    def image_name(self):
        """Gets the image_name of this UDFInfoVersion.  # noqa: E501

        Docker image name to use for udf  # noqa: E501

        :return: The image_name of this UDFInfoVersion.  # noqa: E501
        :rtype: str
        """
        return self._image_name

    @image_name.setter
    def image_name(self, image_name):
        """Sets the image_name of this UDFInfoVersion.

        Docker image name to use for udf  # noqa: E501

        :param image_name: The image_name of this UDFInfoVersion.  # noqa: E501
        :type: str
        """

        self._image_name = image_name

    @property
    def _exec(self):
        """Gets the _exec of this UDFInfoVersion.  # noqa: E501

        Type-specific executable text  # noqa: E501

        :return: The _exec of this UDFInfoVersion.  # noqa: E501
        :rtype: str
        """
        return self.__exec

    @_exec.setter
    def _exec(self, _exec):
        """Sets the _exec of this UDFInfoVersion.

        Type-specific executable text  # noqa: E501

        :param _exec: The _exec of this UDFInfoVersion.  # noqa: E501
        :type: str
        """

        self.__exec = _exec

    @property
    def exec_raw(self):
        """Gets the exec_raw of this UDFInfoVersion.  # noqa: E501

        optional raw text to store of serialized function, used for showing in UI  # noqa: E501

        :return: The exec_raw of this UDFInfoVersion.  # noqa: E501
        :rtype: str
        """
        return self._exec_raw

    @exec_raw.setter
    def exec_raw(self, exec_raw):
        """Sets the exec_raw of this UDFInfoVersion.

        optional raw text to store of serialized function, used for showing in UI  # noqa: E501

        :param exec_raw: The exec_raw of this UDFInfoVersion.  # noqa: E501
        :type: str
        """

        self._exec_raw = exec_raw

    @property
    def default(self):
        """Gets the default of this UDFInfoVersion.  # noqa: E501

        If current image version is default version  # noqa: E501

        :return: The default of this UDFInfoVersion.  # noqa: E501
        :rtype: bool
        """
        return self._default

    @default.setter
    def default(self, default):
        """Sets the default of this UDFInfoVersion.

        If current image version is default version  # noqa: E501

        :param default: The default of this UDFInfoVersion.  # noqa: E501
        :type: bool
        """

        self._default = default

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
        if not isinstance(other, UDFInfoVersion):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
