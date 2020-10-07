import boto3
import json
from django.conf import settings
from akeru.app_settings import EC2_TRUST_POLICY, LAMBDA_TRUST_POLICY, \
    DEFAULT_TRUST_POLICY

EC2_POLICY = getattr(settings, 'EC2_TRUST_POLICY', EC2_TRUST_POLICY)
LAMBDA_POLICY = getattr(settings, 'LAMBDA_TRUST_POLICY', LAMBDA_TRUST_POLICY)

if hasattr(settings, 'DEFAULT_TRUST_POLICY'):
    DEFAULT_POLICY = settings.DEFAULT_TRUST_POLICY
elif hasattr(settings, 'DEFAULT_TRUSTED_USERS'):
    DEFAULT_POLICY = DEFAULT_TRUST_POLICY.replace(
        "<custom_trusted_users>", json.dumps(settings.DEFAULT_TRUSTED_USERS)
    )
else:
    raise Exception("Please provide django settings for DEFAULT_TRUST_POLICY "
                    "or DEFAULT_TRUSTED_USERS")


def get_or_create_role(role_name, trust_policy):
    iam = boto3.client('iam', region_name='ap-southeast-2')
    try:
        role = iam.get_role(RoleName=role_name)['Role']
        iam.update_assume_role_policy(
            RoleName=role_name, PolicyDocument=trust_policy
        )
        return role
    except iam.exceptions.NoSuchEntityException:
        return iam.create_role(
            RoleName=role_name, AssumeRolePolicyDocument=trust_policy
        )['Role']


def get_or_create_user(user_name):
    iam = boto3.client('iam', region_name='ap-southeast-2')
    try:
        return iam.get_user(UserName=user_name)['User']
    except iam.exceptions.NoSuchEntityException:
        return iam.create_user(UserName=user_name)['User']


def get_trust_policy(aws_role):
    if aws_role.trust:
        return aws_role.trust
    elif aws_role.ec2:
        return EC2_POLICY
    elif aws_role.aws_lambda:
        return LAMBDA_POLICY
    else:
        return DEFAULT_POLICY


def get_or_create_instance_profile(aws_role):
    iam = boto3.client('iam', region_name='ap-southeast-2')
    try:
        return iam.get_instance_profile(InstanceProfileName=aws_role.name)
    except iam.exceptions.NoSuchEntityException:
        return iam.create_instance_profile(InstanceProfileName=aws_role.name)


def create_policy(source_policy, target_name):
    iam = boto3.client('iam', region_name='ap-southeast-2')
    s3 = boto3.client('s3', region_name='ap-southeast-2')
    sts = boto3.client("sts", region_name='ap-southeast-2')
    acc = sts.get_caller_identity()['Account']
    target_policy_arn = "arn:aws:iam::{}:policy/{}".format(acc, target_name)
    key = "<key>"

    if not hasattr(settings, 'POLICY_PREFIX'):
        raise Exception("Please provide django setting 'POLICY_PREFIX'")
    if not hasattr(settings, 'POLICY_BUCKET'):
        raise Exception("Please provide django settings 'POLICY_BUCKET'")

    try:
        key = "".join([settings.POLICY_PREFIX, "/", source_policy, ".json"])
        source_s3_file = s3.get_object(Bucket=settings.POLICY_BUCKET, Key=key)
        source_policy_content = source_s3_file['Body'].read().decode('ascii')
    except Exception as ex:
        raise Exception("Unable to find {}: {}".format(key, str(ex)))

    try:
        versions = iam.list_policy_versions(PolicyArn=target_policy_arn)
        if len(versions['Versions']) == 5:
            iam.delete_policy_version(
                PolicyArn=target_policy_arn,
                VersionId=versions['Versions'][4]['VersionId']
            )
        iam.create_policy_version(
            PolicyArn=target_policy_arn,
            PolicyDocument=source_policy_content,
            SetAsDefault=True)
    except iam.exceptions.NoSuchEntityException:
        iam.create_policy(
            PolicyName=target_name, PolicyDocument=source_policy_content
        )

    return target_policy_arn


def get_or_create_group(group_name):
    iam = boto3.client('iam', region_name='ap-southeast-2')

    try:
        return iam.get_group(GroupName=group_name)['Group']
    except iam.exceptions.NoSuchEntityException:
        return iam.create_group(GroupName=group_name)['Group']


def create_user(aws_role):
    iam = boto3.client('iam', region_name='ap-southeast-2')

    # Update policy and create group / user
    target_policy_arn = create_policy(aws_role.policy, aws_role.name)
    get_or_create_user(aws_role.name)
    get_or_create_group(aws_role.name)

    iam.attach_group_policy(
        GroupName=aws_role.name, PolicyArn=target_policy_arn
    )
    iam.add_user_to_group(GroupName=aws_role.name, UserName=aws_role.name)

    # Remove other policies
    policies = iam.list_attached_group_policies(
        GroupName=aws_role.name)['AttachedPolicies']
    for policy in policies:
        if policy['PolicyArn'] != target_policy_arn:
            iam.detach_group_policy(
                GroupName=aws_role.name, PolicyArn=policy['PolicyArn']
            )

    return {
        "success": True,
        "detail": "User '{}' deployed to account".format(aws_role.name)
    }


def create_role(aws_role):
    iam = boto3.client('iam', region_name='ap-southeast-2')

    # Update policy and create role
    target_plcy_arn = create_policy(aws_role.policy, aws_role.name)
    trust = get_trust_policy(aws_role)
    get_or_create_role(aws_role.name, trust)
    iam.attach_role_policy(RoleName=aws_role.name, PolicyArn=target_plcy_arn)
    iam.update_role(RoleName=aws_role.name, MaxSessionDuration=2*60*60)

    # Remove other policies
    policies = iam.list_attached_role_policies(
        RoleName=aws_role.name)['AttachedPolicies']
    for policy in policies:
        if policy['PolicyArn'] != target_plcy_arn:
            iam.detach_role_policy(
                RoleName=aws_role.name, PolicyArn=policy['PolicyArn']
            )

    # Optional set instance profile
    if aws_role.ec2:
        in_pr = get_or_create_instance_profile(aws_role)
        profile_has_roles = len(in_pr['InstanceProfile']['Roles'])
        profile_role = in_pr['InstanceProfile']['Roles'][0]['RoleName']
        role_is_not_target = profile_role != aws_role.name
        if profile_has_roles and role_is_not_target:
            raise Exception(
                "Unexpected role attached to this instance profile"
            )

        if 'Roles' not in in_pr['InstanceProfile']:
            iam.add_role_to_instance_profile(
                InstanceProfileName=aws_role.name, RoleName=aws_role.name
            )

    return {
        "success": True,
        "detail": "Role '{}' deployed to account".format(aws_role.name)
    }
