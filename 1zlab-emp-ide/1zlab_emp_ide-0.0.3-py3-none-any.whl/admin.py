from django.contrib import admin

from emp_ide.models import Visitors, VisitCounts, MpyMachineIP


class AdminVisitCounts(admin.ModelAdmin):
    list_display = ["date", "amount_of_day"]


class AdminVisitors(admin.ModelAdmin):
    list_display = ["ip", "time", "url"]


class AdminMpyMachine(admin.ModelAdmin):
    list_display = ["ip", "machine_ip"]


admin.site.register(VisitCounts, AdminVisitCounts)
admin.site.register(Visitors, AdminVisitors)
admin.site.register(MpyMachineIP, AdminMpyMachine)
