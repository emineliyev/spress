from .base import *  # noqa: F401,F403
from .base import env

DEBUG = False

ALLOWED_HOSTS = env.list('DJANGO_ALLOWED_HOSTS')

# ---------------------------------------------------------------------------
# Security hardening (CLAUDE.md ch.12 — HTTPS, secure cookies, HSTS)
# ---------------------------------------------------------------------------

# Required behind Nginx (deploy/nginx.conf sets X-Forwarded-Proto) — Gunicorn
# only ever receives plain HTTP from Nginx, so without this Django can never
# tell a request arrived over HTTPS. That breaks three things at once: an
# infinite redirect loop with SECURE_SSL_REDIRECT below (Django thinks every
# request is insecure and keeps redirecting to HTTPS, which Nginx again
# forwards as HTTP), CSRF validation (compares the Referer's scheme against
# request.is_secure()), and request.scheme in templates (canonical URLs, Open
# Graph, sitemap, structured data all render "http://" instead of "https://").
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

SECURE_SSL_REDIRECT = env.bool('DJANGO_SECURE_SSL_REDIRECT', default=True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int('DJANGO_SECURE_HSTS_SECONDS', default=31536000)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_REFERRER_POLICY = 'same-origin'

# ---------------------------------------------------------------------------
# Email (CLAUDE.md ch.9 CMS Settings — SMTP)
# ---------------------------------------------------------------------------

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST', default='')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default=EMAIL_HOST_USER)
