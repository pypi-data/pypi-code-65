from django.contrib import admin

# Register your models here.
from .models import StateGroupBinding

class StateBindingAdmin(admin.ModelAdmin):
    filter_horizontal = ['groups']

admin.site.register(StateGroupBinding, StateBindingAdmin)
