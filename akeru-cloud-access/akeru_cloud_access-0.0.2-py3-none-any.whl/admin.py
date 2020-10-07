from django.contrib import admin
from akeru.models import AWSRole, AccessRole
from akeru.deploy import create_role, create_user
from django.contrib import messages


def deploy_role(modeladmin, request, queryset):
    for role in queryset:
        try:
            result = create_user(role) if role.user else create_role(role)
        except Exception as ex:
            result = {"success": False, "detail": ex}

        if result['success']:
            messages.add_message(request, messages.INFO, result['detail'])
        else:
            messages.add_message(request, messages.ERROR, result['detail'])


deploy_role.short_description = "Deploy user/role to account"


def roll_credentials(modeladmin, request, queryset):
    for access in queryset:
        if access.role.user:
            result = {
                "success": False,
                "detail": "Please implement me: {}".format(access.role.name)
            }
            if result['success']:
                messages.add_message(request, messages.INFO, result['detail'])
            else:
                messages.add_message(request, messages.ERROR, result['detail'])
        else:
            messages.add_message(
                request, messages.WARNING,
                "{} is a role, rolling keys is not applicable".format(
                    access.role.name)
            )


roll_credentials.short_description = "Change the IAM keys for a role"


def role_type(obj):
    if obj.role.trust:
        return "Custom Role"
    elif obj.role.ec2:
        return "Instance Profile"
    elif obj.role.aws_lambda:
        return "Lambda Role"
    elif obj.role.user:
        return "Standard User"
    elif not obj.role.user:
        return "Standard Role"
    else:
        return "Error - unknown type"


role_type.short_description = "IAM Type"


def role_name(obj):
    return obj.role.name


role_name.short_description = "Role Name"


def access_entity(obj):
    if obj.user:
        return "{} (User)".format(obj.user)
    else:
        return "{} (Group)".format(obj.group)


access_entity.short_description = "User / Group assigned"


class AWSRoleAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'policy', 'user', 'mfa', 'kms', 'ec2', 'aws_lambda'
    )
    actions = [deploy_role]


class AccessRoleAdmin(admin.ModelAdmin):
    list_display = (role_name, role_type, access_entity)
    readonly_fields = ('access_key', 'secret_key')
    actions = [roll_credentials]


admin.site.register(AWSRole, AWSRoleAdmin)
admin.site.register(AccessRole, AccessRoleAdmin)
