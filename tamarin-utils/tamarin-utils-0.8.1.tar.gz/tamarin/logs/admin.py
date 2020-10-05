from django.contrib import admin
from .models import Log


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    using = 'log'

    def get_queryset(self, request):
        return super(LogAdmin, self).get_queryset(request).using(self.using)
