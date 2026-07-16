"""One happy-path create/edit/delete per CMS-managed model — confirms
the object round-trips through its real CMS form/view and that
`ActivityLog` records the action, not the deeper business rules already
covered elsewhere (news lifecycle, media cleanup, category hierarchy, ...).
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.advertisements.models import AdPosition, Advertisement
from apps.categories.models import Category
from apps.logs.models import ActivityLog
from apps.news.models import News
from apps.pages.models import Page
from apps.settings_app.models import SocialLink
from apps.tags.models import Tag


@pytest.mark.django_db
def test_news_create_edit_delete(admin_client, category):
    create_response = admin_client.post(reverse('cms:news_create'), {
        'title': 'CRUD test xəbəri', 'short_description': 'd', 'content': '<p>c</p>',
        'category': category.pk, 'status': News.Status.DRAFT,
    })
    assert create_response.status_code == 302
    article = News.objects.get(title='CRUD test xəbəri')
    assert ActivityLog.objects.filter(action=ActivityLog.Action.ARTICLE_CREATED).exists()

    edit_response = admin_client.post(reverse('cms:news_edit', args=[article.pk]), {
        'title': 'Redaktə edilmiş başlıq', 'short_description': 'd', 'content': '<p>c</p>',
        'category': category.pk, 'status': News.Status.DRAFT,
    })
    assert edit_response.status_code == 302
    article.refresh_from_db()
    assert article.title == 'Redaktə edilmiş başlıq'
    assert ActivityLog.objects.filter(action=ActivityLog.Action.ARTICLE_UPDATED).exists()

    delete_response = admin_client.post(reverse('cms:news_delete', args=[article.pk]))
    assert delete_response.status_code == 302
    article.refresh_from_db()
    assert article.is_deleted is True
    assert ActivityLog.objects.filter(action=ActivityLog.Action.ARTICLE_DELETED).exists()


@pytest.mark.django_db
def test_category_create_edit_delete(admin_client):
    create_response = admin_client.post(reverse('cms:category_create'), {'name': 'Yeni kateqoriya', 'is_active': True})
    assert create_response.status_code == 302
    cat = Category.objects.get(name='Yeni kateqoriya')
    assert ActivityLog.objects.filter(action=ActivityLog.Action.CATEGORY_CREATED).exists()

    edit_response = admin_client.post(reverse('cms:category_edit', args=[cat.pk]), {'name': 'Dəyişdirilmiş ad', 'is_active': True})
    assert edit_response.status_code == 302
    cat.refresh_from_db()
    assert cat.name == 'Dəyişdirilmiş ad'

    delete_response = admin_client.post(reverse('cms:category_delete', args=[cat.pk]))
    assert delete_response.status_code == 302
    cat.refresh_from_db()
    assert cat.is_deleted is True


@pytest.mark.django_db
def test_tag_create_edit_delete(admin_client):
    create_response = admin_client.post(reverse('cms:tag_create'), {'name': 'Yeni etiket'})
    assert create_response.status_code == 302
    tag = Tag.objects.get(name='Yeni etiket')
    assert ActivityLog.objects.filter(action=ActivityLog.Action.TAG_CREATED).exists()

    edit_response = admin_client.post(reverse('cms:tag_edit', args=[tag.pk]), {'name': 'Dəyişdirilmiş etiket'})
    assert edit_response.status_code == 302
    tag.refresh_from_db()
    assert tag.name == 'Dəyişdirilmiş etiket'

    delete_response = admin_client.post(reverse('cms:tag_delete', args=[tag.pk]))
    assert delete_response.status_code == 302
    assert not Tag.objects.filter(pk=tag.pk).exists()


@pytest.mark.django_db
def test_page_create_edit_delete(admin_client):
    create_response = admin_client.post(reverse('cms:page_create'), {
        'title': 'Yeni səhifə', 'content': '<p>c</p>', 'is_published': True,
    })
    assert create_response.status_code == 302
    page = Page.objects.get(title='Yeni səhifə')
    assert ActivityLog.objects.filter(action=ActivityLog.Action.PAGE_CREATED).exists()

    edit_response = admin_client.post(reverse('cms:page_edit', args=[page.pk]), {
        'title': 'Dəyişdirilmiş səhifə', 'content': '<p>c</p>', 'is_published': True,
    })
    assert edit_response.status_code == 302
    page.refresh_from_db()
    assert page.title == 'Dəyişdirilmiş səhifə'

    delete_response = admin_client.post(reverse('cms:page_delete', args=[page.pk]))
    assert delete_response.status_code == 302
    assert not Page.objects.filter(pk=page.pk).exists()


@pytest.mark.django_db
def test_advertisement_create_edit_delete(admin_client, media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)

    create_response = admin_client.post(reverse('cms:ad_create'), {
        'title': 'Yeni reklam', 'position': position.pk, 'banner': media_file.pk,
        'target_url': 'https://example.com', 'price': '0', 'start_date': '2026-01-01T00:00',
    })
    assert create_response.status_code == 302
    ad = Advertisement.objects.get(title='Yeni reklam')
    assert ActivityLog.objects.filter(action=ActivityLog.Action.AD_CREATED).exists()

    edit_response = admin_client.post(reverse('cms:ad_edit', args=[ad.pk]), {
        'title': 'Dəyişdirilmiş reklam', 'position': position.pk, 'banner': media_file.pk,
        'target_url': 'https://example.com', 'price': '0', 'start_date': '2026-01-01T00:00',
    })
    assert edit_response.status_code == 302
    ad.refresh_from_db()
    assert ad.title == 'Dəyişdirilmiş reklam'

    delete_response = admin_client.post(reverse('cms:ad_delete', args=[ad.pk]))
    assert delete_response.status_code == 302
    ad.refresh_from_db()
    assert ad.is_deleted is True


@pytest.mark.django_db
def test_social_link_create_edit_delete(admin_client):
    create_response = admin_client.post(reverse('cms:social_link_create'), {
        'platform': SocialLink.Platform.FACEBOOK, 'url': 'https://facebook.com/spress', 'order': 0,
    })
    assert create_response.status_code == 302
    link = SocialLink.objects.get(platform=SocialLink.Platform.FACEBOOK)
    assert ActivityLog.objects.filter(action=ActivityLog.Action.SOCIAL_LINK_CREATED).exists()

    edit_response = admin_client.post(reverse('cms:social_link_edit', args=[link.pk]), {
        'platform': SocialLink.Platform.INSTAGRAM, 'url': 'https://instagram.com/spress', 'order': 1,
    })
    assert edit_response.status_code == 302
    link.refresh_from_db()
    assert link.platform == SocialLink.Platform.INSTAGRAM

    delete_response = admin_client.post(reverse('cms:social_link_delete', args=[link.pk]))
    assert delete_response.status_code == 302
    assert not SocialLink.objects.filter(pk=link.pk).exists()


@pytest.mark.django_db
def test_journalist_cannot_manage_social_links(journalist_client):
    response = journalist_client.post(reverse('cms:social_link_create'), {
        'platform': SocialLink.Platform.FACEBOOK, 'url': 'https://facebook.com/spress', 'order': 0,
    })
    assert response.status_code == 403
