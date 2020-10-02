from django.db.models import Max, Count

from restless_dj_utils.rest_sessions.models import APISession

try:
    from celery import shared_task
except ImportError:
    shared_task = None


def _cleanup_active_sessions():
    """Cleanup session access database"""

    api_sessions = APISession.objects.filter(is_active=True)

    for api_session in api_sessions.iterator():
        if APISession.objects.has_expired(api_session):
            api_session.is_active = False
            api_session.save(update_fields=['is_active'])


def _cleanup_expired_session_access_database():
    """Cleanup session access database"""

    api_sessions = APISession.objects \
        .filter(is_active=False) \
        .annotate(access_count=Count('accesses')) \
        .filter(access_count__gte=2) \
        .annotate(access_latest=Max('accesses__created'))

    for api_session in api_sessions.iterator():
        api_session.accesses.filter(created__lt=api_session.access_latest).delete()


if shared_task is not None:
    @shared_task()
    def cleanup_sessions():
        """Cleanup sessions celery task"""
        _cleanup_active_sessions()
        _cleanup_expired_session_access_database()
