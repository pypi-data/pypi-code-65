# coding: utf-8

"""
    DocuSign REST API

    The DocuSign REST API provides you with a powerful, convenient, and simple Web services API for interacting with DocuSign.  # noqa: E501

    OpenAPI spec version: v2.1
    Contact: devcenter@docusign.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


import pprint
import re  # noqa: F401

import six


class BulkRecipientsSummaryResponse(object):
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
        'bulk_recipients': 'list[BulkRecipient]',
        'bulk_recipients_count': 'str',
        'bulk_recipients_uri': 'str',
        'error_details': 'list[ErrorDetails]'
    }

    attribute_map = {
        'bulk_recipients': 'bulkRecipients',
        'bulk_recipients_count': 'bulkRecipientsCount',
        'bulk_recipients_uri': 'bulkRecipientsUri',
        'error_details': 'errorDetails'
    }

    def __init__(self, bulk_recipients=None, bulk_recipients_count=None, bulk_recipients_uri=None, error_details=None):  # noqa: E501
        """BulkRecipientsSummaryResponse - a model defined in Swagger"""  # noqa: E501

        self._bulk_recipients = None
        self._bulk_recipients_count = None
        self._bulk_recipients_uri = None
        self._error_details = None
        self.discriminator = None

        if bulk_recipients is not None:
            self.bulk_recipients = bulk_recipients
        if bulk_recipients_count is not None:
            self.bulk_recipients_count = bulk_recipients_count
        if bulk_recipients_uri is not None:
            self.bulk_recipients_uri = bulk_recipients_uri
        if error_details is not None:
            self.error_details = error_details

    @property
    def bulk_recipients(self):
        """Gets the bulk_recipients of this BulkRecipientsSummaryResponse.  # noqa: E501

        A complex type containing information about the bulk recipients in the response.  # noqa: E501

        :return: The bulk_recipients of this BulkRecipientsSummaryResponse.  # noqa: E501
        :rtype: list[BulkRecipient]
        """
        return self._bulk_recipients

    @bulk_recipients.setter
    def bulk_recipients(self, bulk_recipients):
        """Sets the bulk_recipients of this BulkRecipientsSummaryResponse.

        A complex type containing information about the bulk recipients in the response.  # noqa: E501

        :param bulk_recipients: The bulk_recipients of this BulkRecipientsSummaryResponse.  # noqa: E501
        :type: list[BulkRecipient]
        """

        self._bulk_recipients = bulk_recipients

    @property
    def bulk_recipients_count(self):
        """Gets the bulk_recipients_count of this BulkRecipientsSummaryResponse.  # noqa: E501

        The number of items returned in this response.  # noqa: E501

        :return: The bulk_recipients_count of this BulkRecipientsSummaryResponse.  # noqa: E501
        :rtype: str
        """
        return self._bulk_recipients_count

    @bulk_recipients_count.setter
    def bulk_recipients_count(self, bulk_recipients_count):
        """Sets the bulk_recipients_count of this BulkRecipientsSummaryResponse.

        The number of items returned in this response.  # noqa: E501

        :param bulk_recipients_count: The bulk_recipients_count of this BulkRecipientsSummaryResponse.  # noqa: E501
        :type: str
        """

        self._bulk_recipients_count = bulk_recipients_count

    @property
    def bulk_recipients_uri(self):
        """Gets the bulk_recipients_uri of this BulkRecipientsSummaryResponse.  # noqa: E501

        Contains a URI for an endpoint that allows you to easily retrieve bulk recipient information.  # noqa: E501

        :return: The bulk_recipients_uri of this BulkRecipientsSummaryResponse.  # noqa: E501
        :rtype: str
        """
        return self._bulk_recipients_uri

    @bulk_recipients_uri.setter
    def bulk_recipients_uri(self, bulk_recipients_uri):
        """Sets the bulk_recipients_uri of this BulkRecipientsSummaryResponse.

        Contains a URI for an endpoint that allows you to easily retrieve bulk recipient information.  # noqa: E501

        :param bulk_recipients_uri: The bulk_recipients_uri of this BulkRecipientsSummaryResponse.  # noqa: E501
        :type: str
        """

        self._bulk_recipients_uri = bulk_recipients_uri

    @property
    def error_details(self):
        """Gets the error_details of this BulkRecipientsSummaryResponse.  # noqa: E501

        Array or errors.  # noqa: E501

        :return: The error_details of this BulkRecipientsSummaryResponse.  # noqa: E501
        :rtype: list[ErrorDetails]
        """
        return self._error_details

    @error_details.setter
    def error_details(self, error_details):
        """Sets the error_details of this BulkRecipientsSummaryResponse.

        Array or errors.  # noqa: E501

        :param error_details: The error_details of this BulkRecipientsSummaryResponse.  # noqa: E501
        :type: list[ErrorDetails]
        """

        self._error_details = error_details

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
        if issubclass(BulkRecipientsSummaryResponse, dict):
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
        if not isinstance(other, BulkRecipientsSummaryResponse):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
