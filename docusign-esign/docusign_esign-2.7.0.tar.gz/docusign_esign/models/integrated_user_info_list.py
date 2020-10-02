# coding: utf-8

"""
    DocuSign REST API

    The DocuSign REST API provides you with a powerful, convenient, and simple Web services API for interacting with DocuSign.  # noqa: E501

    OpenAPI spec version: v2
    Contact: devcenter@docusign.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class IntegratedUserInfoList(object):
    """NOTE: This class is auto generated by the swagger code generator program.

    Do not edit the class manually.
    """

    """
    Attributes:
      swagger_types (dict): The key is attribute name
                            and the value is attribute type.
      attribute_map (dict): The key is attribute name
                            and the value is json key in definition.
    """
    swagger_types = {
        'all_users_selected': 'str',
        'end_position': 'str',
        'next_uri': 'str',
        'previous_uri': 'str',
        'result_set_size': 'str',
        'start_position': 'str',
        'total_set_size': 'str',
        'users': 'list[UserInfo]'
    }

    attribute_map = {
        'all_users_selected': 'allUsersSelected',
        'end_position': 'endPosition',
        'next_uri': 'nextUri',
        'previous_uri': 'previousUri',
        'result_set_size': 'resultSetSize',
        'start_position': 'startPosition',
        'total_set_size': 'totalSetSize',
        'users': 'users'
    }

    def __init__(self, all_users_selected=None, end_position=None, next_uri=None, previous_uri=None, result_set_size=None, start_position=None, total_set_size=None, users=None):  # noqa: E501
        """IntegratedUserInfoList - a model defined in Swagger"""  # noqa: E501

        self._all_users_selected = None
        self._end_position = None
        self._next_uri = None
        self._previous_uri = None
        self._result_set_size = None
        self._start_position = None
        self._total_set_size = None
        self._users = None
        self.discriminator = None

        if all_users_selected is not None:
            self.all_users_selected = all_users_selected
        if end_position is not None:
            self.end_position = end_position
        if next_uri is not None:
            self.next_uri = next_uri
        if previous_uri is not None:
            self.previous_uri = previous_uri
        if result_set_size is not None:
            self.result_set_size = result_set_size
        if start_position is not None:
            self.start_position = start_position
        if total_set_size is not None:
            self.total_set_size = total_set_size
        if users is not None:
            self.users = users

    @property
    def all_users_selected(self):
        """Gets the all_users_selected of this IntegratedUserInfoList.  # noqa: E501

          # noqa: E501

        :return: The all_users_selected of this IntegratedUserInfoList.  # noqa: E501
        :rtype: str
        """
        return self._all_users_selected

    @all_users_selected.setter
    def all_users_selected(self, all_users_selected):
        """Sets the all_users_selected of this IntegratedUserInfoList.

          # noqa: E501

        :param all_users_selected: The all_users_selected of this IntegratedUserInfoList.  # noqa: E501
        :type: str
        """

        self._all_users_selected = all_users_selected

    @property
    def end_position(self):
        """Gets the end_position of this IntegratedUserInfoList.  # noqa: E501

        The last position in the result set.   # noqa: E501

        :return: The end_position of this IntegratedUserInfoList.  # noqa: E501
        :rtype: str
        """
        return self._end_position

    @end_position.setter
    def end_position(self, end_position):
        """Sets the end_position of this IntegratedUserInfoList.

        The last position in the result set.   # noqa: E501

        :param end_position: The end_position of this IntegratedUserInfoList.  # noqa: E501
        :type: str
        """

        self._end_position = end_position

    @property
    def next_uri(self):
        """Gets the next_uri of this IntegratedUserInfoList.  # noqa: E501

        The URI to the next chunk of records based on the search request. If the endPosition is the entire results of the search, this is null.   # noqa: E501

        :return: The next_uri of this IntegratedUserInfoList.  # noqa: E501
        :rtype: str
        """
        return self._next_uri

    @next_uri.setter
    def next_uri(self, next_uri):
        """Sets the next_uri of this IntegratedUserInfoList.

        The URI to the next chunk of records based on the search request. If the endPosition is the entire results of the search, this is null.   # noqa: E501

        :param next_uri: The next_uri of this IntegratedUserInfoList.  # noqa: E501
        :type: str
        """

        self._next_uri = next_uri

    @property
    def previous_uri(self):
        """Gets the previous_uri of this IntegratedUserInfoList.  # noqa: E501

        The postal code for the billing address.  # noqa: E501

        :return: The previous_uri of this IntegratedUserInfoList.  # noqa: E501
        :rtype: str
        """
        return self._previous_uri

    @previous_uri.setter
    def previous_uri(self, previous_uri):
        """Sets the previous_uri of this IntegratedUserInfoList.

        The postal code for the billing address.  # noqa: E501

        :param previous_uri: The previous_uri of this IntegratedUserInfoList.  # noqa: E501
        :type: str
        """

        self._previous_uri = previous_uri

    @property
    def result_set_size(self):
        """Gets the result_set_size of this IntegratedUserInfoList.  # noqa: E501

        The number of results returned in this response.   # noqa: E501

        :return: The result_set_size of this IntegratedUserInfoList.  # noqa: E501
        :rtype: str
        """
        return self._result_set_size

    @result_set_size.setter
    def result_set_size(self, result_set_size):
        """Sets the result_set_size of this IntegratedUserInfoList.

        The number of results returned in this response.   # noqa: E501

        :param result_set_size: The result_set_size of this IntegratedUserInfoList.  # noqa: E501
        :type: str
        """

        self._result_set_size = result_set_size

    @property
    def start_position(self):
        """Gets the start_position of this IntegratedUserInfoList.  # noqa: E501

        Starting position of the current result set.  # noqa: E501

        :return: The start_position of this IntegratedUserInfoList.  # noqa: E501
        :rtype: str
        """
        return self._start_position

    @start_position.setter
    def start_position(self, start_position):
        """Sets the start_position of this IntegratedUserInfoList.

        Starting position of the current result set.  # noqa: E501

        :param start_position: The start_position of this IntegratedUserInfoList.  # noqa: E501
        :type: str
        """

        self._start_position = start_position

    @property
    def total_set_size(self):
        """Gets the total_set_size of this IntegratedUserInfoList.  # noqa: E501

        The total number of items available in the result set. This will always be greater than or equal to the value of the property returning the results in the in the response.  # noqa: E501

        :return: The total_set_size of this IntegratedUserInfoList.  # noqa: E501
        :rtype: str
        """
        return self._total_set_size

    @total_set_size.setter
    def total_set_size(self, total_set_size):
        """Sets the total_set_size of this IntegratedUserInfoList.

        The total number of items available in the result set. This will always be greater than or equal to the value of the property returning the results in the in the response.  # noqa: E501

        :param total_set_size: The total_set_size of this IntegratedUserInfoList.  # noqa: E501
        :type: str
        """

        self._total_set_size = total_set_size

    @property
    def users(self):
        """Gets the users of this IntegratedUserInfoList.  # noqa: E501

          # noqa: E501

        :return: The users of this IntegratedUserInfoList.  # noqa: E501
        :rtype: list[UserInfo]
        """
        return self._users

    @users.setter
    def users(self, users):
        """Sets the users of this IntegratedUserInfoList.

          # noqa: E501

        :param users: The users of this IntegratedUserInfoList.  # noqa: E501
        :type: list[UserInfo]
        """

        self._users = users

    def to_dict(self):
        """Returns the model properties as a dict"""
        result = {}

        for attr, _ in six.iteritems(self.swagger_types):
            value = getattr(self, attr)
            if isinstance(value, list):
                result[attr] = list(map(
                    lambda x: x.to_dict() if hasattr(x, "to_dict") else x,
                    value
                ))
            elif hasattr(value, "to_dict"):
                result[attr] = value.to_dict()
            elif isinstance(value, dict):
                result[attr] = dict(map(
                    lambda item: (item[0], item[1].to_dict())
                    if hasattr(item[1], "to_dict") else item,
                    value.items()
                ))
            else:
                result[attr] = value
        if issubclass(IntegratedUserInfoList, dict):
            for key, value in self.items():
                result[key] = value

        return result

    def to_str(self):
        """Returns the string representation of the model"""
        return pprint.pformat(self.to_dict())

    def __repr__(self):
        """For `print` and `pprint`"""
        return self.to_str()

    def __eq__(self, other):
        """Returns true if both objects are equal"""
        if not isinstance(other, IntegratedUserInfoList):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
