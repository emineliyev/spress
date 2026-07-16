from .base import *  # noqa: F401,F403
from .base import env

DEBUG = env.bool('DJANGO_DEBUG', default=True)

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS', default=['localhost', '127.0.0.1'])

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# No local Redis broker yet (CLAUDE.md ch.13 background tasks — see
# docs/ARCHITECTURE.md "Known gap"). Tasks run inline instead of failing
# to connect, matching Celery's own recommended development pattern.
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
