import boto3
from botocore.exceptions import ClientError
from django.db import models
from django.contrib.auth.models import User, Group
from django.core.exceptions import ValidationError
from django.conf import settings
from django.utils.translation import gettext_lazy as _


def choices():
    choice = []
    try:
        s3 = boto3.client('s3', region_name='ap-southeast-2')
        policies = s3.list_objects(
            Bucket=settings.POLICY_BUCKET, Prefix=settings.POLICY_PREFIX
        )
        for policy in policies['Contents']:
            key = policy['Key']
            name = key[key.rfind('/') + 1:key.rfind(".")]
            if name.startswith('template-'):
                choice.append((name, name),)
    except ClientError:
        pass

    return choice


class AWSRole(models.Model):
    name = models.CharField(max_length=100, unique=True)
    policy = models.CharField(max_length=100, choices=choices())
    trust = models.TextField(blank=True)
    user = models.BooleanField(default=False)
    mfa = models.BooleanField(default=False)
    kms = models.BooleanField(default=False)
    ec2 = models.BooleanField(default=False)
    aws_lambda = models.BooleanField(default=False)
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['name']
        unique_together = ['name', 'user']

    def __init__(self, *args, **kwargs):
        super(AWSRole, self).__init__(*args, **kwargs)
        self._meta.get_field('policy').choices = choices()

    def __str__(self):
        prefix = "Std User" if self.user else "Role"
        if self.ec2 or self.aws_lambda:
            prefix = "{} {}".format("EC2" if self.ec2 else "Lambda", prefix)

        return "{} | {}".format(prefix, self.name)

    def clean(self):
        if self.mfa and not self.user:
            raise ValidationError(_("MFA can only be applied to users"))
        if self.ec2 and self.aws_lambda:
            raise ValidationError(
                _("Cannot choose EC2 and Lambda at the same time")
            )
        if self.user and self.trust:
            raise ValidationError(
                _("Trust policies cannot be applied to users")
            )
        if self.trust and (self.ec2 or self.aws_lambda):
            msg = "You can either specify a custom trust policy OR " \
                  "EC2/Lamba. Not both."
            raise ValidationError(_(msg))


class AccessRole(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, blank=True, null=True
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE, blank=True, null=True
    )
    role = models.ForeignKey(AWSRole, on_delete=models.CASCADE)
    access_key = models.CharField(max_length=100, blank=True, null=True)
    secret_key = models.CharField(max_length=100, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.role.user and not self.access_key:
            iam = boto3.client('iam', region_name='ap-southeast-2')
            keys = iam.create_access_key(UserName=self.role.name)['AccessKey']
            self.access_key = keys['AccessKeyId']
            self.secret_key = keys['SecretAccessKey']
        elif not self.role.user:
            self.access_key = None
            self.secret_key = None
        super(AccessRole, self).save(*args, **kwargs)

    def clean(self):
        if self.role.user and self.group:
            raise ValidationError(_("A group cannot be tied to an AWS user. "
                                    "Only user is available"))
        if not self.user and not self.group:
            raise ValidationError(_("Select either a user or a group"))
        if self.user and self.group:
            raise ValidationError(
                _("You must select either a user or a group, not both.")
            )
