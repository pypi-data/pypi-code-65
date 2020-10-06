from django.contrib import admin

from lzlab_blogs.models import Author


class AuthorFilter(admin.SimpleListFilter):
    title = '作者'

    # Parameter for the filter that will be used in the URL query.
    parameter_name = 'author'

    def lookups(self, request, model_admin):
        authors = [(author.id, author.alias) for author in Author.objects.all()]

        return authors

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        if self.value():
            return queryset.filter(author__id=self.value()).order_by('update_time', 'abbreviation')
        return queryset.order_by('update_time', 'abbreviation')
