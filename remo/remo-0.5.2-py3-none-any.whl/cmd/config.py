import re
import unicodedata
import warnings
from datetime import datetime

from django.contrib.auth import get_user_model

from .log import Log
from remo_app.config.config import Config, ViewerOptions, CloudPlatformOptions


def normalize_email(email):
    """
    Normalize the email address by lowercasing the domain part of it.
    """
    email = email or ''
    try:
        email_name, domain_part = email.strip().rsplit('@', 1)
    except ValueError:
        pass
    else:
        email = email_name + '@' + domain_part.lower()
    return email


def normalize_username(username):
    return unicodedata.normalize('NFKC', username) if isinstance(username, str) else username


def normalize_user_info(username: str, email: str, password: str):
    username = re.sub(r"[\s-]+", "_", username.lower())
    username = re.sub(r"[^.\w\d_]+", "", username)

    if not password:
        password = 'adminpass'

    if not email:
        email = '{}@remo.ai'.format(username)

    email = normalize_email(email)
    username = normalize_username(username)
    return username, email, password


def create_or_update_user(username='remo', email='remo@remo.ai', password='adminpass'):
    username, email, password = normalize_user_info(username, email, password)

    User = get_user_model()
    user = User.objects.filter(is_superuser=True).first()
    warnings.simplefilter("ignore")
    if not user:
        User.objects.create_superuser(username, email, password, last_login=datetime.now())
    else:
        user.email = email
        user.username = username
        user.set_password(password)
        user.save()

    Log.msg(f"""
    Local credentials:

    login: {email}
    password: {password}
    """)

    return username, email, password


def create_config(db_url, colab: bool = False, token: str = None):
    Log.stage('Creating remo config')
    Log.msg(f'* Config file location: {Config.path()}')

    cfg = Config.load()
    if not cfg:
        name, email, password = create_or_update_user()
        cfg = Config(db_url=db_url, user_name=name, user_email=email, user_password=password)
    else:
        name, email, password = create_or_update_user(cfg.user_name, cfg.user_email, cfg.user_password)
        cfg.update(db_url=db_url, user_name=name, user_email=email, user_password=password)

    if colab:
        cfg.viewer = ViewerOptions.jupyter
        cfg.cloud_platform = CloudPlatformOptions.colab

    if token:
        cfg.token = token

    cfg.save()
    return cfg
