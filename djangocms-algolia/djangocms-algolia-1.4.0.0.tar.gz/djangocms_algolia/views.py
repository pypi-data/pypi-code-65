from django.views.generic import TemplateView


class AlgoliaSearchView(TemplateView):
    template_name = 'djangocms_algolia/search.html'
