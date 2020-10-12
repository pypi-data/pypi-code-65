import os
import pkgutil
from datetime import datetime, timedelta
from importlib import import_module
from itertools import groupby
from operator import itemgetter
from typing import Any, Callable, Optional, Sequence, Union
from uuid import uuid4

from django.conf import settings
from django.db.models import Model
from django.http import HttpRequest
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.functional import lazy


def copyright_years(years: Sequence[int], seperator: str = ", ", joiner: str = "–") -> str:
    """Take a sequence of integegers and produces a string with ranges.

    >>> copyright_years([1999, 2000, 2001, 2005, 2007, 2008, 2009])
    '1999–2001, 2005, 2007–2009'
    """
    ranges = [
        list(map(itemgetter(1), group))
        for _, group in groupby(enumerate(years), lambda e: e[1] - e[0])
    ]
    years_strs = [
        str(range_[0]) if len(range_) == 1 else joiner.join([str(range_[0]), str(range_[-1])])
        for range_ in ranges
    ]

    return seperator.join(years_strs)


def dt_show_toolbar(request: HttpRequest) -> bool:
    """Add a helper to determin if Django debug toolbar should be displayed.

    Extends the default behaviour by enabling DJDT for superusers independent
    of source IP.
    """
    from debug_toolbar.middleware import show_toolbar  # noqa

    if not settings.DEBUG:
        return False

    if show_toolbar(request):
        return True
    elif hasattr(request, "user") and request.user.is_superuser:
        return True

    return False


def get_app_packages() -> Sequence[str]:
    """Find all packages within the infrablue.apps namespace."""
    # Import error are non-fatal here because probably simply no app is installed.
    try:
        import infrablue.apps
    except ImportError:
        return []

    return [f"infrablue.apps.{pkg[1]}" for pkg in pkgutil.iter_modules(infrablue.apps.__path__)]


def merge_app_settings(
    setting: str, original: Union[dict, list], deduplicate: bool = False
) -> Union[dict, list]:
    """Merge app settings.

    Get a named settings constant from all apps and merge it into the original.
    To use this, add a settings.py file to the app, in the same format as Django's
    main settings.py.

    Note: Only selected names will be imported frm it to minimise impact of
    potentially malicious apps!
    """
    for pkg in get_app_packages():
        try:
            mod_settings = import_module(pkg + ".settings")
        except ImportError:
            # Import errors are non-fatal. They mean that the app has no settings.py.
            continue

        app_setting = getattr(mod_settings, setting, None)
        if not app_setting:
            # The app might not have this setting or it might be empty. Ignore it in that case.
            continue

        for entry in app_setting:
            if entry in original:
                if not deduplicate:
                    raise AttributeError(f"{entry} already set in original.")
            else:
                if isinstance(original, list):
                    original.append(entry)
                elif isinstance(original, dict):
                    original[entry] = app_setting[entry]
                else:
                    raise TypeError("Only dict and list settings can be merged.")


def get_site_preferences():
    """Get the preferences manager of the current site."""
    from django.contrib.sites.models import Site  # noqa

    return Site.objects.get_current().preferences


def lazy_preference(section: str, name: str) -> Callable[[str, str], Any]:
    """Lazily get a config value from dynamic preferences.

    Useful to bind preferences
    to other global settings to make them available to third-party apps that are not
    aware of dynamic preferences.
    """

    def _get_preference(section: str, name: str) -> Any:
        return get_site_preferences()[f"{section}__{name}"]

    # The type is guessed from the default value to improve lazy()'s behaviour
    # FIXME Reintroduce the behaviour described above
    return lazy(_get_preference, str)(section, name)


def lazy_get_favicon_url(
    title: str, size: int, rel: str, default: Optional[str] = None
) -> Callable[[str, str], Any]:
    """Lazily get the URL to a favicon image."""

    def _get_favicon_url(size: int, rel: str) -> Any:
        from favicon.models import Favicon  # noqa

        try:
            favicon = Favicon.on_site.get(title=title)
        except Favicon.DoesNotExist:
            return default
        else:
            return favicon.get_favicon(size, rel).faviconImage.url

    return lazy(_get_favicon_url, str)(size, rel)


def is_impersonate(request: HttpRequest) -> bool:
    """Check whether the user was impersonated by an admin."""
    if hasattr(request, "user"):
        return getattr(request.user, "is_impersonate", False)
    else:
        return False


def has_person(obj: Union[HttpRequest, Model]) -> bool:
    """Check wehether a model object has a person attribute linking it to a Person object.

    The passed object can also be a HttpRequest object, in which case its
    associated User object is unwrapped and tested.
    """
    if isinstance(obj, HttpRequest):
        if hasattr(obj, "user"):
            obj = obj.user
        else:
            return False

    person = getattr(obj, "person", None)
    if person is None:
        return False
    elif getattr(person, "is_dummy", False):
        return False
    else:
        return True


def celery_optional(orig: Callable) -> Callable:
    """Add a decorator that makes Celery optional for a function.

    If Celery is configured and available, it wraps the function in a Task
    and calls its delay method when invoked; if not, it leaves it untouched
    and it is executed synchronously.
    """
    if hasattr(settings, "CELERY_RESULT_BACKEND"):
        from ..celery import app  # noqa

        task = app.task(orig)

    def wrapped(*args, **kwargs):
        if hasattr(settings, "CELERY_RESULT_BACKEND"):
            task.delay(*args, **kwargs)
        else:
            orig(*args, **kwargs)

    return wrapped


def path_and_rename(instance, filename: str, upload_to: str = "files") -> str:
    """Update path of an uploaded file and renames it to a random UUID in Django FileField."""
    _, ext = os.path.splitext(filename)

    # set filename as random string
    new_filename = f"{uuid4().hex}.{ext}"

    # Create upload directory if necessary
    os.makedirs(os.path.join(settings.MEDIA_ROOT, upload_to), exist_ok=True)

    # return the whole path to the file
    return os.path.join(upload_to, new_filename)


def custom_information_processor(request: HttpRequest) -> dict:
    """Provide custom information in all templates."""
    from ..models import CustomMenu

    return {
        "FOOTER_MENU": CustomMenu.get_default("footer"),
    }


def now_tomorrow() -> datetime:
    """Return current time tomorrow."""
    return timezone.now() + timedelta(days=1)


def objectgetter_optional(
    model: Model, default: Optional[Any] = None, default_eval: bool = False
) -> Callable[[HttpRequest, Optional[int]], Model]:
    """Get an object by pk, defaulting to None."""

    def get_object(request: HttpRequest, id_: Optional[int] = None, **kwargs) -> Model:
        if id_ is not None:
            return get_object_or_404(model, pk=id_)
        else:
            return eval(default) if default_eval else default  # noqa:S307

    return get_object
