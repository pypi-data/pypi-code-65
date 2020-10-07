from akeru import app_settings
from django.conf import settings


def get_setting(name):
    in_application = getattr(settings, name, None)
    in_default = getattr(app_settings, name, None)

    if in_application:
        return in_application
    elif in_default:
        return in_default
    else:
        raise Exception("The setting '{}' has not been defined".format(name))
