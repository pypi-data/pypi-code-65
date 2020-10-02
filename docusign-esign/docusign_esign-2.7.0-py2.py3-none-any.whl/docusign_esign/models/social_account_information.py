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


class SocialAccountInformation(object):
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
        'email': 'str',
        'error_details': 'ErrorDetails',
        'provider': 'str',
        'social_id': 'str',
        'user_name': 'str'
    }

    attribute_map = {
        'email': 'email',
        'error_details': 'errorDetails',
        'provider': 'provider',
        'social_id': 'socialId',
        'user_name': 'userName'
    }

    def __init__(self, email=None, error_details=None, provider=None, social_id=None, user_name=None):  # noqa: E501
        """SocialAccountInformation - a model defined in Swagger"""  # noqa: E501

        self._email = None
        self._error_details = None
        self._provider = None
        self._social_id = None
        self._user_name = None
        self.discriminator = None

        if email is not None:
            self.email = email
        if error_details is not None:
            self.error_details = error_details
        if provider is not None:
            self.provider = provider
        if social_id is not None:
            self.social_id = social_id
        if user_name is not None:
            self.user_name = user_name

    @property
    def email(self):
        """Gets the email of this SocialAccountInformation.  # noqa: E501

        The users email address.  # noqa: E501

        :return: The email of this SocialAccountInformation.  # noqa: E501
        :rtype: str
        """
        return self._email

    @email.setter
    def email(self, email):
        """Sets the email of this SocialAccountInformation.

        The users email address.  # noqa: E501

        :param email: The email of this SocialAccountInformation.  # noqa: E501
        :type: str
        """

        self._email = email

    @property
    def error_details(self):
        """Gets the error_details of this SocialAccountInformation.  # noqa: E501


        :return: The error_details of this SocialAccountInformation.  # noqa: E501
        :rtype: ErrorDetails
        """
        return self._error_details

    @error_details.setter
    def error_details(self, error_details):
        """Sets the error_details of this SocialAccountInformation.


        :param error_details: The error_details of this SocialAccountInformation.  # noqa: E501
        :type: ErrorDetails
        """

        self._error_details = error_details

    @property
    def provider(self):
        """Gets the provider of this SocialAccountInformation.  # noqa: E501

        The social account provider (Facebook, Yahoo, etc.)  # noqa: E501

        :return: The provider of this SocialAccountInformation.  # noqa: E501
        :rtype: str
        """
        return self._provider

    @provider.setter
    def provider(self, provider):
        """Sets the provider of this SocialAccountInformation.

        The social account provider (Facebook, Yahoo, etc.)  # noqa: E501

        :param provider: The provider of this SocialAccountInformation.  # noqa: E501
        :type: str
        """

        self._provider = provider

    @property
    def social_id(self):
        """Gets the social_id of this SocialAccountInformation.  # noqa: E501

        The ID provided by the Socal Account.  # noqa: E501

        :return: The social_id of this SocialAccountInformation.  # noqa: E501
        :rtype: str
        """
        return self._social_id

    @social_id.setter
    def social_id(self, social_id):
        """Sets the social_id of this SocialAccountInformation.

        The ID provided by the Socal Account.  # noqa: E501

        :param social_id: The social_id of this SocialAccountInformation.  # noqa: E501
        :type: str
        """

        self._social_id = social_id

    @property
    def user_name(self):
        """Gets the user_name of this SocialAccountInformation.  # noqa: E501

        The full user name for the account.  # noqa: E501

        :return: The user_name of this SocialAccountInformation.  # noqa: E501
        :rtype: str
        """
        return self._user_name

    @user_name.setter
    def user_name(self, user_name):
        """Sets the user_name of this SocialAccountInformation.

        The full user name for the account.  # noqa: E501

        :param user_name: The user_name of this SocialAccountInformation.  # noqa: E501
        :type: str
        """

        self._user_name = user_name

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
        if issubclass(SocialAccountInformation, dict):
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
        if not isinstance(other, SocialAccountInformation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
