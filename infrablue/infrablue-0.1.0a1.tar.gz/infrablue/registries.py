"""Custom registries for some preference containers."""

from dynamic_preferences.registries import PerInstancePreferenceRegistry


class SitePreferenceRegistry(PerInstancePreferenceRegistry):
    """Registry for preferences valid for a site."""

    pass


class GroupPreferenceRegistry(PerInstancePreferenceRegistry):
    """Registry for a preference valid for a group."""

    pass


site_preferences_registry = SitePreferenceRegistry()
group_preferences_registry = GroupPreferenceRegistry()
