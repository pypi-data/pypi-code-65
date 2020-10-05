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
import fnmatch
import json
import os
import pathlib
import sys
from functools import wraps

import click

from kadi_apy.lib.core import KadiAPI
from kadi_apy.lib.core import SearchResource
from kadi_apy.lib.exceptions import KadiAPYConfigurationError
from kadi_apy.lib.exceptions import KadiAPYException
from kadi_apy.lib.records import Record


def _item_init(class_type, identifier=None, id=None):
    """Try to init an item."""

    try:
        return class_type(identifier=identifier, id=id)
    except KadiAPYException as e:
        click.echo(e, err=True)
        sys.exit(1)


def print_request_error(response):
    """Prints the error message and exits with a status code of 1."""
    try:
        payload = response.json()

        click.echo(
            f"{payload.get('description', 'Unknown error.')} ({response.status_code})"
        )
    except:
        click.echo(f"Status code: {response.status_code}")

    sys.exit(1)


def apy_command(func):
    """Decorator to handle the default arguments and exceptions of an APY command."""

    click.option(
        "-h", "--host", help="Host name of the Kadi4Mat instance to use for the API."
    )(func)

    click.option(
        "-k", "--token", help="Personal access token (PAT) to use for the API."
    )(func)

    click.option(
        "-s",
        "--skip-verify",
        is_flag=True,
        help="Skip verifying the SSL/TLS certificate of the host.",
    )(func)

    @wraps(func)
    def decorated_command(token, host, skip_verify, *args, **kwargs):
        KadiAPI.token = token if token is not None else os.environ.get("KADI_PAT")
        KadiAPI.host = host if host is not None else os.environ.get("KADI_HOST")
        KadiAPI.verify = not skip_verify

        try:
            func(*args, **kwargs)
        except KadiAPYException as e:
            click.echo(e, err=True)
            sys.exit(1)

    return decorated_command


def id_identifier_options(class_type, helptext=None, get_id=False, init=False):
    """Decorator to handle the id and identifier."""

    def decorator(func):
        help_id = f"ID of the {class_type.__name__.lower()}"
        if helptext:
            help_id = f"{help_id} {helptext}"

        help_identifier = f"Identifier of the {class_type.__name__.lower()}"
        if helptext:
            help_identifier = f"{help_identifier} {helptext}"

        option = f"--{class_type.__name__.lower()}-id"
        click.option(
            f"-{class_type.__name__[0].lower()}",
            option,
            help=help_id,
            default=None,
            type=int,
        )(func)

        click.option(
            f"-{class_type.__name__[0].upper()}",
            f"--{class_type.__name__.lower()}-identifier",
            help=help_identifier,
            default=None,
            type=str,
        )(func)

        @wraps(func)
        def decorated_command(*args, **kwargs):
            item_id = kwargs[f"{class_type.__name__.lower()}_id"]
            item_identifier = kwargs[f"{class_type.__name__.lower()}_identifier"]
            if (item_id is None and item_identifier is None) or (
                item_id is not None and item_identifier is not None
            ):
                print(
                    f"Please specify either the id or the identifier of the"
                    f" {class_type.__name__.lower()}."
                )
                sys.exit(1)

            # Init the item either by the id or the identifier.
            # The item is directly passed to the function.
            if init:
                item = _item_init(class_type, identifier=item_identifier, id=item_id)
                kwargs[f"{class_type.__name__[0].lower()}"] = item
                del kwargs[f"{class_type.__name__.lower()}_id"]
                del kwargs[f"{class_type.__name__.lower()}_identifier"]

            # The item_id is fetched via the identifier if the item_id is empty.
            elif get_id:
                if item_id is None:
                    item = _item_init(class_type, identifier=item_identifier)
                    kwargs[f"{class_type.__name__.lower()}_id"] = item.id
                del kwargs[f"{class_type.__name__.lower()}_identifier"]

            func(*args, **kwargs)

        return decorated_command

    return decorator


def item_create(class_type, pipe=False, **kwargs):
    """Creates a new item if possible and necessary"""

    item = class_type(create=True, **kwargs)
    if pipe:
        return click.echo(item.id)

    if item.created is True:
        click.echo(f"Sucessully created {repr(item)}.")
    else:
        click.echo(f"{class_type.__name__} {item.id} exists.")

    return item


def _update_attribute(item, attribute, value):
    """Edit a basic attribute of an item."""

    meta = item.meta
    if attribute not in meta:
        click.echo(f"Attribute {attribute} does not exist.")
        return

    value_old = meta[attribute]

    if value_old == value:
        click.echo(f"The {attribute} is already '{value_old}'. Nothing to do.")
    else:
        response = item.set_attribute(attribute=attribute, value=value)
        if response.status_code == 200:
            click.echo(
                f"Successfully updated the {attribute} of {repr(item)} from "
                f"'{value_old}' to '{value}'."
            )
        else:
            print_request_error(response=response)


def item_edit(item, **kwargs):
    """Edit visibility, title or description of a item."""

    for attr, value in kwargs.items():
        if value is not None:
            _update_attribute(item, attribute=attr, value=value)


def item_add_user(item, user_id, permission_new):
    """Add a user to an item."""

    response = item.add_user(user_id=user_id, role_name=permission_new)
    if response.status_code == 201:
        click.echo(
            f"Successfully added user {user_id} as '{permission_new}' to {repr(item)}."
        )
    elif response.status_code == 409:
        response_change = item.change_user_role(
            user_id=user_id, role_name=permission_new
        )
        if response_change.status_code == 200:
            click.echo(f"User {user_id} is '{permission_new}' of {repr(item)}.")
        else:
            print_request_error(response=response_change)
    else:
        print_request_error(response=response)


def item_add_group_role(item, group_id, permission_new):
    """Add a group role to an item."""

    response = item.add_group_role(group_id, role_name=permission_new)
    if response.status_code == 201:
        click.echo(
            f"Successfully added group {group_id} as '{permission_new}' to"
            f" {repr(item)}."
        )
    elif response.status_code == 409:
        response_change = item.change_group_role(
            group_id=group_id, role_name=permission_new
        )
        if response_change.status_code == 200:
            click.echo(f"Group {group_id} is '{permission_new}' of {repr(item)}.")
        else:
            print_request_error(response=response_change)
    else:
        print_request_error(response=response)


def item_remove_group_role(item, group_id):
    """Remove a group role from an item."""

    response = item.remove_group_role(group_id)
    if response.status_code == 204:
        click.echo(f"Group {group_id} was removed from {repr(item)}.")
    else:
        print_request_error(response=response)


def item_remove_user(item, user_id):
    """Remove a user from an item."""

    response = item.remove_user(user_id=user_id)
    if response.status_code == 204:
        click.echo(f"User {user_id} was removed from {repr(item)}.")
    else:
        print_request_error(response=response)


def item_print_info(item, pipe=False, **kwargs):
    """Print basic information of an item."""

    meta = item.meta

    if not pipe:
        click.echo(
            f"Information of {repr(item)}:\nTitle: {meta['title']}\n"
            f"Identifier: {meta['identifier']}."
        )
    if kwargs["description"]:
        click.echo(f"Description: {meta['plain_description']}")

    if kwargs["visibility"]:
        click.echo(f"Visibility: {meta['visibility']}")

    if isinstance(item, Record):
        if "filelist" in kwargs:
            if kwargs["filelist"]:
                response = item.get_filelist(page=kwargs["page"])
                if response.status_code == 200:
                    payload = response.json()
                    click.echo(
                        f"Found {payload['_pagination']['total_items']} file(s) on "
                        f"{payload['_pagination']['total_pages']} page(s).\n"
                        f"Showing results of page {kwargs['page']}:"
                    )
                    for results in payload["items"]:
                        click.echo(
                            f"Found file '{results['name']}' with id '{results['id']}'."
                        )

            if "metadata" in kwargs:
                if kwargs["metadata"]:
                    if not pipe:
                        click.echo("Metadata:")

                    click.echo(
                        json.dumps(
                            item.meta["extras"],
                            indent=2,
                            sort_keys=True,
                            ensure_ascii=False,
                        )
                    )


def item_delete(item, i_am_sure):
    """Delete an item."""

    if not i_am_sure:
        click.echo(
            f"If you are sure you want to delete {repr(item)}, "
            "use the flag --i-am-sure."
        )
        sys.exit(1)

    response = item.delete()
    if response.status_code == 204:
        click.echo(f"Deleting {repr(item)} was successful.")
    else:
        click.echo(f"Deleting {repr(item)} was not successful.")
        print_request_error(response=response)


def item_add_record_link(item, record_id):
    """Add an item to a record."""

    response = item.add_record_link(record_id=record_id)
    if response.status_code == 201:
        click.echo(f"Successfully linked record {record_id} to {repr(item)}.")
    else:
        click.echo(f"Linking record {record_id} to {repr(item)} was not successful.")
        print_request_error(response=response)


def item_remove_record_link(item, record_id):
    """Remove a record link from an item."""

    response = item.remove_record_link(record_id=record_id)
    if response.status_code == 204:
        click.echo(f"Successfully removed record {record_id} from {repr(item)}.")
    else:
        click.echo(f"Removing record {record_id} from {repr(item)} was not successful.")
        print_request_error(response=response)


def item_add_collection_link(item, collection_id):
    """Add an item to a collection."""

    response = item.add_collection_link(collection_id=collection_id)
    if response.status_code == 201:
        click.echo(f"Successfully linked collection {collection_id} to {repr(item)}.")
    elif response.status_code == 409:
        click.echo(
            f"Link from {repr(item)} to collection {collection_id} already exsists. "
            "Nothing to do."
        )
    else:
        click.echo(
            f"Linking collection {collection_id} to {repr(item)} was not successful."
        )
        print_request_error(response=response)


def item_remove_collection_link(item, collection_id):
    """Remove an item link from a collection."""

    response = item.remove_collection_link(collection_id=collection_id)
    if response.status_code == 204:
        click.echo(
            f"Successfully removed collection {collection_id} from {repr(item)}."
        )
    else:
        click.echo(
            f"Removing collection {collection_id} from {repr(item)} was not successful."
        )
        print_request_error(response=response)


def item_remove_group_link(item, group_id):
    """Remove group link from an item."""

    response = item.remove_group_link(group_id=group_id)
    if response.status_code == 204:
        click.echo(f"Successfully removed group {group_id} from {repr(item)}.")
    else:
        click.echo(
            f"Removing group {group_id} from {repr(item)} was " "not successful."
        )
        print_request_error(response=response)


def item_add_tag(item, tag):
    """Add a tag to an item."""

    tag = tag.lower()
    response = item.add_tag(tag)
    if response is None:
        click.echo(f"Tag '{tag}' already present in {repr(item)}. Nothing to do.")
    elif response.status_code == 200:
        click.echo(f"Successfully added tag '{tag}' to {repr(item)}.")
    else:
        click.echo(f"Adding tag '{tag}' to {repr(item)} was not " "successful.")
        print_request_error(response=response)


def item_remove_tag(item, tag):
    """Remove a tag from an item."""

    if not item.check_tag(tag):
        click.echo(f"Tag '{tag}' not resent in {repr(item)}. Nothing to do.")
        sys.exit(0)

    response = item.remove_tag(tag)

    if response.status_code == 200:
        click.echo(f"Successfully removed tag '{tag}' from {repr(item)}.")
    else:
        click.echo(f"Removing tag '{tag}' from {repr(item)} was not successful.")
        print_request_error(response=response)


def search_resources_init(token=None, host=None):
    """Init a search request."""

    # print to standard error since standard output may be used for piping
    try:
        return SearchResource()
    except KadiAPYConfigurationError as e:
        click.echo(e, err=True)
        sys.exit(1)


def search_items(search, item, user, my_user_id, **params):
    """Search items."""

    if user is not None and my_user_id:
        click.echo(f"Please specify either an user id or use the flag '-i'.")
        sys.exit(1)

    if my_user_id:
        user = search.pat_user_id

    if user is None:
        response = search.search_items(item, **params)
    else:
        response = search.search_items_user(item, user=user, **params)

    if response.status_code == 200:
        payload = response.json()
        current_page = params["page"]
        if current_page is None:
            current_page = 1
        click.echo(
            f"Found {payload['_pagination']['total_items']} {item.__name__}(s) on "
            f"{payload['_pagination']['total_pages']} page(s).\n"
            f"Showing results of page {current_page}:"
        )
        for results in payload["items"]:
            click.echo(
                f"Found {item.__name__} {results['id']} with title "
                f"'{results['title']}' and identifier '{results['identifier']}'."
            )
    else:
        print_request_error(response=response)


def _upload(r, file_path, replace=False):
    """Delete a file."""

    file_name = file_path.split(os.sep)[-1]

    click.echo(f"Prepare upload of file '{file_name}'")

    response = r.upload_file(file_path=file_path, replace=replace)
    if response.status_code == 409 and not replace:
        click.echo(
            f"A file with the name '{file_name}' already exists.\nFile '{file_name}' "
            "was not uploaded. Use '-f' to force overwriting existing file."
        )
    elif response.status_code == 200:
        click.echo(f"Upload of file '{file_name}' was successful.")
    else:
        click.echo(f"Upload of file '{file_name}' was not successful. ")
        print_request_error(response=response)


def record_add_files(r, file_name, pattern, force):
    """Upload files into a record."""

    if not os.path.isdir(file_name):
        if not os.path.isfile(file_name):
            click.echo(f"File: {file_name} does not exist.")
            sys.exit(1)

        _upload(r, file_path=file_name, replace=force)

    else:
        path_folder = file_name
        filelist = fnmatch.filter(os.listdir(path_folder), pattern)

        for file_upload in filelist:
            file_path = os.path.join(path_folder, file_upload)

            if os.path.isdir(file_path):
                continue

            _upload(r, file_path=file_path, replace=force)


def validate_metadatum(metadatum, value, type, unit):
    """Check correct form for metadatum."""

    metadatum_type = type

    if metadatum_type is None:
        metadatum_type = "string"

    if metadatum_type not in ["string", "integer", "boolean", "float"]:
        click.echo(
            f"The type {metadatum_type} is given. However, only 'string', 'integer', "
            "'boolean' or 'float' are allowed."
        )
        sys.exit(1)

    mapping_type = {
        "string": "str",
        "integer": "int",
        "boolean": "bool",
        "float": "float",
    }

    metadatum_type = mapping_type[metadatum_type]

    if metadatum_type not in ["int", "float"] and unit is not None:
        if unit.strip():
            click.echo("Specifying a unit is only allowed with 'integer' or 'float'.")
            sys.exit(1)
        unit = None

    if metadatum_type == "bool":
        mapping_value = {"true": True, "false": False}
        if value not in mapping_value.keys():
            click.echo(
                "Choosing 'boolean', the value has to be either 'true' or 'false' not "
                f"'{value}'."
            )
            sys.exit(1)
        value = mapping_value[value]

    if metadatum_type == "int":
        try:
            value = int(value)
        except ValueError:
            click.echo(
                f"Choosing 'integer', the value has to be an integer not '{value}'."
            )
            sys.exit(1)

    if metadatum_type == "float":
        try:
            value = float(value)
        except ValueError:
            click.echo(f"Choosing 'float', the value has to be a float not '{value}'.")
            sys.exit(1)

    if metadatum_type == "str":
        try:
            value = str(value)
        except ValueError:
            click.echo(
                f"Choosing 'string', the value has to be a string not '{value}'."
            )
            sys.exit(1)

    metadatum_new = {
        "type": metadatum_type,
        "unit": unit,
        "key": metadatum,
        "value": value,
    }

    return metadatum_new


def record_add_metadatum(r, metadatum_new, force):
    """Add a metadatum to a record."""

    metadatum = metadatum_new["key"]
    unit = metadatum_new["unit"]
    value = metadatum_new["value"]

    if force is False and r.check_metadatum(metadatum):
        click.echo(
            f"Metadatum '{metadatum}' already exists. Use '--force' to overwrite it or "
            "change the name."
        )
        sys.exit(1)

    metadata_before_update = r.meta["extras"]

    response = r.add_metadatum(metadatum_new, force)

    metadata_after_update = r.meta["extras"]

    if response.status_code == 200:
        if metadata_before_update == metadata_after_update:
            click.echo(f"Metadata were not changed.")
        else:
            text_unit = ""
            if unit is not None:
                text_unit = f"and the unit '{unit}' "
            click.echo(
                f"Successfully added metadatum '{metadatum}' with the value '{value}' "
                f"{text_unit}to {repr(r)}."
            )
    else:
        click.echo(
            f"Something went wrong when trying to add new metadatum '{metadatum}'"
            f" to {repr(r)}."
        )
        print_request_error(response=response)


def record_add_record_link(r, record_to, name):
    """Add a record link to a record."""

    response = r.get_record_links(page=1, per_page=100)

    if response.status_code == 200:
        payload = response.json()
        total_pages = payload["_pagination"]["total_pages"]
        for page in range(1, total_pages + 1):
            for results in payload["items"]:
                if results["record_to"]["id"] == record_to and results["name"] == name:
                    click.echo(f"Link already exsists. Nothing to do.")
                    return
            if page < total_pages:
                response = r.get_record_links(page=page + 1, per_page=100)
                if response.status_code == 200:
                    payload = response.json()
                else:
                    print_request_error(response)
        response = r.link_record(record_to=record_to, name=name)
        if response.status_code == 201:
            click.echo(f"Successfully linked {r!r} to record {record_to}.")
        else:
            print_request_error(response=response)
    else:
        print_request_error(response)


def record_add_metadata(r, metadata_new, force):
    """Add metadata to a record."""

    def _callback(obj, case):

        if case == 0:
            click.echo(
                f"Metadatum {obj['key']} is of type"
                f" '{obj['type']}' and will not be replaced."
            )
        if case == 1:
            metadatum_key = obj["key"]
            try:
                metadatum_unit = obj["unit"]
            except:
                metadatum_unit = None
            metadatum_value = obj["value"]

            text_unit = ""
            if metadatum_unit is not None:
                text_unit = f"and the unit '{metadatum_unit}' "
            click.echo(
                f"Found metadatum '{metadatum_key}' with the value"
                f" '{metadatum_value}' {text_unit}to add to"
                f" {r!r}."
            )

    metadata_before_update = r.meta["extras"]

    response = r.add_metadata(metadata_new, force, callback=_callback)

    metadata_after_update = r.meta["extras"]

    if response.status_code == 200:
        if metadata_before_update == metadata_after_update:
            click.echo(f"Metadata were not changed.")
        else:
            click.echo(f"Successfully updated the metadata of {r!r}.")
    else:
        click.echo(
            f"Something went wrong when trying to add new metadata to {repr(r)}."
        )
        print_request_error(response=response)


def cli_add_metadata(r, metadata, file, force):
    """Add metadata with dict or a list of dicts as input."""

    if (metadata is None and file is None) or (
        metadata is not None and file is not None
    ):
        click.echo("Please specify either '-m' or '-p'.")
        sys.exit(1)

    try:
        if file:
            if not os.path.isfile(file):
                click.echo(f"File: '{file}' does not exist.")
                sys.exit(1)

            with open(file) as f:
                metadata = json.load(f)
        else:
            metadata = json.loads(metadata)
    except json.JSONDecodeError as e:
        click.echo(f"Error loading JSON input ({e}).")
        sys.exit(1)

    response = r.add_metadata(metadata_new=metadata, force=force)

    if response.status_code == 200:
        click.echo(f"Successfully added metadata to {r!r}.")
    else:
        print_request_error(response=response)


def _rename_duplicate_entry(filepath_store, index):
    path = pathlib.Path(filepath_store)
    base = ""
    if len(path.parts) > 1:
        base = os.path.join(*path.parts[:-1])
    file_name = f"{path.stem}_{index}{path.suffix}"
    return os.path.join(base, file_name)


def record_get_file(r, filepath, force, file_name=None, file_id=None):
    """Download one file or all files from a record."""

    list_file_ids = []
    list_file_names = []

    if file_id is not None:
        list_file_ids.append(file_id)
        list_file_names.append(r.get_file_name(file_id))

    elif file_name is not None:
        list_file_ids.append(r.get_file_id(file_name))
        list_file_names.append(file_name)

    else:
        page = 1
        response = r.get_filelist(page=page, per_page=100)

        if response.status_code == 200:
            payload = response.json()
            total_pages = payload["_pagination"]["total_pages"]
            for page in range(1, total_pages + 1):
                if page != 1:
                    response = r.get_filelist(page=page, per_page=100)
                    payload = response.json()

                for results in payload["items"]:
                    list_file_ids.append(results["id"])
                    list_file_names.append(results["name"])
        else:
            print_request_error(response=response)

        number_files = len(list_file_ids)
        if number_files == 0:
            click.echo(f"No files present in {repr(r)}.")
            return

        click.echo(f"Starting to download {number_files} file(s) from {repr(r)}.")

    list_downloaded = []

    for name_iter, id_iter in zip(list_file_names, list_file_ids):
        filepath_store = os.path.join(filepath, name_iter)
        index = 2
        filepath_temp = filepath_store

        if force:
            while filepath_temp in list_downloaded:
                filepath_temp = _rename_duplicate_entry(filepath_store, index)
                index += 1

            list_downloaded.append(filepath_temp)

        else:
            while os.path.isfile(filepath_temp):
                filepath_temp = _rename_duplicate_entry(filepath_store, index)
                index += 1

        response = r.download_file(id_iter, filepath_temp)

        if response.status_code == 200:
            click.echo(
                f"Successfully downloaded file '{name_iter}' from {repr(r)} and stored "
                f"in {filepath_temp}."
            )
        else:
            click.echo(
                f"Something went wrong when trying to download file '{file_name}' from "
                f"{repr(r)}. \nMaybe the file '{file_name}' is not present in "
                f"{repr(r)}."
            )
            print_request_error(response=response)
