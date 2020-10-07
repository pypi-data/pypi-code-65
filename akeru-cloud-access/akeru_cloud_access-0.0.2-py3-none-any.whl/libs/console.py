import urllib
import json
import sys
import requests
import boto3
from akeru.models import AccessRole
from akeru.libs.access import target_role_connection, local_akeru_connection
from akeru.libs.setting import get_setting
from django.conf import settings
from django.core.exceptions import PermissionDenied

ROLE_EXPIRY = get_setting('ASSUMED_ROLE_TIMEOUT')
USER_EXPIRY = get_setting('FEDERATED_USER_TIMEOUT')


def get_user_managed_policy_arns(user):
    user_policies = []
    iam = local_akeru_connection('iam')
    groups = iam.list_groups_for_user(UserName=user)['Groups']

    for group in groups:
        policies = iam.list_attached_group_policies(
            GroupName=group['GroupName']
        )['AttachedPolicies']
        for policy in policies:
            user_policies.append({'arn': policy['PolicyArn']})
    return user_policies


def __acquire_session(access_key, secret_key, session_key):
    # Step 3: Format resulting temporary credentials into JSON
    url_credentials = {'sessionId': access_key, 'sessionKey': secret_key,
                       'sessionToken': session_key}
    json_credential_string = json.dumps(url_credentials)

    # Step 4. Make request to AWS federation endpoint to get sign-in token.
    # Construct the parameter string with the sign-in action request, a
    # 12-hour session duration, and the JSON document with temporary
    # credentials as parameters.
    parameters = "?Action=getSigninToken"
    parameters += "&SessionDuration={}".format(USER_EXPIRY)
    if sys.version_info[0] < 3:
        def quote_plus_function(s):
            return urllib.quote_plus(s)
    else:
        def quote_plus_function(s):
            return urllib.parse.quote_plus(s)
    parameters += "&Session=" + quote_plus_function(json_credential_string)
    request_url = "https://signin.aws.amazon.com/federation" + parameters
    r = requests.get(request_url)
    # Returns a JSON document with a single element named SigninToken.
    signin_token = json.loads(r.text)

    # Step 5: Create URL where users can use the sign-in token to sign in to
    # the console. This URL must be used within 15 minutes after the
    # sign-in token was issued.
    dest_url = "https://console.aws.amazon.com/"
    parameters = "?Action=login"
    parameters += "&Issuer=localhost:8000"
    parameters += "&Destination=" + quote_plus_function(dest_url)
    parameters += "&SigninToken=" + signin_token["SigninToken"]
    request_url = "https://signin.aws.amazon.com/federation" + parameters

    # Send final URL to stdout
    return request_url


def get_user_session(user, access_role_user):
    access = access_role_user.access_key
    secret = access_role_user.secret_key
    sts = boto3.client('sts', region_name='us-east-1',
                       aws_access_key_id=access, aws_secret_access_key=secret)
    session_name = "{}-{}".format(access.role.name, user.username)
    permissions = get_user_managed_policy_arns(access.role.name)
    kwargs = {'Name': session_name, 'PolicyArns': permissions}
    creds = sts.get_federation_token(**kwargs)['Credentials']
    session_url = __acquire_session(**creds)
    return session_url


def get_role_session(user, access_role_role):
    creds = target_role_connection(
        role_name=access_role_role.role.name,
        account_id=settings.ACCOUNT_ID,
        session_name=user.username,
        expiry=60 * 15
    )
    session_url = __acquire_session(**creds)
    return session_url


def generate_session(user, role_is_user, entity_name):
    filter_params = {'role__name': entity_name, 'role__user': role_is_user}
    access_roles = AccessRole.objects.filter(**filter_params)
    user_belongs_to_access_role = False
    if len(access_roles) == 1:
        if access_roles[0].user == user:
            user_belongs_to_access_role = True
        elif user.groups.filter(name=access_roles[0].group.name).exists():
            user_belongs_to_access_role = True

    if user_belongs_to_access_role:
        if role_is_user:
            aws_console_session_url = get_user_session(user, access_roles[0])
            return aws_console_session_url
        else:
            aws_console_session_url = get_role_session(user, access_roles[0])
            return aws_console_session_url

    raise PermissionDenied
