"""Access-control smoke tests for every CMS list/overview screen.

Doesn't test each view's business logic (that's covered where the
underlying feature is tested — news/media/categories/...) — this only
guards the one thing every single CMS screen must get right
(CLAUDE.md ch.12 "Every CMS route requires authentication. Every action
checks permissions."): anonymous is bounced to login, and the handful of
Administrator-only screens actually reject a merely-logged-in staff
member instead of quietly allowing them in.
"""

import pytest
from django.urls import reverse

# (url_name, requires_administrator)
LOGIN_REQUIRED_LIST_VIEWS = [
    ('cms:dashboard', False),
    ('cms:activity_log', False),
    ('cms:news_list', False),
    ('cms:media_list', False),
    ('cms:category_list', False),
    ('cms:tag_list', False),
    ('cms:page_list', False),
    ('cms:ad_list', False),
    ('cms:seo_overview', False),
    ('cms:user_list', True),
    ('cms:settings_edit', True),
    ('cms:social_link_list', True),
]


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,requires_administrator', LOGIN_REQUIRED_LIST_VIEWS)
def test_anonymous_is_redirected_to_login(client, url_name, requires_administrator):
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert reverse('accounts:login') in response.url


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,requires_administrator', LOGIN_REQUIRED_LIST_VIEWS)
def test_logged_in_staff_access(journalist_client, url_name, requires_administrator):
    response = journalist_client.get(reverse(url_name))
    if requires_administrator:
        assert response.status_code == 403
    else:
        assert response.status_code == 200


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,requires_administrator', LOGIN_REQUIRED_LIST_VIEWS)
def test_administrator_can_access_everything(admin_client, url_name, requires_administrator):
    response = admin_client.get(reverse(url_name))
    assert response.status_code == 200
