import json
import time
import logging

import requests
from django.conf import settings

from remo_app.config.config import Config
from remo_app.remo.models.token import Token
from remo_app.remo.services.users import create_or_update_superuser
from remo_app.remo.use_cases import is_remo_local

logger = logging.getLogger('remo_app')


def is_trial_valid() -> bool:
    valid = True
    if is_remo_local():
        try:
            json = {'uuid': settings.REMO_UUID}
            resp = request('POST', f'{settings.REMO_STATS_SERVER}/api/v1/ui/validate-uuid/1/trial/', json=json)
            if not resp:
                raise Exception('Failed validated trial after retries')
            resp = resp.json()
            valid = resp.get('valid', False)
        except Exception as err:
            logger.error(f'Failed to check trial: {err}')

    return valid


def register_user(email: str, username: str, fullname: str, company: str, allow_marketing_emails: bool) -> (bool, dict, dict):
    json = {
      "user": {
        "email": email,
        "uuid": settings.REMO_UUID,
        "fullname": fullname,
        "username": username,
        "company": company,
        "allow_marketing_emails": allow_marketing_emails
      }
    }

    resp = request('POST', f'{settings.REMO_TOKEN_SERVER}/api/v1/users/register', json=json)
    if not resp:
        return False, json, {}
    ok = resp.status_code == 200
    response = resp.json()
    return ok, json, response


def validate_token(token: str) -> bool:
    try:
        license = get_license(token)
    except Exception:
        return False

    if not license:
        return False

    return license.get('valid', False)


def get_license(token: str) -> dict:
    json = {
        "license": {
            "token": token,
            "uuid": settings.REMO_UUID
        }
    }

    resp = request('POST', f'{settings.REMO_TOKEN_SERVER}/api/v1/license/', json=json)
    if not resp or resp.status_code != 200:
        raise Exception('Invalid response from server')

    license = resp.json().get('license', {})
    if not license:
        raise Exception('No license in server response')
    return license


def get_user_details(token: str) -> dict:
    json = {
        "license": {
            "token": token,
            "uuid": settings.REMO_UUID
        }
    }

    resp = request('POST', f'{settings.REMO_TOKEN_SERVER}/api/v1/users/token', json=json)
    if not resp or resp.status_code != 200:
        return {}

    return resp.json().get('user', {})


def store_token(token: str) -> bool:
    try:
        license = get_license(token)
    except Exception as err:
        logger.error(f'Failed to get license from server: {err}')
        return False

    if license:
        license = json.dumps(license)

    db_token = Token.objects.first()
    if not db_token:
        db_token = Token.objects.create(
            token=token,
            license=license
        )
    else:
        db_token.token = token
        db_token.license = license
    db_token.save()

    user = get_user_details(token)
    if user:
        email = user.get('email')
        fullname = user.get('fullname')
        username = user.get('username')
        company = user.get('company')
        allow_marketing_emails = user.get('allow_marketing_emails')
        create_or_update_superuser(email=email, fullname=fullname, username=username, company=company, allow_marketing_emails=allow_marketing_emails, force_update=True)

        config = Config.safe_load(exit_on_error=False)
        config.update(token=token)
        config.save()

    return True


def invalidate_existing_token():
    db_token = Token.objects.first()
    if db_token:
        db_token.delete()


def is_valid_token(token: str) -> bool:
    if not token:
        invalidate_existing_token()
        return False

    if Token.objects.filter(token=token).exists():
        return True

    invalidate_existing_token()

    if not validate_token(token):
        return False

    return store_token(token)


def is_license_valid() -> bool:
    license = read_license()
    return license.get('valid', False)


def read_license() -> dict:
    db_token = Token.objects.first()
    try:
        return db_token.get_license()
    except Exception:
        return {'valid': False}


def request(method: str, url: str, retry=5, timeout=2, **kwargs):
    for _ in range(retry):
        try:
            return requests.request(method, url, **kwargs, timeout=timeout)
        except Exception as err:
            # logger.error(f'Request failed: {err}')
            timeout += 0.2
            time.sleep(1)
