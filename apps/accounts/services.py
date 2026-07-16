from django.contrib.auth.forms import PasswordResetForm
from django.core.cache import cache

# CLAUDE.md ch.12 "Brute Force Protection" — temporary lockout, backed by
# the Redis cache already configured for the project (CLAUDE.md ch.13),
# not a new dependency. Keyed on (IP, username) rather than IP alone or
# username alone: an attacker working through many passwords for one
# account from one machine gets locked out, without that lockout being
# usable to deny service to a real user from a *different* IP, or to
# every account behind a shared office IP.
LOGIN_ATTEMPT_LIMIT = 5
LOGIN_LOCKOUT_SECONDS = 15 * 60


def _login_attempts_cache_key(ip_address, username):
    return f'login-attempts:{ip_address}:{username.strip().lower()}'


def is_login_locked_out(ip_address, username):
    """True once `username` has failed to log in `LOGIN_ATTEMPT_LIMIT`
    times from `ip_address` within the current lockout window."""
    key = _login_attempts_cache_key(ip_address, username)
    return cache.get(key, 0) >= LOGIN_ATTEMPT_LIMIT


def register_login_failure(ip_address, username):
    """Increments the failure counter for this (IP, username) pair.

    `cache.add()` seeds the counter at 0 only if it isn't already
    present — atomic on the Redis backend, so two near-simultaneous
    failed attempts can't both "win" the initial set and silently drop
    one increment. The window is fixed from the *first* failure (not
    slid forward on every subsequent one) — simpler to reason about,
    and standard "N attempts per window" rate-limiting behaviour.
    """
    key = _login_attempts_cache_key(ip_address, username)
    cache.add(key, 0, LOGIN_LOCKOUT_SECONDS)
    cache.incr(key)


def clear_login_failures(ip_address, username):
    """Called on a successful login — a legitimate user who mistyped
    their password a few times shouldn't stay throttled afterwards."""
    cache.delete(_login_attempts_cache_key(ip_address, username))


def send_password_setup_email(request, user):
    """Emails `user` a Django password-reset link — reused both for a
    brand-new account's first password and an admin-triggered "Şifrəni
    sıfırla". Only ever sends a link, never a password (CLAUDE.md ch.12:
    "Never display passwords. Never email passwords.").

    `PasswordResetForm.get_users()` excludes any user whose password isn't
    "usable" (`has_usable_password()`), so the caller must have already
    set a real (if random and unknown) password on `user` — an
    `unusable_password()` account would silently receive nothing here.
    """
    form = PasswordResetForm({'email': user.email})
    if not form.is_valid():
        return False

    form.save(
        request=request,
        use_https=request.is_secure(),
        email_template_name='accounts/password_reset_email.html',
        subject_template_name='accounts/password_reset_subject.txt',
    )
    return True
