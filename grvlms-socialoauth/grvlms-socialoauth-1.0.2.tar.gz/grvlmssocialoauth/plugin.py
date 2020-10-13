import click
from glob import glob
import os

from .__about__ import __version__
from grvlms.commands import cli, compose, context, local
from grvlms.commands import config as config_cli
from grvlms import config as grvlms_config
from grvlms import env
from grvlms import interactive

HERE = os.path.abspath(os.path.dirname(__file__))

templates = os.path.join(HERE, "templates")

config = {
    "add": {
        "ACTIVATE_AZURE": True,
        "AZURE_CLIENT_ID": "",
        "AZURE_SECRET_KEY": "",

        "ACTIVATE_GOOGLE": False,
        "GOOGLE_CLIENT_ID": "",
        "GOOGLE_SECRET_KEY": "",
    }
}

hooks = {
    "init": ["lms"],
}

def patches():
    all_patches = {}
    for path in glob(os.path.join(HERE, "patches", "*")):
        with open(path) as patch_file:
            name = os.path.basename(path)
            content = patch_file.read()
            all_patches[name] = content
    return all_patches

@click.group(help="Extra Command for Social Oauth")
def command():
    pass


def ask_questions_socialoauth(config, defaults):
    # Azure SSO
    interactive.ask_bool(
        "Could you want to enable azure image feature:",
        "SOCIALOAUTH_ACTIVATE_AZURE", 
        config, 
        {"SOCIALOAUTH_ACTIVATE_AZURE": False})
    interactive.ask(
        "Your Azure Client ID:", 
        "SOCIALOAUTH_AZURE_CLIENT_ID",
        config, 
        {"SOCIALOAUTH_AZURE_CLIENT_ID": ""})
    interactive.ask(
        "Your Azure Secret key:", 
        "SOCIALOAUTH_AZURE_SECRET_KEY", 
        config, 
        {"SOCIALOAUTH_AZURE_SECRET_KEY": ""})
    # Google SSO
    interactive.ask_bool(
        "Could you want to enable google image feature:",
        "SOCIALOAUTH_ACTIVATE_GOOGLE", 
        config, 
        {"SOCIALOAUTH_ACTIVATE_GOOGLE": False})
    interactive.ask(
        "Your Google Client ID:", 
        "SOCIALOAUTH_GOOGLE_CLIENT_ID",
        config, 
        {"SOCIALOAUTH_GOOGLE_CLIENT_ID": ""})
    interactive.ask(
        "Your Google Secret key:", 
        "SOCIALOAUTH_GOOGLE_SECRET_KEY", 
        config, 
        {"SOCIALOAUTH_GOOGLE_SECRET_KEY": ""})


def load_config_socialoauth(root, interactive=True):
    defaults = grvlms_config.load_defaults()
    config = grvlms_config.load_current(root, defaults)
    if interactive:
        ask_questions_socialoauth(config, defaults)
    return config, defaults


@click.command(help="Print socialoauth version", name="version")
def print_version():
    click.secho("The version is: {}".format(__version__), fg="blue")


@click.command(help="Init plugin", name="init")
@click.pass_obj
def init(context):
    local.local.callback()
    compose.initialise_plugin("init")

@click.command(help="Config socialoauth variables", name="config")
@click.option("-i", "--interactive", is_flag=True, help="Run interactively")
@click.option("-s", "--set", "set_",
    type=config_cli.YamlParamType(),
    multiple=True,
    metavar="KEY=VAL", 
    help="Set a configuration value")
@click.pass_obj
def config_social(context, interactive, set_):
    config, defaults = load_config_socialoauth(
        context.root, interactive=interactive
    )
    if set_:
        grvlms_config.merge(config, dict(set_), force=True)
    grvlms_config.save_config_file(context.root, config)
    grvlms_config.merge(config, defaults)
    env.save(context.root, config)
    
command.add_command(print_version)
command.add_command(init)
command.add_command(config_social)
