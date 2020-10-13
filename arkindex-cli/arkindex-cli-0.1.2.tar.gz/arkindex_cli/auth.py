# -*- coding: utf-8 -*-
import logging
import os
import sys
from collections import namedtuple
from pathlib import Path
from typing import Optional, Union

import yaml
from arkindex import ArkindexClient
from rich import print

logger = logging.getLogger("auth")

Profile = namedtuple("Profile", ["slug", "url", "token"])


class Profiles(dict):
    def __init__(self, path: Optional[Path] = None) -> None:
        if not path:
            # Use $XDG_CONFIG_HOME/arkindex/cli.yaml or $HOME/.config/arkindex/cli.yaml
            path = (
                Path(os.environ.get("XDG_CONFIG_HOME") or "~/.config").expanduser()
                / "arkindex"
                / "cli.yaml"
            )
        self.path = path
        self.dir = path.parent
        self.default_profile_name = None
        self.gpg_key = None

        if self.path.exists():
            self.load()

    def load(self) -> None:
        try:
            with self.path.open() as f:
                data = yaml.safe_load(f)
        except (IOError, yaml.YAMLError) as e:
            logger.error(f"Failed to load profiles file: {e}")
            return

        for slug, host_data in data.get("hosts", {}).items():
            self[slug] = Profile(slug, host_data["url"], host_data["token"])

        self.default_profile_name = data.get("default_host")
        self.gpg_key = data.get("gpg_key")

    def get_default_profile(self) -> Optional[Profile]:
        if self.default_profile_name in self:
            return self[self.default_profile_name]

    def set_default_profile(self, name: str) -> None:
        assert name in self, f"Profile {name} does not exist"
        self.default_profile_name = name

    def add_profile(self, slug: str, url: str, token: str) -> None:
        self[slug] = Profile(slug, url, token)

    def get_or_exit(self, slug: Optional[str]) -> Profile:
        """
        Get a Profile, or print a user-friendly message for a missing profile and exit
        """
        if slug:
            profile = self.get(slug)
        else:
            profile = self.get_default_profile()

        if profile is None:
            print(
                "[bright_red]Arkindex profile was not found. Try logging in using [white]arkindex login[/] first."
            )
            sys.exit(2)

        return profile

    def get_api_client(
        self, slug: Optional[Union[str, Profile]] = None
    ) -> Optional[ArkindexClient]:
        if isinstance(slug, Profile):
            profile = slug
        elif slug:
            profile = self.get(slug)
        else:
            profile = self.get_default_profile()

        if profile:
            logger.debug(f"Using profile {profile.slug} ({profile.url})")
            return ArkindexClient(base_url=profile.url, token=profile.token)

    def get_api_client_or_exit(
        self, slug: Optional[Union[str, Profile]] = None
    ) -> ArkindexClient:
        if isinstance(slug, Profile):
            profile = slug
        else:
            profile = self.get_or_exit(slug)
        return self.get_api_client(profile)

    def save(self) -> None:
        data = {
            "default_host": self.default_profile_name,
            "gpg_key": self.gpg_key,
            "hosts": {
                profile.slug: {"url": profile.url, "token": profile.token}
                for profile in self.values()
            },
        }

        # Create parent folders if needed
        self.path.parent.mkdir(parents=True, exist_ok=True)

        with self.path.open("w") as f:
            yaml.safe_dump(data, f, default_flow_style=False)
