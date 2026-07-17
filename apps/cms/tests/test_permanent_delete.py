"""Category and Advertisement permanent-delete — mirrors the News
scenario already covered in apps/news/tests/test_media_cleanup.py:
soft-delete/restore never touches anything permanently, and permanent
delete is only reachable once something is actually in the trash.
"""

import pytest
from django.urls import reverse

from apps.advertisements.models import AdPosition, Advertisement
from apps.categories.models import Category
from apps.logs.models import ActivityLog
from apps.media_manager.models import MediaFile
from apps.news.models import News


@pytest.mark.django_db
def test_permanent_delete_removes_an_empty_category(admin_client):
    category = Category.objects.create(name='Boş kateqoriya', is_deleted=True)

    response = admin_client.post(reverse('cms:category_permanent_delete', args=[category.pk]))

    assert response.status_code == 302
    assert not Category.objects.filter(pk=category.pk).exists()
    assert ActivityLog.objects.filter(action=ActivityLog.Action.CATEGORY_PURGED).exists()


@pytest.mark.django_db
def test_permanent_delete_blocked_when_news_still_references_category(admin_client, administrator):
    category = Category.objects.create(name='Bağlı kateqoriya', is_deleted=True)
    # Even a soft-deleted News row still holds the FK — News.category is
    # on_delete=PROTECT, so a naive .delete() would raise ProtectedError.
    News.objects.create(
        title='Bağlı xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator, is_deleted=True,
    )

    response = admin_client.post(reverse('cms:category_permanent_delete', args=[category.pk]))

    assert response.status_code == 302
    assert Category.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_permanent_delete_blocked_when_children_exist(admin_client):
    parent = Category.objects.create(name='Ana kateqoriya', is_deleted=True)
    Category.objects.create(name='Alt kateqoriya', parent=parent, is_deleted=True)

    response = admin_client.post(reverse('cms:category_permanent_delete', args=[parent.pk]))

    assert response.status_code == 302
    assert Category.objects.filter(pk=parent.pk).exists()


@pytest.mark.django_db
def test_permanent_delete_requires_category_to_be_in_trash(admin_client, category):
    response = admin_client.post(reverse('cms:category_permanent_delete', args=[category.pk]))
    assert response.status_code == 404
    assert Category.objects.filter(pk=category.pk).exists()


@pytest.mark.django_db
def test_ad_permanent_delete_cleans_up_exclusive_banner(admin_client, media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    ad = Advertisement.objects.create(
        title='Silinəcək kampaniya', position=position, banner=media_file,
        target_url='https://example.com', is_deleted=True,
    )

    response = admin_client.post(reverse('cms:ad_permanent_delete', args=[ad.pk]))

    assert response.status_code == 302
    assert not Advertisement.objects.filter(pk=ad.pk).exists()
    assert not MediaFile.objects.filter(pk=media_file.pk).exists()
    assert ActivityLog.objects.filter(action=ActivityLog.Action.AD_PURGED).exists()


@pytest.mark.django_db
def test_ad_permanent_delete_keeps_banner_shared_with_another_campaign(admin_client, media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    ad_a = Advertisement.objects.create(
        title='Kampaniya A', position=position, banner=media_file,
        target_url='https://example.com', is_deleted=True,
    )
    Advertisement.objects.create(
        title='Kampaniya B', position=position, banner=media_file, target_url='https://example.com',
    )

    admin_client.post(reverse('cms:ad_permanent_delete', args=[ad_a.pk]))

    assert MediaFile.objects.filter(pk=media_file.pk).exists()


@pytest.mark.django_db
def test_ad_permanent_delete_requires_ad_to_be_in_trash(admin_client, media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    ad = Advertisement.objects.create(
        title='Aktiv kampaniya', position=position, banner=media_file, target_url='https://example.com',
    )
    response = admin_client.post(reverse('cms:ad_permanent_delete', args=[ad.pk]))
    assert response.status_code == 404
    assert Advertisement.objects.filter(pk=ad.pk).exists()
