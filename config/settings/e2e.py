"""
Settings for the Playwright end-to-end suite (e2e/).

A real `runserver` process under this settings module is what
`e2e/playwright.config.js`'s `webServer` starts — unlike pytest's
per-test-run throwaway `test_<dbname>`, that means a normal long-lived
database this process keeps writing real rows into (created articles,
soft-deletes, ...). It must be a completely separate database from the
one used for local development, never the developer's real `news_db` —
that database now holds genuine editorial content (see
docs/ARCHITECTURE.md Phase 19), and an unattended e2e run creating,
soft-deleting and permanently deleting articles against it would be
exactly the kind of destructive, un-confirmed action this project's own
operating principles rule out.

`apps/core/management/commands/bootstrap_e2e_db.py` creates this
database (if missing) and seeds it fresh before every e2e run.
"""

from .development import *  # noqa: F401,F403

DATABASES['default'] = env.db(  # noqa: F405
    'E2E_DATABASE_URL',
    default='postgres://news_user:news_local_dev_pw@127.0.0.1:5432/news_db_e2e',
)
DATABASES['default']['ATOMIC_REQUESTS'] = True

MEDIA_ROOT = BASE_DIR / 'test_media_e2e'  # noqa: F405

# A separate Redis logical DB (not development's /1) — login-lockout
# counters and cache-backed sessions must not bleed into (or get wiped
# by) whatever the developer's own dev server is doing at the same time.
REDIS_URL = env('E2E_REDIS_URL', default='redis://127.0.0.1:6379/3')  # noqa: F405
CACHES['default']['LOCATION'] = REDIS_URL  # noqa: F405

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]
