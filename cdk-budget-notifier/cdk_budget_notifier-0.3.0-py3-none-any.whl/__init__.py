"""
# AWS Budget Notifier

Setup a AWS Budget notification using AWS Cloud Development Kit (CDK).
The construct supports notifying to

* users via e-mail. Up to 10 e-mail addresses are supported
* an SNS topic<br>
  The SNS topic needs to exist and publishing to the topic needs to be allowed.

## Example usage in a CDK Stack

```javascript
const app = new cdk.App();
const stack = new Stack(app, "BudgetNotifierStack");

// Define the SNS topic and setup the resource policy
const topic = new Topic(stack, "topic");

const statement = new PolicyStatement({
  effect: Effect.ALLOW,
  principals: [new ServicePrincipal("budgets.amazonaws.com")],
  actions: ["SNS:Publish"],
  sid: "Allow budget to publish to SNS"
});
topic.addToResourcePolicy(statement);

// Setup the budget notifier and pass the ARN of the SNS topic
new BudgetNotifier(stack, "notifier", {
  topicArn: topic.topicArn,
  availabilityZones: ["eu-central-1"],
  costCenter: "myCostCenter",
  limit: 10,
  unit: "USD",
  threshold: 15,
  notificationType: NotificationType.FORECASTED,
});

```

## Links

* [AWS Cloud Development Kit (CDK)](https://github.com/aws/aws-cdk)
* [Cost Explorer filters](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/ce-filtering.html)
"""
import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from ._jsii import *

import aws_cdk.core


class BudgetNotifier(
    aws_cdk.core.Construct,
    metaclass=jsii.JSIIMeta,
    jsii_type="@stefanfreitag/aws-budget-notifier.BudgetNotifier",
):
    """
    :stability: experimental
    """

    def __init__(
        self,
        scope: aws_cdk.core.Construct,
        id: builtins.str,
        *,
        limit: jsii.Number,
        threshold: jsii.Number,
        unit: builtins.str,
        application: typing.Optional[builtins.str] = None,
        availability_zones: typing.Optional[typing.List[builtins.str]] = None,
        cost_center: typing.Optional[builtins.str] = None,
        notification_type: typing.Optional["NotificationType"] = None,
        recipients: typing.Optional[typing.List[builtins.str]] = None,
        service: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional["TimeUnit"] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        """
        :param scope: -
        :param id: -
        :param limit: (experimental) The cost associated with the budget threshold.
        :param threshold: (experimental) The threshold value in percent (0-100).
        :param unit: (experimental) The unit of measurement that is used for the budget threshold, such as dollars or GB.
        :param application: (experimental) If specified the application name will be added as tag filter.
        :param availability_zones: (experimental) If specified the availability zones will be added as tag filter.
        :param cost_center: (experimental) If specified the cost center will be added as tag filter.
        :param notification_type: (experimental) Whether the notification is for how much you have spent (ACTUAL) or for how much you're forecasted to spend (FORECASTED).
        :param recipients: (experimental) Budget notifications will be sent to each of the recipients (e-mail addresses). A maximum of 10 recipients is allowed.
        :param service: (experimental) If specified the service will be added as tag filter.
        :param time_unit: (experimental) The length of time until a budget resets the actual and forecasted spend.
        :param topic_arn: 

        :stability: experimental
        """
        props = BudgetNotifierProps(
            limit=limit,
            threshold=threshold,
            unit=unit,
            application=application,
            availability_zones=availability_zones,
            cost_center=cost_center,
            notification_type=notification_type,
            recipients=recipients,
            service=service,
            time_unit=time_unit,
            topic_arn=topic_arn,
        )

        jsii.create(BudgetNotifier, self, [scope, id, props])


@jsii.data_type(
    jsii_type="@stefanfreitag/aws-budget-notifier.BudgetNotifierProps",
    jsii_struct_bases=[],
    name_mapping={
        "limit": "limit",
        "threshold": "threshold",
        "unit": "unit",
        "application": "application",
        "availability_zones": "availabilityZones",
        "cost_center": "costCenter",
        "notification_type": "notificationType",
        "recipients": "recipients",
        "service": "service",
        "time_unit": "timeUnit",
        "topic_arn": "topicArn",
    },
)
class BudgetNotifierProps:
    def __init__(
        self,
        *,
        limit: jsii.Number,
        threshold: jsii.Number,
        unit: builtins.str,
        application: typing.Optional[builtins.str] = None,
        availability_zones: typing.Optional[typing.List[builtins.str]] = None,
        cost_center: typing.Optional[builtins.str] = None,
        notification_type: typing.Optional["NotificationType"] = None,
        recipients: typing.Optional[typing.List[builtins.str]] = None,
        service: typing.Optional[builtins.str] = None,
        time_unit: typing.Optional["TimeUnit"] = None,
        topic_arn: typing.Optional[builtins.str] = None,
    ) -> None:
        """(experimental) Configuration options of the {@link BudgetNotifier | BudgetNotifier}.

        :param limit: (experimental) The cost associated with the budget threshold.
        :param threshold: (experimental) The threshold value in percent (0-100).
        :param unit: (experimental) The unit of measurement that is used for the budget threshold, such as dollars or GB.
        :param application: (experimental) If specified the application name will be added as tag filter.
        :param availability_zones: (experimental) If specified the availability zones will be added as tag filter.
        :param cost_center: (experimental) If specified the cost center will be added as tag filter.
        :param notification_type: (experimental) Whether the notification is for how much you have spent (ACTUAL) or for how much you're forecasted to spend (FORECASTED).
        :param recipients: (experimental) Budget notifications will be sent to each of the recipients (e-mail addresses). A maximum of 10 recipients is allowed.
        :param service: (experimental) If specified the service will be added as tag filter.
        :param time_unit: (experimental) The length of time until a budget resets the actual and forecasted spend.
        :param topic_arn: 

        :stability: experimental
        """
        self._values: typing.Dict[str, typing.Any] = {
            "limit": limit,
            "threshold": threshold,
            "unit": unit,
        }
        if application is not None:
            self._values["application"] = application
        if availability_zones is not None:
            self._values["availability_zones"] = availability_zones
        if cost_center is not None:
            self._values["cost_center"] = cost_center
        if notification_type is not None:
            self._values["notification_type"] = notification_type
        if recipients is not None:
            self._values["recipients"] = recipients
        if service is not None:
            self._values["service"] = service
        if time_unit is not None:
            self._values["time_unit"] = time_unit
        if topic_arn is not None:
            self._values["topic_arn"] = topic_arn

    @builtins.property
    def limit(self) -> jsii.Number:
        """(experimental) The cost associated with the budget threshold.

        :stability: experimental
        """
        result = self._values.get("limit")
        assert result is not None, "Required property 'limit' is missing"
        return result

    @builtins.property
    def threshold(self) -> jsii.Number:
        """(experimental) The threshold value in percent (0-100).

        :stability: experimental
        """
        result = self._values.get("threshold")
        assert result is not None, "Required property 'threshold' is missing"
        return result

    @builtins.property
    def unit(self) -> builtins.str:
        """(experimental) The unit of measurement that is used for the budget threshold, such as dollars or GB.

        :stability: experimental
        """
        result = self._values.get("unit")
        assert result is not None, "Required property 'unit' is missing"
        return result

    @builtins.property
    def application(self) -> typing.Optional[builtins.str]:
        """(experimental) If specified the application name will be added as tag filter.

        :stability: experimental
        """
        result = self._values.get("application")
        return result

    @builtins.property
    def availability_zones(self) -> typing.Optional[typing.List[builtins.str]]:
        """(experimental) If specified the availability zones will be added as tag filter.

        :stability: experimental
        """
        result = self._values.get("availability_zones")
        return result

    @builtins.property
    def cost_center(self) -> typing.Optional[builtins.str]:
        """(experimental) If specified the cost center will be added as tag filter.

        :stability: experimental
        """
        result = self._values.get("cost_center")
        return result

    @builtins.property
    def notification_type(self) -> typing.Optional["NotificationType"]:
        """(experimental) Whether the notification is for how much you have spent (ACTUAL) or for how much you're forecasted to spend (FORECASTED).

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-notification.html#cfn-budgets-budget-notification-notificationtype
        :stability: experimental
        """
        result = self._values.get("notification_type")
        return result

    @builtins.property
    def recipients(self) -> typing.Optional[typing.List[builtins.str]]:
        """(experimental) Budget notifications will be sent to each of the recipients (e-mail addresses).

        A maximum of 10 recipients is allowed.

        :stability: experimental
        """
        result = self._values.get("recipients")
        return result

    @builtins.property
    def service(self) -> typing.Optional[builtins.str]:
        """(experimental) If specified the service will be added as tag filter.

        :stability: experimental
        """
        result = self._values.get("service")
        return result

    @builtins.property
    def time_unit(self) -> typing.Optional["TimeUnit"]:
        """(experimental) The length of time until a budget resets the actual and forecasted spend.

        :see: http://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-properties-budgets-budget-budgetdata.html#cfn-budgets-budget-budgetdata-timeunit
        :stability: experimental
        """
        result = self._values.get("time_unit")
        return result

    @builtins.property
    def topic_arn(self) -> typing.Optional[builtins.str]:
        """
        :stability: experimental
        """
        result = self._values.get("topic_arn")
        return result

    def __eq__(self, rhs: typing.Any) -> builtins.bool:
        return isinstance(rhs, self.__class__) and rhs._values == self._values

    def __ne__(self, rhs: typing.Any) -> builtins.bool:
        return not (rhs == self)

    def __repr__(self) -> str:
        return "BudgetNotifierProps(%s)" % ", ".join(
            k + "=" + repr(v) for k, v in self._values.items()
        )


@jsii.enum(jsii_type="@stefanfreitag/aws-budget-notifier.NotificationType")
class NotificationType(enum.Enum):
    """
    :stability: experimental
    """

    ACTUAL = "ACTUAL"
    """
    :stability: experimental
    """
    FORECASTED = "FORECASTED"
    """
    :stability: experimental
    """


@jsii.enum(jsii_type="@stefanfreitag/aws-budget-notifier.TimeUnit")
class TimeUnit(enum.Enum):
    """
    :stability: experimental
    """

    MONTHLY = "MONTHLY"
    """
    :stability: experimental
    """
    QUARTERLY = "QUARTERLY"
    """
    :stability: experimental
    """
    ANNUALLY = "ANNUALLY"
    """
    :stability: experimental
    """


__all__ = [
    "BudgetNotifier",
    "BudgetNotifierProps",
    "NotificationType",
    "TimeUnit",
]

publication.publish()
