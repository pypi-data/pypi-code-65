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
import click

from kadi_apy.cli.main import kadi_apy
from kadi_apy.cli.utils import apy_command
from kadi_apy.cli.utils import id_identifier_options
from kadi_apy.cli.utils import item_add_user
from kadi_apy.cli.utils import item_create
from kadi_apy.cli.utils import item_delete
from kadi_apy.cli.utils import item_edit
from kadi_apy.cli.utils import item_print_info
from kadi_apy.cli.utils import item_remove_user
from kadi_apy.cli.utils import search_items
from kadi_apy.cli.utils import search_resources_init
from kadi_apy.lib.groups import Group


@kadi_apy.group()
def groups():
    """Commands to manage groups."""


@groups.command()
@click.option("-t", "--title", default="my title", type=str, help="Title of the group")
@click.option(
    "-i", "--identifier", required=True, help="Identifier of the group", default=None
)
@click.option(
    "-v",
    "--visibility",
    help="Visibility of the group",
    default="private",
    type=click.Choice(["private", "public"]),
)
@click.option(
    "-p",
    "--pipe",
    help="Use this flag if you want to pipe the returned group id.",
    is_flag=True,
)
@apy_command
def create(**kwargs):
    """Create a group."""

    item_create(class_type=Group, **kwargs)


@groups.command()
@id_identifier_options(class_type=Group, helptext="to edit", init=True)
@click.option(
    "-v",
    "--visibility",
    help="Visibility of the group to set",
    default=None,
    type=click.Choice(["private", "public"]),
)
@click.option("-t", "--title", default=None, type=str, help="Title of the group to set")
@click.option(
    "-d",
    "--description",
    default=None,
    type=str,
    help="Description of the group to set",
)
@apy_command
def edit(g, visibility, title, description):
    """Edit visibility, title or description of a group."""

    item_edit(g, visibility=visibility, title=title, description=description)


@groups.command()
@id_identifier_options(class_type=Group, init=True)
@click.option(
    "-d",
    "--description",
    help="Show the description of the group",
    is_flag=True,
    default=False,
)
@click.option(
    "-v",
    "--visibility",
    help="Show the visibility of the group",
    is_flag=True,
    default=False,
)
@apy_command
def show_info(g, **kwargs):
    """Show info of a group."""

    item_print_info(g, **kwargs)


@groups.command()
@id_identifier_options(class_type=Group, helptext="to add the user", init=True)
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="ID of the user to add to the group",
    type=int,
)
@click.option(
    "-p",
    "--permission-new",
    help="Permission of new user",
    default="member",
    type=click.Choice(["member", "editor", "admin"], case_sensitive=False),
)
@apy_command
def add_user(g, user_id, permission_new):
    """Add a user to a group."""

    item_add_user(g, user_id=user_id, permission_new=permission_new)


@groups.command()
@id_identifier_options(class_type=Group, helptext="to remove the user", init=True)
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="ID of the user to remove from the group",
    type=int,
)
@apy_command
def remove_user(g, user_id):
    """Remove a user from a group."""

    item_remove_user(g, user_id=user_id)


@groups.command()
@id_identifier_options(class_type=Group, helptext="to delete", init=True)
@click.option(
    "--i-am-sure", help="Enable this option to delete the group", is_flag=True
)
@apy_command
def delete(g, i_am_sure):
    """Delete a group."""

    item_delete(g, i_am_sure)


@groups.command()
@click.option("-t", "--tag", help="Tag(s) for search", type=str, multiple=True)
@click.option(
    "-m",
    "--mimetype",
    help="MIME types for search",
    type=str,
    multiple=True,
)
@click.option("-p", "--page", help="Page for search results", type=int, default=1)
@click.option(
    "-n",
    "--per-page",
    help="Number of results per page",
    type=click.IntRange(1, 100, clamp=True),
    default=10,
)
@click.option(
    "-u",
    "--user",
    help="Show created groups or specific user ID. Only those with read access are "
    "shown",
    type=int,
    default=None,
)
@click.option(
    "-i",
    "--my_user_id",
    help="Show only own created groups.",
    is_flag=True,
)
@apy_command
def get_groups(user, my_user_id, **kwargs):
    """Search for groups."""

    s = search_resources_init()

    search_items(s, Group, user=user, my_user_id=my_user_id, **kwargs)
