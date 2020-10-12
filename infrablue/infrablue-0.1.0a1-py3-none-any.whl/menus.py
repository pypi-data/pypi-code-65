from django.conf import settings
from django.utils.translation import gettext_lazy as _

MENUS = {
    "NAV_MENU_INFRABLUE": [
        {
            "name": _("Home"),
            "url": "index",
            "icon": "home",
            # "validators": ["menu_generator.validators.is_authenticated"],
        },
        {
            "name": _("Login"),
            "url": settings.LOGIN_URL,
            "icon": "lock_open",
            "validators": ["menu_generator.validators.is_anonymous"],
        },
        {
            "name": _("Register"),
            "url": "django_registration_register",
            "icon": "how_to_reg",
            "validators": ["menu_generator.validators.is_anonymous"],
        },
        {
            "name": _("Me"),
            "url": "self_detail",
            "icon": "face",
            "validators": ["menu_generator.validators.is_authenticated"],
        },
        {
            "name": _("Server Groups"),
            "url": "server_group_list",
            "icon": "group_work",
            "validators": [
                "menu_generator.validators.is_authenticated",
                "menu_generator.validators.is_staff",
            ],
        },
        {
            "name": _("Meetings"),
            "url": "meeting_list",
            "icon": "voice_chat",
            "validators": ["menu_generator.validators.is_authenticated"],
        },
        {
            "name": _("User Management"),
            "url": "#",
            "icon": "supervisor_account",
            "validators": [
                "menu_generator.validators.is_authenticated",
                "menu_generator.validators.is_staff",
            ],
            "submenu": [
                {
                    "name": _("Users"),
                    "url": "user_list",
                    "icon": "person",
                    "validators": ["menu_generator.validators.is_authenticated", "menu_generator.validators.is_staff"],
                },
                {
                    "name": _("Groups"),
                    "url": "group_list",
                    "icon": "group",
                    "validators": ["menu_generator.validators.is_authenticated", "menu_generator.validators.is_staff"],
                },
            ],
        },
        {
            "name": _("Admin"),
            "url": "#",
            "icon": "security",
            "validators": [
                "menu_generator.validators.is_authenticated",
                "menu_generator.validators.is_staff",
                # ("infrablue.core.util.predicates.permission_validator", "core.view_admin_menu"),
            ],
            "submenu": [
                {
                    "name": _("Configuration"),
                    "url": "preferences_site",
                    "icon": "build",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        "menu_generator.validators.is_staff",
                        # (
                        #     "infrablue.core.util.predicates.permission_validator",
                        #     "core.change_site_preferences",
                        # ),
                    ],
                },
                {
                    "name": _("Backend Admin"),
                    "url": "admin:index",
                    "icon": "settings",
                    "validators": [
                        "menu_generator.validators.is_authenticated",
                        "menu_generator.validators.is_superuser",
                    ],
                },
            ],
        },
        {
            "name": _("Logout"),
            "url": "logout",
            "icon": "exit_to_app",
            "validators": ["menu_generator.validators.is_authenticated"],
        },
    ],
}
