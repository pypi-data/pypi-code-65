from django.contrib import admin
from template_data.models import TemplateData

@admin.register(TemplateData)
class TemplateDataAdmin(admin.ModelAdmin):
    list_display = ['id', 'page', 'key', 'value', 'type']
