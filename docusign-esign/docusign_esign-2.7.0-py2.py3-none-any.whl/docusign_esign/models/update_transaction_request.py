# coding: utf-8

"""
    DocuSign REST API

    The DocuSign REST API provides you with a powerful, convenient, and simple Web services API for interacting with DocuSign.

    OpenAPI spec version: v2
    Contact: devcenter@docusign.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from pprint import pformat
from six import iteritems
import re


class UpdateTransactionRequest(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    """
    def __init__(self, code=None, message=None, state=None):
        """
        UpdateTransactionRequest - a model defined in Swagger

        :param dict swaggerTypes: The key is attribute name
                                  and the value is attribute type.
        :param dict attributeMap: The key is attribute name
                                  and the value is json key in definition.
        """
        self.swagger_types = {
            'code': 'str',
            'message': 'str',
            'state': 'str'
        }

        self.attribute_map = {
            'code': 'code',
            'message': 'message',
            'state': 'state'
        }

        self._code = code
        self._message = message
        self._state = state

    @property
    def code(self):
        """
        Gets the code of this UpdateTransactionRequest.
        

        :return: The code of this UpdateTransactionRequest.
        :rtype: str
        """
        return self._code

    @code.setter
    def code(self, code):
        """
        Sets the code of this UpdateTransactionRequest.
        

        :param code: The code of this UpdateTransactionRequest.
        :type: str
        """

        self._code = code

    @property
    def message(self):
        """
        Gets the message of this UpdateTransactionRequest.
        

        :return: The message of this UpdateTransactionRequest.
        :rtype: str
        """
        return self._message

    @message.setter
    def message(self, message):
        """
        Sets the message of this UpdateTransactionRequest.
        

        :param message: The message of this UpdateTransactionRequest.
        :type: str
        """

        self._message = message

    @property
    def state(self):
        """
        Gets the state of this UpdateTransactionRequest.
        The state or province associated with the address.

        :return: The state of this UpdateTransactionRequest.
        :rtype: str
        """
        return self._state

    @state.setter
    def state(self, state):
        """
        Sets the state of this UpdateTransactionRequest.
        The state or province associated with the address.

        :param state: The state of this UpdateTransactionRequest.
        :type: str
        """

        self._state = state

    def to_dict(self):
        """
        Returns the model properties as a dict
        """
        result = {}

        for attr, _ in iteritems(self.swagger_types):
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

        return result

    def to_str(self):
        """
        Returns the string representation of the model
        """
        return pformat(self.to_dict())

    def __repr__(self):
        """
        For `print` and `pprint`
        """
        return self.to_str()

    def __eq__(self, other):
        """
        Returns true if both objects are equal
        """
        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """
        Returns true if both objects are not equal
        """
        return not self == other
