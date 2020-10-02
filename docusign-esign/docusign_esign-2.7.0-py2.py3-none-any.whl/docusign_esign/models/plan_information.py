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


class PlanInformation(object):
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
        'add_ons': 'list[AddOn]',
        'currency_code': 'str',
        'free_trial_days_override': 'str',
        'plan_feature_sets': 'list[FeatureSet]',
        'plan_id': 'str',
        'recipient_domains': 'list[RecipientDomain]'
    }

    attribute_map = {
        'add_ons': 'addOns',
        'currency_code': 'currencyCode',
        'free_trial_days_override': 'freeTrialDaysOverride',
        'plan_feature_sets': 'planFeatureSets',
        'plan_id': 'planId',
        'recipient_domains': 'recipientDomains'
    }

    def __init__(self, add_ons=None, currency_code=None, free_trial_days_override=None, plan_feature_sets=None, plan_id=None, recipient_domains=None):  # noqa: E501
        """PlanInformation - a model defined in Swagger"""  # noqa: E501

        self._add_ons = None
        self._currency_code = None
        self._free_trial_days_override = None
        self._plan_feature_sets = None
        self._plan_id = None
        self._recipient_domains = None
        self.discriminator = None

        if add_ons is not None:
            self.add_ons = add_ons
        if currency_code is not None:
            self.currency_code = currency_code
        if free_trial_days_override is not None:
            self.free_trial_days_override = free_trial_days_override
        if plan_feature_sets is not None:
            self.plan_feature_sets = plan_feature_sets
        if plan_id is not None:
            self.plan_id = plan_id
        if recipient_domains is not None:
            self.recipient_domains = recipient_domains

    @property
    def add_ons(self):
        """Gets the add_ons of this PlanInformation.  # noqa: E501

        Reserved:  # noqa: E501

        :return: The add_ons of this PlanInformation.  # noqa: E501
        :rtype: list[AddOn]
        """
        return self._add_ons

    @add_ons.setter
    def add_ons(self, add_ons):
        """Sets the add_ons of this PlanInformation.

        Reserved:  # noqa: E501

        :param add_ons: The add_ons of this PlanInformation.  # noqa: E501
        :type: list[AddOn]
        """

        self._add_ons = add_ons

    @property
    def currency_code(self):
        """Gets the currency_code of this PlanInformation.  # noqa: E501

        Specifies the ISO currency code for the account.  # noqa: E501

        :return: The currency_code of this PlanInformation.  # noqa: E501
        :rtype: str
        """
        return self._currency_code

    @currency_code.setter
    def currency_code(self, currency_code):
        """Sets the currency_code of this PlanInformation.

        Specifies the ISO currency code for the account.  # noqa: E501

        :param currency_code: The currency_code of this PlanInformation.  # noqa: E501
        :type: str
        """

        self._currency_code = currency_code

    @property
    def free_trial_days_override(self):
        """Gets the free_trial_days_override of this PlanInformation.  # noqa: E501

        Reserved for DocuSign use only.  # noqa: E501

        :return: The free_trial_days_override of this PlanInformation.  # noqa: E501
        :rtype: str
        """
        return self._free_trial_days_override

    @free_trial_days_override.setter
    def free_trial_days_override(self, free_trial_days_override):
        """Sets the free_trial_days_override of this PlanInformation.

        Reserved for DocuSign use only.  # noqa: E501

        :param free_trial_days_override: The free_trial_days_override of this PlanInformation.  # noqa: E501
        :type: str
        """

        self._free_trial_days_override = free_trial_days_override

    @property
    def plan_feature_sets(self):
        """Gets the plan_feature_sets of this PlanInformation.  # noqa: E501

        A complex type that sets the feature sets for the account.  # noqa: E501

        :return: The plan_feature_sets of this PlanInformation.  # noqa: E501
        :rtype: list[FeatureSet]
        """
        return self._plan_feature_sets

    @plan_feature_sets.setter
    def plan_feature_sets(self, plan_feature_sets):
        """Sets the plan_feature_sets of this PlanInformation.

        A complex type that sets the feature sets for the account.  # noqa: E501

        :param plan_feature_sets: The plan_feature_sets of this PlanInformation.  # noqa: E501
        :type: list[FeatureSet]
        """

        self._plan_feature_sets = plan_feature_sets

    @property
    def plan_id(self):
        """Gets the plan_id of this PlanInformation.  # noqa: E501

        The DocuSign Plan ID for the account.  # noqa: E501

        :return: The plan_id of this PlanInformation.  # noqa: E501
        :rtype: str
        """
        return self._plan_id

    @plan_id.setter
    def plan_id(self, plan_id):
        """Sets the plan_id of this PlanInformation.

        The DocuSign Plan ID for the account.  # noqa: E501

        :param plan_id: The plan_id of this PlanInformation.  # noqa: E501
        :type: str
        """

        self._plan_id = plan_id

    @property
    def recipient_domains(self):
        """Gets the recipient_domains of this PlanInformation.  # noqa: E501

          # noqa: E501

        :return: The recipient_domains of this PlanInformation.  # noqa: E501
        :rtype: list[RecipientDomain]
        """
        return self._recipient_domains

    @recipient_domains.setter
    def recipient_domains(self, recipient_domains):
        """Sets the recipient_domains of this PlanInformation.

          # noqa: E501

        :param recipient_domains: The recipient_domains of this PlanInformation.  # noqa: E501
        :type: list[RecipientDomain]
        """

        self._recipient_domains = recipient_domains

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
        if issubclass(PlanInformation, dict):
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
        if not isinstance(other, PlanInformation):
            return False

        return self.__dict__ == other.__dict__

    def __ne__(self, other):
        """Returns true if both objects are not equal"""
        return not self == other
