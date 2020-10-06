from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .forms import UserCreationForm, UserChangeForm
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm
    model = User
    list_display = ('id', 'email', 'last_name', 'first_name', 'middle_name', 'is_staff', 'is_superuser', 'is_active',)
    list_display_links = ('id', 'email', 'last_name', 'first_name', 'middle_name')
    list_filter = ('is_staff', 'is_active',)
    fieldsets = (
        (None, {'fields': ('email', 'last_name', 'first_name', 'middle_name', 'password')}),
        (_('Permissions'), {'fields': ('is_staff', 'is_superuser', 'is_active')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'last_name', 'first_name', 'middle_name', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active')}
        ),
    )
    search_fields = ('email', 'last_name', 'first_name', 'middle_name')
    ordering = ('email',)