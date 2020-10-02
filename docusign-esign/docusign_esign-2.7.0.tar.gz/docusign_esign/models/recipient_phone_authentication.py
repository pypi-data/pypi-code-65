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


class RecipientPhoneAuthentication(object):
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
        'recip_may_provide_number': 'str',
        'record_voice_print': 'str',
        'sender_provided_numbers': 'list[str]',
        'validate_recip_provided_number': 'str'
    }

    attribute_map = {
        'recip_may_provide_number': 'recipMayProvideNumber',
        'record_voice_print': 'recordVoicePrint',
        'sender_provided_numbers': 'senderProvidedNumbers',
        'validate_recip_provided_number': 'validateRecipProvidedNumber'
    }

    def __init__(self, recip_may_provide_number=None, record_voice_print=None, sender_provided_numbers=None, validate_recip_provided_number=None):  # noqa: E501
        """RecipientPhoneAuthentication - a model defined in Swagger"""  # noqa: E501

        self._recip_may_provide_number = None
        self._record_voice_print = None
        self._sender_provided_numbers = None
        self._validate_recip_provided_number = None
        self.discriminator = None

        if recip_may_provide_number is not None:
            self.recip_may_provide_number = recip_may_provide_number
        if record_voice_print is not None:
            self.record_voice_print = record_voice_print
        if sender_provided_numbers is not None:
            self.sender_provided_numbers = sender_provided_numbers
        if validate_recip_provided_number is not None:
            self.validate_recip_provided_number = validate_recip_provided_number

    @property
    def recip_may_provide_number(self):
        """Gets the recip_may_provide_number of this RecipientPhoneAuthentication.  # noqa: E501

        Boolean. When set to **true**, the recipient can supply a phone number their choice.  # noqa: E501

        :return: The recip_may_provide_number of this RecipientPhoneAuthentication.  # noqa: E501
        :rtype: str
        """
        return self._recip_may_provide_number

    @recip_may_provide_number.setter
    def recip_may_provide_number(self, recip_may_provide_number):
        """Sets the recip_may_provide_number of this RecipientPhoneAuthentication.

        Boolean. When set to **true**, the recipient can supply a phone number their choice.  # noqa: E501

        :param recip_may_provide_number: The recip_may_provide_number of this RecipientPhoneAuthentication.  # noqa: E501
        :type: str
        """

        self._recip_may_provide_number = recip_may_provide_number

    @property
    def record_voice_print(self):
        """Gets the record_voice_print of this RecipientPhoneAuthentication.  # noqa: E501

        Reserved.  # noqa: E501

        :return: The record_voice_print of this RecipientPhoneAuthentication.  # noqa: E501
        :rtype: str
        """
        return self._record_voice_print

    @record_voice_print.setter
    def record_voice_print(self, record_voice_print):
        """Sets the record_voice_print of this RecipientPhoneAuthentication.

        Reserved.  # noqa: E501

        :param record_voice_print: The record_voice_print of this RecipientPhoneAuthentication.  # noqa: E501
        :type: str
        """

        self._record_voice_print = record_voice_print

    @property
    def sender_provided_numbers(self):
        """Gets the sender_provided_numbers of this RecipientPhoneAuthentication.  # noqa: E501

        An Array containing a list of phone numbers the recipient may use for SMS text authentication.   # noqa: E501

        :return: The sender_provided_numbers of this RecipientPhoneAuthentication.  # noqa: E501
        :rtype: list[str]
        """
        return self._sender_provided_numbers

    @sender_provided_numbers.setter
    def sender_provided_numbers(self, sender_provided_numbers):
        """Sets the sender_provided_numbers of this RecipientPhoneAuthentication.

        An Array containing a list of phone numbers the recipient may use for SMS text authentication.   # noqa: E501

        :param sender_provided_numbers: The sender_provided_numbers of this RecipientPhoneAuthentication.  # noqa: E501
        :type: list[str]
        """

        self._sender_provided_numbers = sender_provided_numbers

    @property
    def validate_recip_provided_number(self):
        """Gets the validate_recip_provided_number of this RecipientPhoneAuthentication.  # noqa: E501

         Reserved.  # noqa: E501

        :return: The validate_recip_provided_number of this RecipientPhoneAuthentication.  # noqa: E501
        :rtype: str
        """
        return self._validate_recip_provided_number

    @validate_recip_provided_number.setter
    def validate_recip_provided_number(self, validate_recip_provided_number):
        """Sets the validate_recip_provided_number of this RecipientPhoneAuthentication.

         Reserved.  # noqa: E501

        :param validate_recip_provided_number: The validate_recip_provided_number of this RecipientPhoneAuthentication.  # noqa: E501
        :type: str
        """

        self._validate_recip_provided_number = validate_recip_provided_number

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
        if issubclass(RecipientPhoneAuthentication, dict):
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
        if not isinstance(other, RecipientPhoneAuthentication):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
