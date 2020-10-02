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
from kadi_apy.cli.utils import print_request_error
from kadi_apy.lib.core import SearchUser


@kadi_apy.group()
def users():
    """Commands to manage users."""


@users.command()
@click.option("-p", "--page", help="Page for search results", type=int, default=1)
@click.option(
    "-n",
    "--per-page",
    help="Number of results per page",
    type=click.IntRange(1, 100, clamp=True),
    default=10,
)
@click.option(
    "-n",
    "--per-page",
    help="Number of results per page",
    type=click.IntRange(1, 100, clamp=True),
    default=10,
)
@click.option(
    "-f",
    "--filter",
    help="To filter the users by their display name or username",
    type=str,
    default=None,
)
@apy_command
def get_users(**kwargs):
    """Search for users."""

    s = SearchUser()

    response = s.search_users(**kwargs)
    if response.status_code == 200:
        payload = response.json()
        current_page = kwargs["page"]
        if current_page is None:
            current_page = 1
        click.echo(
            f"Found {payload['_pagination']['total_items']} user(s) on "
            f"{payload['_pagination']['total_pages']} page(s).\n"
            f"Showing results of page {current_page}:"
        )
        for results in payload["items"]:
            click.echo(
                f"Found user '{results['identity']['displayname']}' with id "
                f"'{results['id']}' and identity_type "
                f"'{results['identity']['identity_type']}'."
            )
    else:
        print_request_error(response=response)
