"""Access-control smoke tests for every CMS list/overview screen
(CLAUDE.md ch.12 "Every CMS route requires authentication. Every action
checks permissions.") — doesn't test each view's business logic (that's
covered where the underlying feature is tested), only the one thing
every CMS screen must get right: anonymous is bounced to login, and each
screen's actual role gate matches what CLAUDE.md ch.9 "User Roles"
describes for that role.
"""

import pytest
from django.urls import reverse

ALL_ROLES = {'administrator', 'editor_in_chief', 'editor', 'journalist', 'content_manager'}

# (url_name, {roles allowed to reach it})
LIST_VIEWS = [
    ('cms:dashboard', ALL_ROLES),
    ('cms:activity_log', ALL_ROLES),
    ('cms:media_list', ALL_ROLES),
    ('cms:contact_message_list', ALL_ROLES),
    ('cms:news_list', {'administrator', 'editor_in_chief', 'editor', 'journalist'}),
    ('cms:tag_list', {'administrator', 'editor_in_chief', 'editor', 'content_manager'}),
    ('cms:page_list', {'administrator', 'editor_in_chief', 'editor', 'content_manager'}),
    ('cms:seo_overview', {'administrator', 'editor_in_chief', 'editor', 'content_manager'}),
    ('cms:category_list', {'administrator', 'editor_in_chief', 'content_manager'}),
    ('cms:ad_list', {'administrator', 'editor_in_chief', 'content_manager'}),
    ('cms:user_list', {'administrator'}),
    ('cms:settings_edit', {'administrator'}),
    ('cms:social_link_list', {'administrator'}),
]


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,allowed_roles', LIST_VIEWS)
def test_anonymous_is_redirected_to_login(client, url_name, allowed_roles):
    response = client.get(reverse(url_name))
    assert response.status_code == 302
    assert reverse('accounts:login') in response.url


@pytest.mark.django_db
@pytest.mark.parametrize('url_name,allowed_roles', LIST_VIEWS)
@pytest.mark.parametrize('role', sorted(ALL_ROLES))
def test_role_access_matches_permission_matrix(
    client, role, url_name, allowed_roles,
    administrator, editor_in_chief, editor, journalist, content_manager,
):
    user_by_role = {
        'administrator': administrator,
        'editor_in_chief': editor_in_chief,
        'editor': editor,
        'journalist': journalist,
        'content_manager': content_manager,
    }
    client.force_login(user_by_role[role])

    response = client.get(reverse(url_name))

    if role in allowed_roles:
        assert response.status_code == 200
    else:
        assert response.status_code == 403
