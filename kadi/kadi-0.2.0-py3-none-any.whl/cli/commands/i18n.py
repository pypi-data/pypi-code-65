# Copyright 2020 Karlsruhe Institute of Technology
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json
import os
import sys
import tempfile

import click
from flask import current_app

from kadi.cli.main import kadi
from kadi.cli.utils import check_env
from kadi.cli.utils import run_command
from kadi.cli.utils import success
from kadi.cli.utils import warning


@kadi.group()
def i18n():
    """Utility commands for managing translations."""


def _pybabel_extract(translations_path):
    cwd = os.getcwd()
    # Change to the application root path so all extracted strings will be shown as
    # being relative to that path.
    os.chdir(current_app.root_path)

    babel_cfg = os.path.join(translations_path, "babel.cfg")
    messages_pot = os.path.join(translations_path, "messages.pot")

    cmd = [
        "pybabel",
        "extract",
        "-F",
        babel_cfg,
        "-k",
        "lazy_gettext",
        "-k",
        "_l",
        "-o",
        messages_pot,
        "--copyright-holder",
        "Karlsruhe Institute of Technology",
        "--project",
        "Kadi4Mat",
        ".",
    ]
    run_command(cmd)

    os.chdir(cwd)


@i18n.command()
@click.argument("lang")
@click.option("--i-am-sure", is_flag=True)
@check_env
def init(lang, i_am_sure):
    """Add a new language to the backend translations."""
    if not i_am_sure:
        warning(
            f"This might replace existing translations for language '{lang}'. If you"
            " are sure you want to do this, use the flag --i-am-sure."
        )
        return

    translations_path = current_app.config["BACKEND_TRANSLATIONS_PATH"]
    messages_pot = os.path.join(translations_path, "messages.pot")

    _pybabel_extract(translations_path)

    cmd = ["pybabel", "init", "-i", messages_pot, "-d", translations_path, "-l", lang]
    run_command(cmd)

    success("Initialization completed successfully.")


@i18n.command()
@check_env
def update():
    """Update all existing backend translations."""
    translations_path = current_app.config["BACKEND_TRANSLATIONS_PATH"]
    messages_pot = os.path.join(translations_path, "messages.pot")

    _pybabel_extract(translations_path)

    cmd = ["pybabel", "update", "-i", messages_pot, "-d", translations_path]
    run_command(cmd)

    success("Update completed successfully.")


@i18n.command()
@check_env
def compile():
    """Compile all existing backend translations."""
    translations_path = current_app.config["BACKEND_TRANSLATIONS_PATH"]

    cmd = ["pybabel", "compile", "-d", translations_path]
    run_command(cmd)

    success("Compilation completed successfully.")


def _sync(key, value, old_translation, new_translation):
    if isinstance(value, dict):
        _new_translation = new_translation[key] = {}

        # If an old translation exists with the key (and is also a dictionary), then use
        # it for the subsequent checks of the nested keys.
        if key in old_translation and isinstance(old_translation[key], dict):
            _old_translation = old_translation[key]
        else:
            _old_translation = {}

        for _key, _value in value.items():
            _sync(_key, _value, _old_translation, _new_translation)
    else:
        # Either copy the old translation or use an empty string.
        if key in old_translation:
            new_translation[key] = old_translation[key]
        else:
            new_translation[key] = ""


def _get_missing_entries(old_translation, new_translation):
    entries = {}

    for key, value in old_translation.items():
        if key not in new_translation:
            entries[key] = value
        elif isinstance(value, dict):
            results = _get_missing_entries(old_translation[key], new_translation[key])
            if results:
                entries[key] = results

    return entries


@i18n.command()
@check_env
def sync():
    """Synchronize all frontend translation keys based on the default locale."""
    translations_path = current_app.config["FRONTEND_TRANSLATIONS_PATH"]
    default_locale = current_app.config["LOCALE_DEFAULT"]

    primary_translation = json.load(
        open(os.path.join(translations_path, f"{default_locale}.json"))
    )

    for locale in current_app.config["LOCALES"]:
        file_path = os.path.join(translations_path, f"{locale}.json")

        if locale == default_locale:
            # Only sort the keys for the default locale.
            new_translation = primary_translation
        else:
            new_translation = {}
            old_translation = json.load(open(file_path))

            for key, value in primary_translation.items():
                _sync(key, value, old_translation, new_translation)

            # List any missing entries separately instead of removing them, in case they
            # were just moved to another key.
            entries = _get_missing_entries(old_translation, new_translation)
            if entries:
                new_translation["_old"] = entries

        # Create a new file in the same directory with the new translations, then
        # replace the old one.
        tmp_file = tempfile.NamedTemporaryFile(
            mode="w", dir=translations_path, delete=False
        )

        try:
            tmp_file.write(
                json.dumps(
                    new_translation, indent=2, sort_keys=True, ensure_ascii=False
                )
                + "\n"
            )
            tmp_file.close()

            os.rename(tmp_file.name, file_path)

            if locale != default_locale:
                click.echo(f"Synchronized '{file_path}'.")

        except Exception as e:
            click.secho(str(e), fg="red")

            try:
                os.remove(tmp_file.name)
            except FileNotFoundError:
                pass

            sys.exit(1)

    success("Synchronization completed successfully.")
