from django.contrib import admin, messages
from django.utils.translation import ngettext
from outbreak_tracker.models import Disease, TrackerLog, Demographics, FAQSection, FAQDetail


admin.site.site_header = 'Caribbean Virus Tracker Administration Portal'
admin.site.site_title = 'Admin Portal'
admin.site.index_title = 'Caribbean Virus Tracker'

@admin.register(Disease)
class DiseaseAdmin(admin.ModelAdmin):
    list_display = ('code_name','name', 'start_date', 'end_date',)
    list_filter = ('start_date', 'end_date')
    fieldsets = (
        ('General', {
            'fields':('code_name','name', 'description','reference_url',)
        }),
        ('Pandemic Period', {
            'fields':('start_date','end_date')
        }),
        ('Read Only', {
            'classes':('collapse',),
            'fields':('created', 'last_updated')
        }),
    )
    readonly_fields = ('created', 'last_updated',)


@admin.register(TrackerLog)
class TrackerLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'country', 'is_published' , 'total_cases', 'total_deaths', 'recovered')
    list_filter = ('date','is_published')
    ordering = ('-date','country','is_published')
    fieldsets = (
        ('General', {
            'fields':('disease', 'country',)
        }),
        ('Case Stats', {
            'fields':('date', ('total_cases', 'total_deaths', 'recovered',), ('source_name', 'source_url',),)
        }),
        ('Read Only', {
            'classes':('collapse',),
            'fields':(('is_published', 'created', 'last_updated',),)
        }),
    )
    readonly_fields = ('is_published','created', 'last_updated',)
    actions = ['make_published']

    def make_published(self, request, queryset):
        queryset.update(is_published=True)
        self.message_user(request, ngettext(
            '%d country logs was successfully marked as published.',
            '%d countries logs were successfully marked as published.',
            queryset.count()
        ) % queryset.count(), messages.SUCCESS)
    make_published.short_description = 'Publish Tracker Logs'


@admin.register(Demographics)
class DemographicsAdmin(admin.ModelAdmin):
    list_display = ('country', 'latitude', 'longitude', 'parent_country', 'last_updated')
    ordering = ('country',)
    list_filter = ('parent_country',)


class FAQDetailInline(admin.StackedInline):
    model = FAQDetail
    fields = ('question', 'answer', 'priority')
    extra = 1


@admin.register(FAQSection)
class FAQSectionAdmin(admin.ModelAdmin):
    list_display = ('title', 'disease', 'priority')
    list_filter = ('disease',)
    ordering = ('priority',)
    inlines = [FAQDetailInline,]

