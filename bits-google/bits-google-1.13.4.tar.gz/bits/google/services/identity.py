# -*- coding: utf-8 -*-
"""Google Cloud Identity API."""

import re

from bits.google.services.base import Base
from googleapiclient.discovery import build


class CloudIdentity(Base):
    """CloudIdentity class."""

    def __init__(self, credentials):
        """Initialize a class instance."""
        self.ci = build("cloudidentity", "v1", credentials=credentials, cache_discovery=False)

    #
    # Groups
    #
    def create_group(self, email, description=None, display_name=None, labels=None, parent=None):
        """Create a Cloud Identity Group."""
        if not description:
            description = email.split("@")[0]
        if not display_name:
            display_name = email.split("@")[0]
        if not labels:
            labels = {
                "cloudidentity.googleapis.com/groups.discussion_forum": "",
            }
        if not parent:
            parent = "customers/C00q9u7iu"
        body = {
            "description": description,
            "displayName": display_name,
            "groupKey": {"id": email},
            "labels": labels,
            "parent": parent,
        }
        params = {
            "body": body,
            "initialGroupConfig": "WITH_INITIAL_OWNER",
        }
        return self.ci.groups().create(**params).execute()

    def delete_group(self, name):
        """Delete a Cloud Identity Group."""
        if not re.match("groups/", name):
            name = f"groups/{name}"
        return self.ci.groups().delete(name=name).execute()

    def get_group(self, name):
        """Return a Cloud Identity Group."""
        if not re.match("groups/", name):
            name = f"groups/{name}"
        return self.ci.groups().get(name=name).execute()

    def list_groups(self, parent=None, view="BASIC", pageSize=1000):
        """Return a list of groups."""
        if not parent:
            parent = "customers/C00q9u7iu"
        if not re.match("customers/", parent):
            parent = f"customers/{parent}"
        params = {
            "parent": parent,
            "view": view,
            "pageSize": pageSize,
        }
        groups = self.ci.groups()
        request = groups.list(**params)
        return self.get_list_items(groups, request, "groups")

    def lookup_group(self, groupKey):
        """Return Name of a Cloud Identity Group."""
        params = {
            "groupKey_id": groupKey
        }
        return self.ci.groups().lookup(**params).execute()

    def patch_group(self, name, description=None, display_name=None):
        """Patch a Cloud Identity Group."""
        if not re.match("groups/", name):
            name = f"groups/{name}"
        body = {}
        fields = []
        if description:
            body["description"] = description
            fields.append("description")
        if display_name:
            body["displayName"] = display_name
            fields.append("displayName")
        update_mask = ",".join(fields)
        params = {
            "body": body,
            "name": name,
            "updateMask": update_mask
        }
        return self.ci.groups().patch(**params).execute()

    def search_groups(self, query, view="BASIC", pageSize=1000):
        """Return results of a group search."""
        params = {
            "query": query,
            "view": view,
            "pageSize": pageSize,
        }
        groups = self.ci.groups()
        request = groups.search(**params)
        return self.get_list_items(groups, request, "groups")
