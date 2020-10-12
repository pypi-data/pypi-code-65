from typing import Any, Optional

from django.apps import AppConfig
from django.db.models.signals import post_save

from dynamic_preferences.registries import preference_models
from dynamic_preferences.signals import preference_updated

from .registries import group_preferences_registry, site_preferences_registry
from .util.sass_helpers import clean_scss
from .signals import add_preference_permissions


class InfrablueConfig(AppConfig):
    name = "infrablue"

    def ready(self):
        super().ready()

        preference_updated.connect(self.preference_updated)

        sitepreferencemodel = self.get_model("SitePreferenceModel")
        grouppreferencemodel = self.get_model("GroupPreferenceModel")

        preference_models.register(sitepreferencemodel, site_preferences_registry)
        preference_models.register(grouppreferencemodel, group_preferences_registry)

        post_save.connect(add_preference_permissions, sender="auth.User")

    def preference_updated(
        self,
        sender: Any,
        section: Optional[str] = None,
        name: Optional[str] = None,
        old_value: Optional[Any] = None,
        new_value: Optional[Any] = None,
        **kwargs,
    ) -> None:
        if section == "theme":
            if name in ("primary", "secondary"):
                clean_scss()
            elif name in ("favicon", "pwa_icon"):
                from favicon.models import Favicon  # noqa

                is_favicon = name == "favicon"

                if new_value:
                    Favicon.on_site.update_or_create(
                        title=name,
                        defaults={"isFavicon": name == "favicon", "faviconImage": new_value,},
                    )
                else:
                    Favicon.on_site.filter(title=name, isFavicon=is_favicon).delete()
