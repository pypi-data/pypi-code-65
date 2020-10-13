__all__ = ["send_email_template"]

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from async_email.email import send_email_template
from async_email.exceptions import InvalidDefaultFromEmail

default_app_config = "async_email.apps.AsyncEmailConfig"


def validate_default_from_email():
    """
    We not allow the application run without a valid DEFAULT_FROM_EMAIL
    """

    default_from_email = settings.DEFAULT_FROM_EMAIL
    print(f"{default_from_email}".center(80, "="))

    try:
        validate_email(default_from_email)
    except ValidationError:
        raise InvalidDefaultFromEmail(
            "Please configure the DEFAULT_FROM_EMAIL on your project settings.py"
        )


validate_default_from_email()
