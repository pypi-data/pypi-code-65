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
from kadi_apy.lib import utils
from kadi_apy.lib.core import Resource


class Collection(Resource):
    """Model to represent collections."""

    base_path = "/collections"

    def __init__(self, id=None, identifier=None, **kwargs):
        super().__init__(id=id, identifier=identifier, **kwargs)

    def add_user(self, user_id, role_name):
        """Add a user."""

        return utils.add_user(self, user_id, role_name)

    def remove_user(self, user_id):
        """Remove a user."""

        return utils.remove_user(self, user_id)

    def change_user_role(self, user_id, role_name):
        """Change a user role."""

        endpoint = f"{self._actions['add_user_role']}/{user_id}"
        data = {"name": role_name}
        return self._patch(endpoint, json=data)

    def add_group_role(self, group_id, role_name):
        """Add a group role to a collection."""

        return utils.add_group_role(self, group_id, role_name)

    def remove_group_role(self, group_id):
        """Remove a group role from a collection."""

        return utils.remove_group_role(self, group_id)

    def change_group_role(self, group_id, role_name):
        """Change group role."""

        return utils.change_group_role(self, group_id, role_name)

    def get_users(self, **params):
        """Get user of a collection."""

        endpoint = f"{self.base_path}/{self.id}/roles/users"
        return self._get(endpoint, params=params)

    def add_record_link(self, record_id):
        """Add a record to a collection."""

        return utils.add_record_link(self, record_id)

    def remove_record_link(self, record_id):
        """Remove a record from a collection."""

        return utils.remove_record(self, record_id)

    def get_records(self, **params):
        """Get records from a collection. Supports pagination."""

        endpoint = f"{self.base_path}/{self.id}/records"
        return self._get(endpoint, params=params)

    def get_groups(self, **params):
        """Get groups of a collection. Supports pagination."""

        endpoint = f"{self.base_path}/{self.id}/groups"
        return self._get(endpoint, params=params)

    def add_tag(self, tag):
        """Add a tag to a collection."""

        return utils.add_tag(self, tag)

    def remove_tag(self, tag):
        """Remove a tag from a collection."""

        return utils.remove_tag(self, tag)

    def get_tags(self):
        """Get all tags from a collection."""

        return utils.get_tags(self)

    def check_tag(self, tag):
        """Check if a collection has a certain tag."""

        return utils.check_tag(self, tag)

    def set_attribute(self, attribute, value):
        """Set attribute."""

        return utils.set_attribute(self, attribute, value)
