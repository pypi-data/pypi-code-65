import logging
import os
from multiprocessing import Process
import atexit

import requests
import typer

from . import postgres
from .config import Config
from .killer import is_port_in_use, try_to_terminate_another_remo_app, kill_background_process, terminate_electron_app
from .log import Log
from ..config.config import CloudPlatformOptions


def delayed_browse(config, debug=False):
    if config.viewer == 'electron':
        from .viewer.electron import browse
    else:
        from .viewer.browser import browse

    url = build_url(config)
    browse(url, debug)


def build_url(config, initial_page='datasets'):
    page = initial_page.strip('/')
    return '{}/{}/'.format(config.get_host_address(), page)


def backup_job():
    from remo_app.config.standalone.wsgi import application
    from remo_app.remo.use_cases.usage_stats.jobs import run_periodic_backup
    run_periodic_backup(120, postgres.get_instance())


def check_db_connection_job():
    from remo_app.config.standalone.wsgi import application
    from remo_app.remo.use_cases.usage_stats.jobs import run_periodic_check_db_connection
    run_periodic_check_db_connection(5, postgres.get_instance())


def stop_db_server():
    pg = postgres.get_instance()
    if pg.is_need_to_stop:
        pg.stop()


def get_public_url():
    try:
        resp = requests.get('http://localhost:4040/api/tunnels').json()
        tunnels = resp.get('tunnels')
        if not tunnels:
            return

        url = tunnels[0].get('public_url')
        if url:
            return url.replace('http://', 'https://')
    except Exception:
        return


def run_server(config, debug=False, background_job=None, with_browser=True):
    debug = debug or config.debug
    if debug:
        os.environ['DJANGO_DEBUG'] = 'True'
    from remo_app.config.standalone.wsgi import application
    from django.conf import settings

    colab = config.cloud_platform == CloudPlatformOptions.colab
    if config.is_local_server() and is_port_in_use(config.port):
        if colab:
            Log.msg(f'Remo app running locally on http://localhost:{config.port}')
            public_url = get_public_url()
            if public_url:
                config.public_url = public_url
                config.save()
                Log.msg(f"""
You can access Remo from browser on {public_url}

To be able use Remo in Colab Notebook, do the following:
```
import remo

remo.open_ui()
```
""")
            return

        Log.error(f'Failed to start remo-app, port {config.port} already in use.', report=True)

        ok = try_to_terminate_another_remo_app(config)
        if not ok:
            Log.msg(f'You can change default port in config file: {Config.path()}')
            return
    else:
        terminate_electron_app()

    if config.is_local_server():
        from remo_app.remo.services.license import is_trial_valid, store_token, is_valid_token
        if not config.cloud_platform and not is_valid_token(config.token) and not is_trial_valid():
            msg = """
Remo is free to use, but you would need to register your email address to keep using it.
Do you want to register now?"""
            if typer.confirm(msg, default=True):
                register_free_token()
            else:
                Log.msg("Launching Remo, you will have the chance to register from the UI")

        processes = []
        if colab:
            backup_process = Process(target=backup_job)
            backup_process.start()
            processes.append(backup_process)
        else:
            check_db_connection_process = Process(target=check_db_connection_job)
            check_db_connection_process.start()
            processes.append(check_db_connection_process)

        if with_browser and not colab:
            ui_process = Process(target=delayed_browse, args=(config, debug), daemon=True)
            ui_process.start()
            processes.append(ui_process)

        background_process = Process(target=background_job)
        background_process.start()
        processes.append(background_process)

        atexit.register(stop_db_server)
        atexit.register(kill_background_process, *processes)

        start_server(application, config.port)

    else:
        Log.msg(f'Remo is running on remote server: {config.get_host_address()}')
        if with_browser:
            delayed_browse(config, debug)


def start_server(application, port: str = Config.default_port):
    from waitress import serve

    logging.basicConfig()
    logger = logging.getLogger('waitress')
    logger.setLevel(logging.ERROR)

    Log.msg(f'Remo app running on http://localhost:{port}. Press Control-C to stop it.')
    serve(application, _quiet=True, port=port, threads=3)


def register_free_token():
    from django.conf import settings
    from remo_app.remo.services.license import register_user, store_token
    from remo_app.remo.services.email import send_email, compose_msg
    from remo_app.remo.services.users import create_or_update_superuser

    if typer.confirm("Do you already have a token?", default=True):
        token = get_required_value('Token')
        ok = is_token_valid(token)
        if not ok:
            Log.msg("Provided token is not valid.")
            if not typer.confirm("Do you want to pass registration to get new token?", default=True):
                return
        else:
            if not store_token(token):
                Log.msg("Something is wrong with provided token")
            return

    fullname = get_optional_value('Full name')
    email = get_required_value('Email')
    username = get_optional_value('Username')
    company = get_optional_value('Company')
    allow_marketing_emails = get_bool_value('Do you want subscribe for updates?')
    create_or_update_superuser(email=email, fullname=fullname, username=username, company=company,
                               allow_marketing_emails=allow_marketing_emails)

    ok = False
    try:
        ok, req, resp = register_user(email, username, fullname, company, allow_marketing_emails)
    except Exception as err:
        Log.exit(f'Failed to register user: {err}', report=True, exception=True)

    if not ok:
        send_email(
            subject=f'Failed to register user from CLI: {fullname}',
            content=compose_msg(req, resp)
        )
        Log.msg(f'Failed to register user, please contact us at {settings.REMO_EMAIL}')
        return

    typer.secho("\nGreat! Now verify your email address", fg=typer.colors.GREEN, bold=True)
    typer.secho("""We have sent you an email with activation link to verify your email.
And you will get follow up email with token. Please insert the token below.
""", fg=typer.colors.GREEN)

    ok = False
    token = ''
    for _ in range(3):
        token = get_required_value('Token')
        ok = is_token_valid(token)
        if not ok:
            Log.msg("Please try another token")
            continue

        break

    if ok:
        ok = store_token(token)
    if not ok:
        Log.msg(f"""
Something went wrong, you token is not valid.
Please contact us at {settings.REMO_EMAIL} and we will help to fix the issue.""")


def is_token_valid(token: str) -> bool:
    from remo_app.remo.services.license import validate_token
    try:
        return validate_token(token)
    except Exception as err:
        Log.error(f'Failed to validate token: {err}', report=True, exception=True)
    return False


def get_required_value(text: str) -> str:
    while True:
        value = input(f'{text} (required): ').strip()
        if value:
            break
        Log.msg(f'{text} is a required field, cannot be empty')
    return value


def get_optional_value(text: str) -> str:
    return input(f'{text}: ').strip()


def get_bool_value(text: str) -> bool:
    return typer.confirm(text, default=True)
