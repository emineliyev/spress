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

# Only set in production — Django's own CSRF failure page includes a
# helpful DEBUG-mode explanation locally that a custom view would hide.
CSRF_FAILURE_VIEW = 'apps.core.views.csrf_failure'

# ---------------------------------------------------------------------------
# Static files (CLAUDE.md ch.13 "Static Assets" — "Use cache versioning
# for updates")
# ---------------------------------------------------------------------------

# deploy/nginx.conf caches /static/ for 30 days with no revalidation — a
# CSS/JS edit that reused the same filename (every deploy, since none of
# them are hashed) meant every visitor's browser kept serving the old
# cached copy for up to 30 days after the fix actually shipped (found
# after a rich-text.css fix "didn't work" — it had, the browser just
# never re-fetched it). ManifestStaticFilesStorage appends a content
# hash to every static filename during collectstatic (deploy.sh already
# runs this every deploy) and rewrites every {% static %} reference to
# match, so an unchanged file keeps the same URL (still cached, no
# wasted re-downloads) while a changed one gets a new URL the 30-day
# cache can't possibly have — no nginx change needed, it just serves
# whatever filenames exist on disk.
STORAGES = {
    # STORAGES is a full replacement, not a merge with Django's own
    # defaults — 'default' (MediaFile uploads) must be restated
    # explicitly here or every file upload would break, not just
    # static files.
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}

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
