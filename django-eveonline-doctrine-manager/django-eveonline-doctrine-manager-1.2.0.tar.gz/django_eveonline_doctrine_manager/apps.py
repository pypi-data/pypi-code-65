from django.apps import AppConfig
from django.conf import settings

class DjangoEveOnlineDoctrineManagerConfig(AppConfig):
    name = 'django_eveonline_doctrine_manager'
    verbose_name = "EVE Doctrine Manager"
    url_slug = 'eveonline'
    install_requires = ['crispy_forms', 'django_eveonline_connector']

    def ready(self):
        for requirement in self.install_requires:
            if requirement not in settings.INSTALLED_APPS:
                raise Exception(f"Missing '{requirement}' in INSTALLED_APPS")
        