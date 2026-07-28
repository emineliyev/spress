"""Two related additions to user management (apps/cms/views/user.py's
UserDeleteView, apps/cms/views/profile.py's ChangePasswordView):
Administrators can now permanently delete an (already deactivated) user,
and any logged-in CMS user can change their own password without an
admin's involvement or a working SMTP setup.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from apps.logs.models import ActivityLog
from apps.news.models import News

User = get_user_model()


@pytest.mark.django_db
def test_user_delete_requires_the_target_to_be_deactivated_first(admin_client, journalist):
    response = admin_client.post(reverse('cms:user_delete', args=[journalist.pk]))
    assert response.status_code == 404
    assert User.objects.filter(pk=journalist.pk).exists()


@pytest.mark.django_db
def test_user_delete_removes_a_deactivated_user_with_no_articles(admin_client, journalist):
    journalist.is_active = False
    journalist.save(update_fields=['is_active'])

    response = admin_client.post(reverse('cms:user_delete', args=[journalist.pk]))

    assert response.status_code == 302
    assert not User.objects.filter(pk=journalist.pk).exists()
    assert ActivityLog.objects.filter(action=ActivityLog.Action.USER_DELETED).exists()


@pytest.mark.django_db
def test_user_delete_blocked_when_user_authored_articles(admin_client, journalist, category):
    journalist.is_active = False
    journalist.save(update_fields=['is_active'])
    # News.author is on_delete=PROTECT — a naive .delete() would raise
    # ProtectedError instead of the friendly message this view shows.
    News.objects.create(
        title='Jurnalistin xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=journalist,
    )

    response = admin_client.post(reverse('cms:user_delete', args=[journalist.pk]))

    assert response.status_code == 302
    assert User.objects.filter(pk=journalist.pk).exists()


@pytest.mark.django_db
def test_user_cannot_delete_their_own_account(admin_client, administrator):
    administrator.is_active = False
    administrator.save(update_fields=['is_active'])

    response = admin_client.post(reverse('cms:user_delete', args=[administrator.pk]))

    assert response.status_code == 302
    assert User.objects.filter(pk=administrator.pk).exists()


@pytest.mark.django_db
def test_user_delete_requires_administrator(journalist_client, editor):
    editor.is_active = False
    editor.save(update_fields=['is_active'])

    response = journalist_client.post(reverse('cms:user_delete', args=[editor.pk]))

    assert response.status_code == 403
    assert User.objects.filter(pk=editor.pk).exists()


@pytest.mark.django_db
def test_change_password_requires_login(client):
    response = client.get(reverse('cms:change_password'))
    assert response.status_code == 302
    assert '/accounts/login' in response.url


@pytest.mark.django_db
def test_any_logged_in_user_can_change_their_own_password(journalist_client, journalist):
    response = journalist_client.post(reverse('cms:change_password'), {
        'old_password': 'test-pass-12345',
        'new_password1': 'a-brand-new-strong-pass-9',
        'new_password2': 'a-brand-new-strong-pass-9',
    })

    assert response.status_code == 302
    journalist.refresh_from_db()
    assert journalist.check_password('a-brand-new-strong-pass-9')
    assert ActivityLog.objects.filter(action=ActivityLog.Action.USER_PASSWORD_CHANGED).exists()


@pytest.mark.django_db
def test_change_password_rejects_a_wrong_current_password(journalist_client, journalist):
    response = journalist_client.post(reverse('cms:change_password'), {
        'old_password': 'completely-wrong',
        'new_password1': 'a-brand-new-strong-pass-9',
        'new_password2': 'a-brand-new-strong-pass-9',
    })

    assert response.status_code == 200  # form_invalid — re-renders, no redirect
    journalist.refresh_from_db()
    assert journalist.check_password('test-pass-12345')  # unchanged
