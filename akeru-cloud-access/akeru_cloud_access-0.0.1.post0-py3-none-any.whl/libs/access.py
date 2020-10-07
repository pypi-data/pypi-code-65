import boto3
from akeru.libs.setting import get_setting


def __get_boto_connection(service, client, creds=None):
    keys = creds if creds else {}
    if client:
        return boto3.client(service, region_name='us-east-1', **keys)
    else:
        return boto3.resource(service, region_name='us-east-1', **keys)


def local_akeru_connection(service, client=True):
    return __get_boto_connection(service, client, None)


def remote_akeru_credentials(account_id):
    return target_role_connection(
        role_name=get_setting('REMOTE_ACCESS_ROLE'),
        account_id=account_id,
        session_name=get_setting('REMOTE_ACCESS_ROLE'),
        expiry=60*15,
    )


def target_role_connection(role_name, account_id, session_name, expiry):
    sts = local_akeru_connection('sts')
    target_role = "arn:aws:iam::{}:role/{}".format(account_id, role_name)
    creds = sts.assume_role(
        RoleArn=target_role,
        RoleSessionName=session_name,
        DurationSeconds=expiry
    )
    return creds['Credentials']
