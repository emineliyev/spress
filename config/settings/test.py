"""
Settings for the automated test suite (pytest --ds=config.settings.test).

Inherits development.py rather than duplicating it — same database,
cache and Celery-eager behavior as local dev, just with a faster
password hasher so auth-heavy tests (login, lockout) aren't needlessly
slow (CLAUDE.md ch.15 "avoid premature optimization" cuts both ways:
this one is measured, not speculative — MD5 is single digit ms vs
PBKDF2's ~100ms per hash, and every fixture that logs a user in pays
that cost once per test).
"""

from .development import *  # noqa: F401,F403

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Tests that attach real files to a MediaFile (conftest.py's `media_file`
# fixture, media_manager upload-pipeline tests, ...) must never write into
# the real project media/ folder — that's dev content, and this project
# was just cleaned of every leftover test file once already by hand.
MEDIA_ROOT = BASE_DIR / 'test_media'
