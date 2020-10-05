from typing import Callable, Union

import click
from click_option_group import MutuallyExclusiveOptionGroup

from sym.cli.constants.env import SYM_USE_CONTROL_MASTER
from sym.cli.helpers.ssh import check_ssh_version
from sym.cli.helpers.util import flow

from ..saml_clients.chooser import choose_saml_client
from .config import Config
from .envvar_option import EnvvarGroupedOption, EnvvarOption
from .params import get_resource_env_vars


def config_option(
    name: str, help: str, default: Union[None, Callable[[], None]] = None, **kwargs
):
    def decorator(f):
        option_decorator = click.option(
            f"--{name}",
            help=help,
            prompt=True,
            default=default or (lambda: Config.instance().get(name)),
            **kwargs,
        )
        return option_decorator(f)

    return decorator


def _resource_callback(ctx, resource: str, saml_client_name: str, throw=True):
    if resource is None:
        return None
    if not Config.is_logged_in():
        return resource
    saml_client = choose_saml_client(saml_client_name)
    if not saml_client.validate_resource(resource):
        if throw:
            raise click.BadParameter(f"Invalid resource: {resource}")
        else:
            return None
    return resource


def _resource_option_callback(ctx, _param, resource: str):
    return _resource_callback(ctx, resource, ctx.params["saml_client_name"], throw=False)


def _resource_arg_callback(ctx, _param, resource: str):
    return _resource_callback(ctx, resource, ctx.parent.params["saml_client_name"])


def resource_option(f):
    option_decorator = click.option(
        "--resource",
        help="the Sym resource to use",
        envvar=get_resource_env_vars(),
        callback=_resource_option_callback,
        default=lambda: Config.get_default("resource"),
        cls=EnvvarOption,
    )
    return option_decorator(f)


def resource_argument(f):
    option_decorator = click.argument("resource", callback=_resource_arg_callback)
    return option_decorator(f)


def ansible_options(f):
    group = MutuallyExclusiveOptionGroup("Ansible Roles")
    options = [
        group.option(
            "--ansible-aws-profile",
            help="the local AWS Profile to use for Ansible commands",
            envvar="AWS_PROFILE",
            cls=EnvvarGroupedOption,
        ),
        group.option(
            "--ansible-sym-resource",
            help="the Sym resource to use for Ansible commands",
            envvar="SYM_ANSIBLE_RESOURCE",
            callback=_resource_arg_callback,
            cls=EnvvarGroupedOption,
        ),
        click.option(
            "--control-master/--no-control-master",
            help="allow SSH ControlPath caching",
            envvar=SYM_USE_CONTROL_MASTER,
            is_flag=True,
            default=check_ssh_version,
            cls=EnvvarOption,
        ),
        click.option(
            "--send-command/--no-send-command",
            help="Use SSM SendCommand instead of SSH",
            envvar="SYM_SEND_COMMAND",
            is_flag=True,
            default=True,
            cls=EnvvarOption,
        ),
        click.option(
            "--forks",
            help="number of parallel subprocesses for ansible",
            default=15,
        ),
    ]
    return flow(options, f)


def required_option(*args, if_, **kwargs):
    def _callback(ctx, param: str, value: str):
        if not value and if_(ctx):
            raise click.exceptions.UsageError(f"{param} is required")
        return value

    def wrapper(f):
        return click.option(*args, callback=_callback, **kwargs)(f)

    return wrapper
