import os
from glob import glob

from django.utils.translation import gettext_lazy as _

from dynaconf import LazySettings

ENVVAR_PREFIX_FOR_DYNACONF = "INFRABLUE"
DIRS_FOR_DYNACONF = ["/etc/infrablue"]

SETTINGS_FILE_FOR_DYNACONF = []
for directory in DIRS_FOR_DYNACONF:
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.ini"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.yaml"))
    SETTINGS_FILE_FOR_DYNACONF += glob(os.path.join(directory, "*.toml"))

_settings = LazySettings(
    ENVVAR_PREFIX_FOR_DYNACONF=ENVVAR_PREFIX_FOR_DYNACONF,
    SETTINGS_FILE_FOR_DYNACONF=SETTINGS_FILE_FOR_DYNACONF,
)

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = _settings.get("secret_key", "DoNotUseInProduction")

DEBUG = _settings.get("maintenance.debug", False)

ALLOWED_HOSTS = _settings.get("http.allowed_hosts", ["*"])

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sites",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    "infrablue.apps.InfrablueConfig",
    "material",
    "menu_generator",
    "django_yarnpkg",
    "favicon",
    "django_any_js",
    "sass_processor",
    "django_otp.plugins.otp_totp",
    "django_otp.plugins.otp_static",
    "django_otp",
    "otp_yubikey",
    "dynamic_preferences",
    "dynamic_preferences.users.apps.UserPreferencesConfig",
    "bigbluebutton.django.apps.BigbluebuttonConfig",
    "django_registration",
    "two_factor",
    "guardian",
]

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "django_yarnpkg.finders.NodeModulesFinder",
    "sass_processor.finders.CssFinder",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.contrib.sites.middleware.CurrentSiteMiddleware",
]

ROOT_URLCONF = "infrablue.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "dynamic_preferences.processors.global_preferences",
            ],
        },
    },
]

WSGI_APPLICATION = "infrablue.wsgi.application"

# Database
# https://docs.djangoproject.com/en/3.0/ref/settings/#databases

DATABASES = {
}

DATABASE_TYPE = _settings.get("database.type", "sqlite3")
if DATABASE_TYPE == "sqlite3":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": _settings.get("database.name", "infrablue.db"),
        "ATOMIC_REQUESTS": True,
    }
elif DATABASE_TYPE == "postgresql":
    DATABASES["default"] = {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _settings.get("database.name", "infrablue"),
        "USER": _settings.get("database.username", "infrablue"),
        "PASSWORD": _settings.get("database.password", None),
        "HOST": _settings.get("database.host", "127.0.0.1"),
        "PORT": _settings.get("database.port", "5432"),
        "ATOMIC_REQUESTS": True,
    }


if _settings.get("caching.memcached.enabled", False):
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.memcached.MemcachedCache",
            "LOCATION": _settings.get("caching.memcached.address", "127.0.0.1:11211"),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/3.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",},
]

# Authentication backends are dynamically populated
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    'guardian.backends.ObjectPermissionBackend',
]

if _settings.get("auth.social", None):
    CONTEXT_PROCESSORS = [
        "social_django.context_processors.backends",
        "social_django.context_processors.login_redirect",
    ]
    TEMPLATES[0]["OPTIONS"]["context_processors"].append(CONTEXT_PROCESSORS)

    BACKENDS = [
        "social_core.backends.open_id.OpenIdAuth",
        "social_core.backends.google.GoogleOpenId",
        "social_core.backends.google.GoogleOAuth2",
        "social_core.backends.google.GoogleOAuth",
        "social_core.backends.twitter.TwitterOAuth",
        "social_core.backends.yahoo.YahooOpenId",
    ]
    AUTHENTICATION_BACKENDS.append(BACKENDS)

    INSTALLED_APPS.append("social_django")

if _settings.get("ldap.uri", None):
    # LDAP dependencies are not necessarily installed, so import them here
    import ldap  # noqa
    from django_auth_ldap.config import (
        LDAPSearch,
        NestedGroupOfNamesType,
        NestedGroupOfUniqueNamesType,
        PosixGroupType,
    )  # noqa

    # Enable Django's integration to LDAP
    AUTHENTICATION_BACKENDS.append("django_auth_ldap.backend.LDAPBackend")

    AUTH_LDAP_SERVER_URI = _settings.get("ldap.uri")

    # Optional: non-anonymous bind
    if _settings.get("ldap.bind.dn", None):
        AUTH_LDAP_BIND_DN = _settings.get("ldap.bind.dn")
        AUTH_LDAP_BIND_PASSWORD = _settings.get("ldap.bind.password")

    # Search attributes to find users by username
    AUTH_LDAP_USER_SEARCH = LDAPSearch(
        _settings.get("ldap.users.base"),
        ldap.SCOPE_SUBTREE,
        _settings.get("ldap.users.filter", "(uid=%(user)s)"),
    )

    # Mapping of LDAP attributes to Django model fields
    AUTH_LDAP_USER_ATTR_MAP = {
        "first_name": _settings.get("ldap.map.first_name", "givenName"),
        "last_name": _settings.get("ldap.map.last_name", "sn"),
        "email": _settings.get("ldap.map.email", "mail"),
    }

    # Discover flags by LDAP groups
    if _settings.get("ldap.groups.base", None):
        AUTH_LDAP_GROUP_SEARCH = LDAPSearch(
            _settings.get("ldap.groups.base"),
            ldap.SCOPE_SUBTREE,
            _settings.get(
                "ldap.groups.filter",
                "(objectClass=%s)" % _settings.get("ldap.groups.type", "groupOfNames"),
            ),
        )

        _group_type = _settings.get("ldap.groups.type", "groupOfNames").lower()
        if _group_type == "groupofnames":
            AUTH_LDAP_GROUP_TYPE = NestedGroupOfNamesType()
        elif _group_type == "groupofuniquenames":
            AUTH_LDAP_GROUP_TYPE = NestedGroupOfUniqueNamesType()
        elif _group_type == "posixgroup":
            AUTH_LDAP_GROUP_TYPE = PosixGroupType()

        AUTH_LDAP_USER_FLAGS_BY_GROUP = {}
        for _flag in ["is_active", "is_staff", "is_superuser"]:
            _dn = _settings.get("ldap.groups.flags.%s" % _flag, None)
            if _dn:
                AUTH_LDAP_USER_FLAGS_BY_GROUP[_flag] = _dn

        # Backend admin requires superusers to also be staff members
        if (
            "is_superuser" in AUTH_LDAP_USER_FLAGS_BY_GROUP
            and "is_staff" not in AUTH_LDAP_USER_FLAGS_BY_GROUP
        ):
            AUTH_LDAP_USER_FLAGS_BY_GROUP["is_staff"] = AUTH_LDAP_USER_FLAGS_BY_GROUP[
                "is_superuser"
            ]

# Internationalization
# https://docs.djangoproject.com/en/3.0/topics/i18n/

LANGUAGES = [
    ("de", _("German")),
    ("en", _("English")),
]
LANGUAGE_CODE = _settings.get("l10n.lang", "en")
TIME_ZONE = _settings.get("l10n.tz", "UTC")
USE_I18N = True
USE_L10N = True
USE_TZ = True

SITE_ID = 1

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/3.0/howto/static-files/

STATIC_URL = _settings.get("static.url", "/static/")
MEDIA_URL = _settings.get("media.url", "/media/")

STATIC_ROOT = _settings.get("static.root", os.path.join(BASE_DIR, "static"))
MEDIA_ROOT = _settings.get("media.root", os.path.join(BASE_DIR, "media"))
NODE_MODULES_ROOT = _settings.get("node_modules.root", os.path.join(BASE_DIR, "node_modules"))

YARN_INSTALLED_APPS = [
    "jquery",
    "materialize-css",
    "material-design-icons-iconfont",
    "select2",
    "select2-materialize",
]

JS_URL = _settings.get("js_assets.url", STATIC_URL)
JS_ROOT = _settings.get("js_assets.root", NODE_MODULES_ROOT + "/node_modules")

DYNAMIC_PREFERENCES = {
    "REGISTRY_MODULE": "preferences",
}

SELECT2_CSS = JS_URL + "/select2/dist/css/select2.min.css"
SELECT2_JS = JS_URL + "/select2/dist/js/select2.min.js"
SELECT2_I18N_PATH = JS_URL + "/select2/dist/js/i18n"

ANY_JS = {
    "materialize": {"js_url": JS_URL + "/materialize-css/dist/js/materialize.min.js"},
    "jQuery": {"js_url": JS_URL + "/jquery/dist/jquery.min.js"},
    "material-design-icons": {
        "css_url": JS_URL + "/material-design-icons-iconfont/dist/material-design-icons.css"
    },
    "select2-materialize": {
        "css_url": JS_URL + "/select2-materialize/select2-materialize.css",
        "js_url": JS_URL + "/select2-materialize/index.js",
    },
}

SASS_PROCESSOR_ENABLED = True
SASS_PROCESSOR_AUTO_INCLUDE = False
SASS_PROCESSOR_CUSTOM_FUNCTIONS = {
    "get-colour": "infrablue.util.sass_helpers.get_colour",
    "get-preference": "infrablue.util.sass_helpers.get_preference",
}
SASS_PROCESSOR_INCLUDE_DIRS = [
    _settings.get("materialize.sass_path", JS_ROOT + "/materialize-css/sass/"),
    STATIC_ROOT,
]

ADMINS = _settings.get("contact.admins", [])
SERVER_EMAIL = _settings.get("contact.from", "root@localhost")
DEFAULT_FROM_EMAIL = _settings.get("contact.from", "root@localhost")
MANAGERS = _settings.get("contact.admins", [])

if _settings.get("mail.server.host", None):
    EMAIL_HOST = _settings.get("mail.server.host")
    EMAIL_USE_TLS = _settings.get("mail.server.tls", False)
    EMAIL_USE_SSL = _settings.get("mail.server.ssl", False)
    if _settings.get("mail.server.port", None):
        EMAIL_PORT = _settings.get("mail.server.port")
    if _settings.get("mail.server.user", None):
        EMAIL_HOST_USER = _settings.get("mail.server.user")
        EMAIL_HOST_PASSWORD = _settings.get("mail.server.password")

LOGIN_URL = "two_factor:login"
LOGIN_REDIRECT_URL = "index"

if _settings.get("2fa.call.enabled", False):
    if "two_factor.middleware.threadlocals.ThreadLocals" not in MIDDLEWARE:
        MIDDLEWARE.insert(
            MIDDLEWARE.index("django_otp.middleware.OTPMiddleware") + 1,
            "two_factor.middleware.threadlocals.ThreadLocals",
        )
    TWO_FACTOR_CALL_GATEWAY = "two_factor.gateways.twilio.gateway.Twilio"

if _settings.get("2fa.sms.enabled", False):
    if "two_factor.middleware.threadlocals.ThreadLocals" not in MIDDLEWARE:
        MIDDLEWARE.insert(
            MIDDLEWARE.index("django_otp.middleware.OTPMiddleware") + 1,
            "two_factor.middleware.threadlocals.ThreadLocals",
        )
    TWO_FACTOR_SMS_GATEWAY = "two_factor.gateways.twilio.gateway.Twilio"

if _settings.get("twilio.sid", None):
    TWILIO_SID = _settings.get("twilio.sid")
    TWILIO_TOKEN = _settings.get("twilio.token")
    TWILIO_CALLER_ID = _settings.get("twilio.callerid")

ACCOUNT_ACTIVATION_DAYS = _settings.get("registration.activation_days", 7)
REGISTRATION_OPEN = _settings.get("registration.allow", True)

BBB_ROLE_CALLBACK = "infrablue.bigbluebutton.get_role"