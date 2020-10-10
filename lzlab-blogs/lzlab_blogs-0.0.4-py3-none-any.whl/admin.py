from django.contrib import admin

from lzlab_blogs.filter.author_filter import AuthorFilter
from lzlab_blogs.models import Author, Article, Topic, Set


class BaseAdmin(admin.ModelAdmin):
    ordering = ['update_time', 'abbreviation']
    date_hierarchy = 'update_time'
    search_fields = ['id', 'abbreviation', 'pinyin', 'create_time']
    list_per_page = 20


class AuthorAdmin(BaseAdmin):
    list_display = ["alias", "moto", "wechat_id"]
    autocomplete_fields = ["user"]
    search_fields = BaseAdmin.search_fields + ['alias']


class ArticleAdmin(BaseAdmin):
    list_filter = [AuthorFilter]
    list_display = ["title", "作者", "主题", "文集", "update_time", "create_time", "public"]
    search_fields = BaseAdmin.search_fields + ['title']
    list_editable = ["public"]
    autocomplete_fields = ["author", "topic", "set"]


class TopicAdmin(BaseAdmin):
    list_filter = [AuthorFilter]
    list_display = ["title", "作者", "update_time", "create_time", "public"]
    search_fields = BaseAdmin.search_fields + ['title']
    list_editable = ["public"]
    autocomplete_fields = ["author"]


class SetAdmin(BaseAdmin):
    list_filter = [AuthorFilter]
    list_display = ["title", "作者", "主题", "update_time", "create_time"]
    search_fields = BaseAdmin.search_fields + ['title']
    autocomplete_fields = ["author", "topic"]


admin.site.register(Author, AuthorAdmin)
admin.site.register(Article, ArticleAdmin)
admin.site.register(Topic, TopicAdmin)
admin.site.register(Set, SetAdmin)
