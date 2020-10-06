import re
import unicodedata
import warnings
from datetime import datetime

from django.contrib.auth import get_user_model

from remo_app.config.config import Config
from remo_app.remo.models import UserDetails


def create_or_update_superuser(email='remo@remo.ai', password='adminpass', username='remo', fullname='Remo', company='', allow_marketing_emails=False, force_update=False):
    from remo_app.remo.services.license import is_license_valid

    password = validate_password(password)
    email, username, first_name, last_name = normalize_user_info(email, username, fullname)

    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    warnings.simplefilter("ignore")
    if not user:
        user = User.objects.create_superuser(username, email, password, last_login=datetime.now())
    else:
        if force_update or not is_license_valid():
            user.email = email
        user.username = username
        user.set_password(password)
    user.first_name = first_name
    user.last_name = last_name
    user.save()

    details, _ = UserDetails.objects.get_or_create(user=user)
    details.company = company
    details.allow_marketing_emails = allow_marketing_emails
    details.save()

    user = User.objects.filter(is_superuser=True).first()

    config = Config.safe_load(exit_on_error=False)
    config.update(user_name=user.username, user_email=user.email, user_password=password)
    config.save()


def create_remo_user(email: str, password: str, username: str, fullname: str) -> bool:
    password = validate_password(password)
    email, username, first_name, last_name = normalize_user_info(email, username, fullname)

    User = get_user_model()
    user = User.objects.filter(email=email)
    warnings.simplefilter("ignore")
    if user.exists():
        return False

    user = User.objects.create_user(username, email, password, last_login=datetime.now())
    user.first_name = first_name
    user.last_name = last_name
    user.save()
    return True


def validate_password(password: str) -> str:
    if not password:
        return 'adminpass'
    return password


def normalize_user_info(email: str, username: str, fullname: str):
    first_name, last_name = split_fullname(fullname)

    username = normalize_username(username)
    if not username:
        username = normalize_username(first_name)
    if not username:
        username = normalize_username(email.split('@', 1)[0])
    if not username:
        username = 'remo'

    if not email:
        email = f'{username}@remo.ai'

    email = email.lower()
    return email, username, first_name, last_name


def normalize_username(username: str) -> str:
    if isinstance(username, str):
        username = re.sub(r"[\s-]+", "_", username.lower())
        username = re.sub(r"[^.\w\d_]+", "", username)
        return unicodedata.normalize('NFKC', username)
    return ''


def split_fullname(fullname: str) -> (str, str):
    first_name, last_name = '', ''
    fullname = fullname.strip().split(' ', 1)
    if len(fullname) == 2:
        first_name, last_name = fullname
    else:
        first_name = fullname[0]
    return first_name, last_name
