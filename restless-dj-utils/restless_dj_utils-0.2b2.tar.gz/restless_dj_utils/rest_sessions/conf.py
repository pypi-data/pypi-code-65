"""
Define application default settings
"""
from django.conf import settings

INACTIVITY_TIMEOUT = getattr(settings, "REST_SESSIONS_INACTIVITY_TIMEOUT", 60 * 60 * 4)
TOKEN_MAX_AGE = getattr(settings, "REST_SESSIONS_TOKEN_MAX_AGE", 60 * 10)
ACCESS_BACKEND = getattr(
    settings, "REST_SESSIONS_ACCESS_BACKEND",
    'restless_dj_utils.rest_sessions.backends.CachedDBSessionAccessBackend')

API_SESSION_MANAGER = getattr(
    settings, "REST_API_SESSION_MANAGER",
    'restless_dj_utils.rest_sessions.manager.APISessionManager')
