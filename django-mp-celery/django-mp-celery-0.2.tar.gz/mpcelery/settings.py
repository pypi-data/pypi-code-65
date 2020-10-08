

class CelerySettings(object):

    CELERY_BROKER_URL = "redis://0.0.0.0:6379/0"

    @property
    def INSTALLED_APPS(self):
        return super().INSTALLED_APPS + ['django_celery_beat']
