from django.apps import AppConfig

class GroupAssignConfig(AppConfig):
    name = 'groupassign'
    label = 'groupassign'

    def ready(self):
        import groupassign.signals
