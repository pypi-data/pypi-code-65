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


def add_user(self, user_id, role_name):
    """Add a user."""

    endpoint = self._actions["add_user_role"]
    data = {"role": {"name": role_name}, "user": {"id": user_id}}
    return self._post(endpoint, json=data)


def remove_user(self, user_id):
    """Remove a user."""

    endpoint = f"{self._actions['add_user_role']}/{user_id}"
    return self._delete(endpoint, json=None)


def add_group_role(self, group_id, role_name):
    """Add a group role."""

    endpoint = self._actions["add_group_role"]
    data = {"role": {"name": role_name}, "group": {"id": group_id}}
    return self._post(endpoint, json=data)


def remove_group_role(self, group_id):
    """Remove a group role."""

    endpoint = f"{self._actions['add_group_role']}/{group_id}"
    return self._delete(endpoint, json=None)


def change_group_role(self, group_id, role_name):
    """Change a group role."""

    endpoint = f"{self._actions['add_group_role']}/{group_id}"
    data = {"name": role_name}
    return self._patch(endpoint, json=data)


def remove_group_link(self, group_id):
    """Remove a group link."""

    endpoint = f"{self._actions['link_group']}/{group_id}"
    return self._delete(endpoint, json=None)


def add_collection_link(self, collection_id):
    """Add a collection."""

    endpoint = self._actions["link_collection"]
    data = {"id": collection_id}
    return self._post(endpoint, json=data)


def remove_collection_link(self, collection_id):
    """Remove a collection."""

    endpoint = f"{self._actions['link_collection']}/{collection_id}"
    return self._delete(endpoint, json=None)


def add_record_link(self, record_id):
    """Add a record."""

    endpoint = self._actions["link_record"]
    data = {"id": record_id}
    return self._post(endpoint, json=data)


def remove_record_link(self, record_id):
    """Remove a record."""

    endpoint = f"{self._actions['link_record']}/{record_id}"
    return self._delete(endpoint, json=None)


def get_tags(self):
    """Get tags."""

    return self.meta["tags"]


def check_tag(self, tag):
    """Check if a certain tag is already present."""

    for obj in self.get_tags():
        if obj == tag:
            return True
    return False


def add_tag(self, tag):
    """Add a tag."""

    endpoint = self._actions["edit"]
    tags = self.get_tags()
    if self.check_tag(tag) == True:
        return None
    tags.append(tag)
    tags = {"tags": tags}
    return self._patch(endpoint, json=tags)


def remove_tag(self, tag):
    """Remove a tag."""

    endpoint = self._actions["edit"]
    tags = [obj for obj in self.get_tags() if obj != tag]
    tags = {"tags": tags}
    return self._patch(endpoint, json=tags)


def set_attribute(self, attribute, value):
    """Set attribute."""

    endpoint = self._actions["edit"]
    attribute = {attribute: value}
    return self._patch(endpoint, json=attribute)
