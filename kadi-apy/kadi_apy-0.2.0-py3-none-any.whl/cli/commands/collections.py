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
from kadi_apy.cli.utils import item_add_group_role
from kadi_apy.cli.utils import item_add_record_link
from kadi_apy.cli.utils import item_add_tag
from kadi_apy.cli.utils import item_add_user
from kadi_apy.cli.utils import item_create
from kadi_apy.cli.utils import item_delete
from kadi_apy.cli.utils import item_edit
from kadi_apy.cli.utils import item_print_info
from kadi_apy.cli.utils import item_remove_group_role
from kadi_apy.cli.utils import item_remove_record_link
from kadi_apy.cli.utils import item_remove_tag
from kadi_apy.cli.utils import item_remove_user
from kadi_apy.cli.utils import search_items
from kadi_apy.cli.utils import search_resources_init
from kadi_apy.lib.collections import Collection
from kadi_apy.lib.groups import Group
from kadi_apy.lib.records import Record


@kadi_apy.group()
def collections():
    """Commands to manage collections."""


@collections.command()
@click.option(
    "-t", "--title", default="my title", type=str, help="Title of the collection"
)
@click.option(
    "-i",
    "--identifier",
    required=True,
    help="Identifier of the collection",
    default=None,
)
@click.option(
    "-v",
    "--visibility",
    help="Visibility of the collection",
    default="private",
    type=click.Choice(["private", "public"]),
)
@click.option(
    "-p",
    "--pipe",
    help="Use this flag if you want to pipe the returned collection id.",
    is_flag=True,
)
@apy_command
def create(**kwargs):
    """Create a collection."""

    item_create(class_type=Collection, **kwargs)


@collections.command()
@id_identifier_options(class_type=Collection, helptext="to edit", init=True)
@click.option(
    "-v",
    "--visibility",
    help="Visibility of the collection to set",
    default=None,
    type=click.Choice(["private", "public"]),
)
@click.option(
    "-t", "--title", default=None, type=str, help="Title of the collection to set"
)
@click.option(
    "-d",
    "--description",
    default=None,
    type=str,
    help="Description of the collection to set",
)
@apy_command
def edit(c, visibility, title, description):
    """Edit visibility, title or description of a collection."""

    item_edit(c, visibility=visibility, title=title, description=description)


@collections.command()
@id_identifier_options(class_type=Collection, init=True)
@click.option(
    "-d",
    "--description",
    help="Show the description of the collection",
    is_flag=True,
    default=False,
)
@click.option(
    "-v",
    "--visibility",
    help="Show the visibility of the collection",
    is_flag=True,
    default=False,
)
@apy_command
def show_info(c, **kwargs):
    """Show info of a collection."""

    item_print_info(c, **kwargs)


@collections.command()
@id_identifier_options(class_type=Collection, helptext="to add the user", init=True)
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="ID of the user to add to the collection",
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
def add_user(c, user_id, permission_new):
    """Add a user to a collection."""

    item_add_user(c, user_id=user_id, permission_new=permission_new)


@collections.command()
@id_identifier_options(class_type=Collection, helptext="to remove the user", init=True)
@click.option(
    "-u",
    "--user-id",
    required=True,
    help="ID of the user to remove from the collection",
    type=int,
)
@apy_command
def remove_user(c, user_id):
    """Remove a user from a collection."""

    item_remove_user(c, user_id=user_id)


@collections.command()
@id_identifier_options(
    class_type=Collection, helptext="to add the group with role permissions", init=True
)
@id_identifier_options(class_type=Group, get_id=True)
@click.option(
    "-p",
    "--permission-new",
    help="Permission of the group",
    default="member",
    type=click.Choice(["member", "editor", "admin"], case_sensitive=False),
)
@apy_command
def add_group_role(c, group_id, permission_new):
    """Add a group role to a collection."""

    item_add_group_role(c, group_id, permission_new)


@collections.command()
@id_identifier_options(class_type=Collection, helptext="to remove the group", init=True)
@id_identifier_options(class_type=Group, get_id=True)
@apy_command
def remove_group_role(c, group_id):
    """Remove a group role from a collection."""

    item_remove_group_role(c, group_id)


@collections.command()
@id_identifier_options(class_type=Collection, helptext="to delete", init=True)
@click.option(
    "--i-am-sure", help="Enable this option to delete the collection", is_flag=True
)
@apy_command
def delete(c, i_am_sure):
    """Delete a collection."""

    item_delete(c, i_am_sure)


@collections.command()
@id_identifier_options(
    class_type=Collection, helptext="to link to the record", init=True
)
@id_identifier_options(
    class_type=Record, helptext="to link to the collection", get_id=True
)
@apy_command
def add_record_link(c, record_id):
    """Link record to a collection."""

    item_add_record_link(c, record_id=record_id)


@collections.command()
@id_identifier_options(
    class_type=Collection, helptext="to remove the record", init=True
)
@id_identifier_options(
    class_type=Record, helptext="remove from the collection", get_id=True
)
@apy_command
def remove_record_link(c, record_id):
    """Remove a record link from a collection."""

    item_remove_record_link(c, record_id=record_id)


@collections.command()
@id_identifier_options(class_type=Collection, helptext="to add a tag", init=True)
@click.option("-t", "--tag", required=True, help="Tag to add", type=str)
@apy_command
def add_tag(c, tag):
    """Add a tag to a collection."""

    item_add_tag(c, tag)


@collections.command()
@id_identifier_options(class_type=Collection, helptext="to remove a tag", init=True)
@click.option("-t", "--tag", required=True, help="Tag to remove", type=str)
@apy_command
def remove_tag(c, tag):
    """Remove a tag from a collection."""

    item_remove_tag(c, tag)


@collections.command()
@click.option("-t", "--tag", help="Tag(s) for search", type=str, multiple=True)
@click.option("-p", "--page", help="Page for search results", type=int)
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
    help="Show created collections or specific user ID. Only those with read access "
    "are shown",
    type=int,
    default=None,
)
@click.option(
    "-i",
    "--my_user_id",
    help="Show only own created collections.",
    is_flag=True,
)
@apy_command
def get_collections(user, my_user_id, **kwargs):
    """Search for collections."""

    s = search_resources_init()

    search_items(s, Collection, user=user, my_user_id=my_user_id, **kwargs)
