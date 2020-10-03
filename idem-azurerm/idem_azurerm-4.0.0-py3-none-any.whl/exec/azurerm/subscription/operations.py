# -*- coding: utf-8 -*-
"""
Azure Resource Manager (ARM) Resource Subscription Execution Module

.. versionadded:: 4.0.0

:maintainer: <devops@eitr.tech>
:configuration: This module requires Azure Resource Manager credentials to be passed as keyword arguments
    to every function or via acct in order to work properly.

    Required provider parameters:

    if using username and password:
      * ``subscription_id``
      * ``username``
      * ``password``

    if using a service principal:
      * ``subscription_id``
      * ``tenant``
      * ``client_id``
      * ``secret``

    Optional provider parameters:

**cloud_environment**: Used to point the cloud driver to different API endpoints, such as Azure GovCloud.
    Possible values:
      * ``AZURE_PUBLIC_CLOUD`` (default)
      * ``AZURE_CHINA_CLOUD``
      * ``AZURE_US_GOV_CLOUD``
      * ``AZURE_GERMAN_CLOUD``

"""
# Python libs
import logging

# Azure libs
HAS_LIBS = False
try:
    import azure.mgmt.subscription.models  # pylint: disable=unused-import
    from msrest.exceptions import SerializationError, ValidationError
    from msrestazure.azure_exceptions import CloudError

    HAS_LIBS = True
except ImportError:
    pass

__func_alias__ = {"list_": "list"}

log = logging.getLogger(__name__)


async def list_locations(hub, ctx, subscription_id=None, **kwargs):
    """
    .. versionadded:: 4.0.0

    List all locations for a subscription.

    :param subscription_id: The ID of the subscription to query.

    CLI Example:

    .. code-block:: bash

        azurerm.subscription.operations.list_locations XXXXXXXX

    """
    result = {}

    if not subscription_id:
        subscription_id = ctx["acct"].get("subscription_id")

    subconn = await hub.exec.azurerm.utils.get_client(ctx, "subscription", **kwargs)
    try:
        locations = await hub.exec.azurerm.utils.paged_object_to_list(
            subconn.subscriptions.list_locations(
                subscription_id=subscription_id
            )
        )

        for loc in locations:
            result[loc["name"]] = loc
    except (CloudError, ValidationError) as exc:
        await hub.exec.azurerm.utils.log_cloud_error("subscription", str(exc), **kwargs)
        result = {"error": str(exc)}

    return result


async def get(hub, ctx, subscription_id=None, **kwargs):
    """
    .. versionadded:: 4.0.0

    Get details about a subscription.

    :param subscription_id: The ID of the subscription to query.

    CLI Example:

    .. code-block:: bash

        azurerm.subscription.operations.get XXXXXXXX

    """
    result = {}

    if not subscription_id:
        subscription_id = ctx["acct"].get("subscription_id")

    subconn = await hub.exec.azurerm.utils.get_client(ctx, "subscription", **kwargs)
    try:
        subscription = subconn.subscriptions.get(
            subscription_id=subscription_id
        )

        result = subscription.as_dict()
    except (CloudError, ValidationError) as exc:
        await hub.exec.azurerm.utils.log_cloud_error("subscription", str(exc), **kwargs)
        result = {"error": str(exc)}

    return result


async def list_(hub, ctx, **kwargs):
    """
    .. versionadded:: 4.0.0

    List all subscriptions for a tenant.

    CLI Example:

    .. code-block:: bash

        azurerm.subscription.operations.list

    """
    result = {}
    subconn = await hub.exec.azurerm.utils.get_client(ctx, "subscription", **kwargs)
    try:
        subs = await hub.exec.azurerm.utils.paged_object_to_list(
            subconn.subscriptions.list()
        )

        for sub in subs:
            result[sub["subscription_id"]] = sub
    except CloudError as exc:
        await hub.exec.azurerm.utils.log_cloud_error("subscription", str(exc), **kwargs)
        result = {"error": str(exc)}

    return result


async def create_csp(hub, ctx, name, customer_name, billing_account, sku, reseller_id=None, **kwargs):
    """
    .. versionadded:: 4.0.0

    Creates an Azure subscription.

    CLI Example:

    .. code-block:: bash

        azurerm.subscription.operations.list

    """
    result = {}

    subconn = await hub.exec.azurerm.utils.get_client(ctx, "subscription", **kwargs)

    params = {
        "display_name": name,
        "sku_id": sku,
        "reseller_id": reseller_id,
    }

    try:
        sub = subconn.subscriptions.create_csp_subscription(
            billing_account_name=billing_account,
            customer_name=customer_name,
            body=params,
        )

        result = sub.as_dict()
    except CloudError as exc:
        await hub.exec.azurerm.utils.log_cloud_error("subscription", str(exc), **kwargs)
        result = {"error": str(exc)}

    return result


async def create_ea(hub, ctx, name, enrollment_account, offer_type, management_group_id=None, owners=None, **kwargs):
    """
    .. versionadded:: 4.0.0

    Creates an Azure subscription.

    CLI Example:

    .. code-block:: bash

        azurerm.subscription.operations.list

    """
    result = {}

    subconn = await hub.exec.azurerm.utils.get_client(ctx, "subscription", **kwargs)

    params = {
        "display_name": name,
        "management_group_id": management_group_id,
        "owners": owners,
        "offer_type": offer_type,
        "additional_parameters": None,
    }

    try:
        sub = subconn.subscriptions.create_subscription_in_enrollment_account(
            enrollment_account_name=enrollment_account,
            body=params,
        )

        result = sub.as_dict()
    except CloudError as exc:
        await hub.exec.azurerm.utils.log_cloud_error("subscription", str(exc), **kwargs)
        result = {"error": str(exc)}

    return result


async def create(hub, ctx, name, billing_account, billing_profile, invoice_section, sku, cost_center=None, owner=None, management_group_id=None, **kwargs):
    """
    .. versionadded:: 4.0.0

    Creates an Azure subscription.

    CLI Example:

    .. code-block:: bash

        azurerm.subscription.operations.list

    """
    result = {}

    subconn = await hub.exec.azurerm.utils.get_client(ctx, "subscription", **kwargs)

    params = {
        "display_name": name,
        "sku_id": sku,
        "cost_center": cost_center,
        "owner": {"object_id": owner},
        "management_group_id": management_group_id,
        "additional_parameters": None,
    }

    try:
        sub = subconn.subscriptions.create_subscription(
            billing_account_name=billing_account,
            billing_profile_name=billing_profile,
            invoice_section_name=invoice_section,
            body=params,
        )

        result = sub.as_dict()
    except CloudError as exc:
        await hub.exec.azurerm.utils.log_cloud_error("subscription", str(exc), **kwargs)
        result = {"error": str(exc)}

    return result
