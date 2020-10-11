# Copyright (C) 2007-2016, Raffaele Salmaso <raffaele@salmaso.org>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from fluo import admin
from fluo import forms
from posts.admin import PostModelAdmin
from .models import Faq, Topic, FaqTranslation


MAX_LANGUAGES = len(settings.LANGUAGES)


class TopicAdminForm(forms.ModelForm):
    pass
class TopicAdmin(admin.ModelAdmin):
    form = TopicAdminForm
admin.site.register(Topic, TopicAdmin)


class FaqTranslationInlineModelForm(forms.ModelForm):
    pass
class FaqTranslationInline(admin.StackedInline):
    model = FaqTranslation
    form = FaqTranslationInlineModelForm
    extra = MAX_LANGUAGES
    max_num = MAX_LANGUAGES
    fields = ('language', 'title', 'text',)
class FaqAdminForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        try:
            from tinymce.widgets import TinyMCE
            self.fields['text'].widget = TinyMCE()
        except ImportError:
            pass
class FaqAdmin(PostModelAdmin):
    form = FaqAdminForm
    list_display = ('__str__', 'status', 'event_date', 'pub_date_begin', 'pub_date_end', '_get_topics',)
    list_display_links = ('__str__',)
    list_per_page = 30
    ordering = ("ordering",)
    fieldsets = (
        (None, {"fields": (
            ('created_at', 'last_modified_at',),
            ('status', 'ordering',),
            'title',
            'event_date',
            ('pub_date_begin', 'pub_date_end',),
            'text',
            'note',
        ),}),
        (_('Show to'), {'fields': ('users',),}),
    )
    readonly_fields = ('created_at', 'last_modified_at',)
    filter_horizontal = ('users', 'topics',)
    inlines = (FaqTranslationInline,)

    def _get_topics(self, obj):
        topics = obj.topics.all().order_by('name')
        if topics:
            return u', '.join([topic.name for topic in topics])
        else:
            return _(u'All')
    _get_topics.short_description = _('Topics')
admin.site.register(Faq, FaqAdmin)
