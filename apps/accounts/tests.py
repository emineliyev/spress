import pytest
from django.urls import reverse

from apps.accounts.services import LOGIN_ATTEMPT_LIMIT
from apps.logs.models import ActivityLog


@pytest.mark.django_db
def test_login_succeeds_with_correct_credentials(client, administrator):
    response = client.post(reverse('accounts:login'), {'username': 'administrator', 'password': 'test-pass-12345'})
    assert response.status_code == 302
    assert ActivityLog.objects.filter(action=ActivityLog.Action.LOGIN_SUCCESS, actor=administrator).exists()


@pytest.mark.django_db
def test_login_fails_with_wrong_password(client, administrator):
    response = client.post(reverse('accounts:login'), {'username': 'administrator', 'password': 'wrong-password'})
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert ActivityLog.objects.filter(action=ActivityLog.Action.LOGIN_FAILED).exists()


@pytest.mark.django_db
def test_login_locks_out_after_repeated_failures(client, administrator):
    for _ in range(LOGIN_ATTEMPT_LIMIT):
        client.post(reverse('accounts:login'), {'username': 'administrator', 'password': 'wrong-password'})

    # The next attempt, even with the *correct* password, must be blocked
    # before Django's own auth backend ever checks it (CLAUDE.md ch.12
    # "Brute Force Protection").
    response = client.post(reverse('accounts:login'), {'username': 'administrator', 'password': 'test-pass-12345'})
    assert response.status_code == 200
    assert not response.wsgi_request.user.is_authenticated
    assert ActivityLog.objects.filter(action=ActivityLog.Action.LOGIN_BLOCKED).exists()


@pytest.mark.django_db
def test_successful_login_clears_previous_failures(client, administrator):
    for _ in range(LOGIN_ATTEMPT_LIMIT - 1):
        client.post(reverse('accounts:login'), {'username': 'administrator', 'password': 'wrong-password'})

    response = client.post(reverse('accounts:login'), {'username': 'administrator', 'password': 'test-pass-12345'})
    assert response.status_code == 302

    # A fresh round of failures afterward should need the full limit again,
    # not be blocked immediately by leftover attempts from before login.
    client.logout()
    for _ in range(LOGIN_ATTEMPT_LIMIT - 1):
        response = client.post(reverse('accounts:login'), {'username': 'administrator', 'password': 'wrong-password'})
    assert not ActivityLog.objects.filter(action=ActivityLog.Action.LOGIN_BLOCKED).exists()


@pytest.mark.django_db
def test_logout_logs_activity(admin_client, administrator):
    response = admin_client.post(reverse('accounts:logout'))
    assert response.status_code == 302
    assert ActivityLog.objects.filter(action=ActivityLog.Action.LOGOUT, actor=administrator).exists()
