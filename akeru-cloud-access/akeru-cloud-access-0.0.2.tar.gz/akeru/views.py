from akeru.models import AccessRole
from akeru.libs.console import generate_session
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView
from django.views.generic.list import ListView
from itertools import chain


class IndexView(TemplateView):
    template_name = 'akeru/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = 'home'
        return context


class AccessView(LoginRequiredMixin, ListView):
    template_name = 'akeru/access.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['location'] = 'access'
        return context

    def get_queryset(self):
        direct_roles = AccessRole.objects.filter(user=self.request.user)
        user_groups = self.request.user.groups.all()
        group_roles = AccessRole.objects.filter(group__in=user_groups)
        return list(chain(direct_roles, group_roles))


class AWSConsoleView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        if kwargs['type'] in ['user', 'role']:
            user_type = True if kwargs['type'] == 'user' else False
            return generate_session(
                self.request.user, user_type, kwargs['entity_name']
            )

        raise PermissionDenied
