import click
import uuid
import json
import random
import requests

from spell.cli.exceptions import (
    api_client_exception_handler,
    ExitException,
)
from spell.cli.utils import cluster_utils

DEFAULT_REGION = "westus2"
CONTAINER_NAME = "spell-blob-container"

required_permissions = [
    "Microsoft.Compute/*",
    "Microsoft.Network/*",
    "Microsoft.Storage/*",
    "Microsoft.Support/*",
    "Microsoft.Authorization/*/read",
    "Microsoft.Resources/deployments/*",
    "Microsoft.Resources/subscriptions/resourceGroups/read",
]


@click.command(name="az", short_help="Sets up an Azure VNet as a Spell cluster", hidden=True)
@click.pass_context
@click.option(
    "-n", "--name", "name", help="This will be used by Spell for you to identify the cluster"
)
@click.option("-r", "--resource-group", "resource_group_name",
              help="This will be the name of the Resource Group Spell will create and "
                   "store all its resources in within your Azure account",
              default="spell-resource-group")
@click.option("-s", "--service-principal", "service_principal_name",
              help="Command to name your Service Principal",
              default="spell-sp")
def create_azure(ctx, name, resource_group_name, service_principal_name):
    """
    This command creates an Azure VNet of your choosing as an external Spell cluster.
    This will let your organization create runs in that VNet, so your data never leaves
    your VNet. You create an Azure Blob Container of your choosing for all run outputs to be written to.
    After this cluster is set up you will be able to select the types and number of machines
    you would like Spell to create in this cluster.
    """

    # Verify the owner is the admin of an org
    spell_client = ctx.obj["client"]
    cluster_utils.validate_org_perms(spell_client, ctx.obj["owner"])

    try:
        from azure.mgmt.resource import ResourceManagementClient
        from azure.mgmt.resource.subscriptions import SubscriptionClient
        from azure.mgmt.authorization import AuthorizationManagementClient
        from azure.mgmt.storage import StorageManagementClient
        from azure.mgmt.storage.models import StorageAccountCreateParameters, Sku, SkuName, Kind
        from spell.cli.utils.azure_credential_wrapper import AzureIdentityCredentialAdapter
        from azure.common.client_factory import get_client_from_cli_profile
        from azure.graphrbac import GraphRbacManagementClient
        from azure.core.exceptions import ClientAuthenticationError
        from azure.storage.blob import BlobServiceClient

    except ImportError:
        click.echo("Please `pip install --upgrade 'spell[cluster-azure]'` and rerun this command")
        return

    click.echo(
        """This command will help you
        - Select a region to create resources in and a subscription for billing
        - Create an App and Service Principal
        - Create a Resource group in the specified region to manage your resources
        - Assign a role to your Service Principal that allows Spell to spin up and
            down machines and access your Blobs
        - Create a uniquely-named storage account
        - Set up an Blob Container to store your run outputs in
        - (TODO): Set up a VNet which Spell will spin up workers in to run your jobs
        - (TODO): Ensure subnets in the VNet in multiple availability zones
        - (TODO): Set up a Security Group providing Spell SSH and Docker access to workers """
    )

    # Create Credentials
    try:
        credentials = AzureIdentityCredentialAdapter()
        credentials.set_token()
        graph_credentials = AzureIdentityCredentialAdapter(resource_id="https://graph.microsoft.com/")
        graph_credentials.set_token()
    except ClientAuthenticationError:
        click.echo("Make sure you are logged into Azure locally. This can be done with `az login` or \
            by running on an Azure compute instance")
        return

    # Validate cluster name
    cluster_utils.echo_delimiter()
    if not name:
        name = click.prompt("Enter a display name for this Azure cluster within Spell")

    with api_client_exception_handler():
        spell_client.validate_cluster_name(name)

    # Queries for Subscription Id
    subscription_client = SubscriptionClient(credentials)
    subscription_id = get_subscription(credentials, subscription_client)
    if subscription_id is None:
        raise ExitException("No active subscriptions found")

    # Get Region
    available_regions = [location.name for location in subscription_client.subscriptions
                         .list_locations(subscription_id)]
    cluster_utils.echo_delimiter()
    region = click.prompt(
        "Please choose a region for your cluster. This might affect machine availability",
        type=click.Choice(available_regions), default=DEFAULT_REGION
    )
    supports_no_gpu = region in (
        "canadaeast",
        "centralus",
        "westcentralus",
        "southafricawest",
        "eastasia",
        "australiacentral",
        "australiacentral2",
        "australiasoutheast",
        "brazilsoutheast",
        "chinaeast",
        "chinanorth",
        "francesouth",
        "germany",
        "germanycentral",
        "germanynorth",
        "germanywestcentral",
        "southindia",
        "westindia",
        "japanwest",
        "koreasouth",
        "switzerlandnorth",
        "switzerlandwest",
        "uaecentral",
        "ukwest",
    )
    if supports_no_gpu:
        if not click.confirm(
            "Azure does not support GPU types in {}. You can still create a cluster, but it will "
            "only have access to CPU types - continue?".format(region)
        ):
            return

    # Create Service Principal
    graphrbac_client = get_client_from_cli_profile(GraphRbacManagementClient)
    client_id, object_id = create_service_principal(graphrbac_client, service_principal_name)
    client_secret, end_date = set_client_secret(graph_credentials, object_id)

    # Create Resource Group
    resource_client = ResourceManagementClient(credentials, subscription_id)
    if resource_client.resource_groups.check_existence(resource_group_name):
        raise ExitException("Resource group `{}` already exists - "
                            "please select a different name".format(resource_group_name))
    resource_group = resource_client.resource_groups.create_or_update(resource_group_name, {"location": region})

    # Creates and Assigns Custom Role to Service Principal
    authorization_client = AuthorizationManagementClient(credentials, subscription_id)
    create_and_assign_role(credentials, subscription_id, resource_group.id, object_id, authorization_client)

    # Creates Storage Account
    storage_client = StorageManagementClient(credentials, subscription_id)
    params = StorageAccountCreateParameters(
        sku=Sku(name=SkuName.standard_ragrs),
        kind=Kind.storage,
        location=region,
    )
    storage_account, storage_account_name = create_storage_account(storage_client, name, resource_group_name, params)

    # Get Storage Key
    list_keys = storage_client.storage_accounts.list_keys(resource_group_name, storage_account_name)
    storage_keys = {v.key_name: v.value for v in list_keys.keys}
    storage_key = storage_keys["key1"]

    # Creates Blob Container
    blob_service_client = BlobServiceClient(account_url=storage_account.primary_endpoints.blob,
                                            credential=storage_key)
    create_blob_container(storage_account, storage_account_name, blob_service_client)

    with api_client_exception_handler():
        cluster = spell_client.create_azure_cluster(
            name,
            client_id,
            client_secret,
            end_date,
            subscription_id,
            region,
            storage_account_name,
            resource_group_name,
        )
        cluster_utils.echo_delimiter()
        url = "{}/{}/clusters/{}".format(ctx.obj["web_url"], ctx.obj["owner"], cluster["name"])
        click.echo(
            "Your cluster {} is initialized! Head over to the web console to create machine types "
            "to execute your runs on - {}".format(name, url)
        )


def get_subscription(credentials, client):

    sub_ids = [sub.subscription_id for sub in client.subscriptions.list() if sub.state == "Enabled"]
    if not sub_ids:
        return None
    elif len(sub_ids) == 1:
        click.echo("One Subscription found: {}. "
                   "Defaulting to this subscription for this cluster".format(sub_ids[0]))
        return sub_ids[0]
    else:
        cluster_utils.echo_delimiter()
        return click.prompt(
            "Please choose a subscription id from your active subscriptions",
            type=click.Choice(sub_ids),
        )


def create_service_principal(client, service_principal_name):
    """
    Creates an App `spell-sp` and Service Principal
    Returns the client id aka. appID and object id of the sp
    TODO(sruthi): Switch to use Microsoft Graph REST API instead of deprecated AD Graph API
    """

    cluster_utils.echo_delimiter()
    click.echo("Creating Service Principal")
    app = client.applications.create({
        "available_to_other_tenants": False,
        "display_name": service_principal_name,
    })
    sp = client.service_principals.create({
        "app_id": app.app_id,
        "account_enabled": True
    })
    client_id = app.app_id
    object_id = sp.object_id
    click.echo("Service Principal `{}` Created!".format(service_principal_name))
    return client_id, object_id


def set_client_secret(credentials, object_id):
    """
    Uses Microsoft Graph REST API to generate a client secret
    Returns the client secret and the end date (date the client secret expires)

    NOTE: There is no Python client library for this, so we do raw HTTP requests to the API.
    In the future we will use the python client API that has not yet been released.
    """

    # Create Request
    header = {"Content-Type": "application/json",
              "Authorization": "Bearer {}".format(credentials.token["access_token"])}
    url = "https://graph.microsoft.com/v1.0/servicePrincipals/{}/addPassword".format(object_id)
    payload = {
        "passwordCredential": {
            "displayName": "spellClientSecret"
        },
    }
    # POST request
    try:
        response = requests.post(url, data=json.dumps(payload), headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ExitException("Error setting client secret: {}".format(e.response.text))

    # Return Client Secret and Expiration Date
    secret_info = json.loads(response.text)
    return secret_info["secretText"], secret_info["endDateTime"]


def create_and_assign_role(credentials, subscription_id, group_id, object_id, authorization_client):
    """Creates a custom `Spell-Access` role with the specified permissions """

    role_definition_id = str(uuid.uuid4())
    header = {"Content-Type": "application/json",
              "Authorization": "Bearer {}".format(credentials.token["access_token"])}
    role_name = "SpellAccess_{}".format(str(random.randint(10 ** 6, 10 ** 7)))
    scope = "subscriptions/{}".format(subscription_id)
    url = "https://management.azure.com/{}/providers/Microsoft.Authorization/" \
          "roleDefinitions/{}?api-version=2015-07-01".format(scope, role_definition_id)
    payload = {
        "name": role_definition_id,
        "properties": {
            "roleName": role_name,
            "description": "Spell Access Role to let Spell spin up and down worker machines and access your blobs",
            "type": "CustomRole",
            "permissions": [
                {
                    "actions": required_permissions
                }
            ],
            "assignableScopes": [scope]
        }
    }
    cluster_utils.echo_delimiter()
    click.echo(
        "Creating role {} with the following permissions: \n{} \n...".format(
            role_name, "\n".join("\t" + p for p in required_permissions)
        )
    )
    try:
        response = requests.put(url, data=json.dumps(payload), headers=header)
        response.raise_for_status()
    except requests.exceptions.HTTPError as e:
        raise ExitException("Error creating role: {}".format(e.response.text))

    click.echo("Role Created!")

    roles = list(authorization_client.role_definitions.list(
        group_id,
        filter="roleName eq '{}'".format(role_name)
    ))
    assert len(roles) == 1, "Found unexpected number of roles ({}) with name {}. " \
                            "Expected exactly 1".format(len(roles), role_name)
    spell_role = roles[0]

    # Assign Custom Role to Service Principal
    authorization_client.role_assignments.create(
        group_id,
        uuid.uuid4(),
        {
            "role_definition_id": spell_role.id,
            "principal_id": object_id,
            "principal_type": "ServicePrincipal",
        }
    )


def create_storage_account(storage_client, cluster_name, resource_group_name, params):
    from azure.core.exceptions import HttpResponseError
    """Creates a Storage Account and returns Storage Client, Storage Account"""

    cluster_utils.echo_delimiter()

    default_name = "".join(filter(str.isalnum, "spell{}storage".format(cluster_name[:13]).lower()))
    storage_account_name = click.prompt(
        "Please enter a name for the Azure Storage Account Spell will create for run outputs",
        default=default_name,
    ).strip()

    # Built in Azure Storage Account name validator
    availability = storage_client.storage_accounts.check_name_availability(storage_account_name)
    if not availability.name_available:
        click.echo("Azure does not support this name for the following reason: {}".format(availability.reason))
        return create_storage_account(storage_client, cluster_name, resource_group_name, params)

    # Create Storage Account
    try:
        storage_async_operation = storage_client.storage_accounts.create(
            resource_group_name,
            storage_account_name,
            params,
        )
        storage_account = storage_async_operation.result()
    except HttpResponseError as e:
        click.echo("Unable to create storage account. Azure error: {}".format(e), err=True)
        return create_storage_account(storage_client, cluster_name, resource_group_name, params)

    click.echo("Storage account `{}` under resource group `{}` created!"
               .format(storage_account_name, resource_group_name))
    return storage_account, storage_account_name


def create_blob_container(storage_account, storage_account_name, blob_service_client):
    """Creates a Blob Container and returns the Container Client"""

    cluster_utils.echo_delimiter()

    for i in range(3):
        try:
            blob_service_client.create_container(storage_account_name)
            click.echo("Created your new blob container `spell-blob-container`!")
            return
        except Exception as e:
            click.echo("Unable to create blob container. Azure error: {}".format(e), err=True)

    raise ExitException("Could not create blob container after three retries.")
