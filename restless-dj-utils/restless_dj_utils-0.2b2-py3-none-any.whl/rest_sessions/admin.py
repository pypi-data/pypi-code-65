"""
Admin configuration
"""
from django.contrib import admin
from .models import APISession, VerifyToken


@admin.register(APISession)
class SessionAdmin(admin.ModelAdmin):
    """Session admin config"""

    readonly_fields = ("user", "created", "remote_address", "user_agent")
    search_fields = ("user__email",)
    list_filter = ("is_active",)
    list_display = ("user", "created", "remote_address", "is_active")

    def has_add_permission(self, request):
        return False


@admin.register(VerifyToken)
class VerifyTokenAdmin(admin.ModelAdmin):
    """VerifyToken admin config"""

    readonly_fields = ("user", "created", "token")
    search_fields = ("user__email",)
    list_display = ("user", "created")

    def has_add_permission(self, request):
        return False
