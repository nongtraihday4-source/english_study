"""Development settings — DEBUG on, SQLite fallback optional."""
from .base import *  # noqa: F401, F403

DEBUG = True

# In development, also allow Django's built-in JSONRenderer for browsable API
REST_FRAMEWORK["DEFAULT_RENDERER_CLASSES"] = [  # noqa: F405
    "utils.renderers.VNNumberJSONRenderer",
    "rest_framework.renderers.BrowsableAPIRenderer",
]

# Relax throttling for development
REST_FRAMEWORK["DEFAULT_THROTTLE_RATES"] = {  # noqa: F405
    "anon": "1000/min",
    "user": "10000/min",
    "login": "100/min",
    "submission": "200/min",
    "ai_grading": "100/min",
}

# Allow all origins in dev
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Use in-memory cache in development (no Redis required)
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_CACHE_ALIAS = "default"

# Celery: run tasks synchronously in dev (no Redis/broker needed)
# Tasks execute inline; exceptions caught by view-level try/except.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = False  # don't re-raise task exceptions at call site

# Short timeouts in case ALWAYS_EAGER is disabled
CELERY_BROKER_TRANSPORT_OPTIONS = {
    "socket_timeout": 2,
    "socket_connect_timeout": 2,
}
CELERY_BROKER_CONNECTION_MAX_RETRIES = 1
