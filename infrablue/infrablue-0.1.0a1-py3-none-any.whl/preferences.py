from django.conf import settings
from django.forms import EmailField, ImageField, URLField
from django.utils.translation import gettext_lazy as _

from dynamic_preferences.preferences import Section
from dynamic_preferences.types import FilePreference, StringPreference

from .registries import site_preferences_registry

general = Section("general")
theme = Section("theme")
mail = Section("mail")
notification = Section("notification")
footer = Section("footer")


@site_preferences_registry.register
class SiteTitle(StringPreference):
    section = general
    name = "title"
    default = "InfraBlue"
    required = False
    verbose_name = _("Site title")


@site_preferences_registry.register
class SiteDescription(StringPreference):
    section = general
    name = "description"
    default = "The free frontend for BigBlueButton"
    required = False
    verbose_name = _("Site description")


@site_preferences_registry.register
class ColourPrimary(StringPreference):
    section = theme
    name = "primary"
    default = "#0186df"
    required = False
    verbose_name = _("Primary colour")


@site_preferences_registry.register
class ColourSecondary(StringPreference):
    section = theme
    name = "secondary"
    default = "#fbc02d"
    required = False
    verbose_name = _("Secondary colour")


@site_preferences_registry.register
class Logo(FilePreference):
    section = theme
    field_class = ImageField
    name = "logo"
    verbose_name = _("Logo")


@site_preferences_registry.register
class Favicon(FilePreference):
    section = theme
    field_class = ImageField
    name = "favicon"
    verbose_name = _("Favicon")


@site_preferences_registry.register
class MailOutName(StringPreference):
    section = mail
    name = "name"
    default = "BigBlueButton"
    required = False
    verbose_name = _("Mail out name")


@site_preferences_registry.register
class MailOut(StringPreference):
    section = mail
    name = "address"
    default = settings.DEFAULT_FROM_EMAIL
    required = False
    verbose_name = _("Mail out address")
    field_class = EmailField
