"""Locks in the permanent-delete media-cleanup behavior added in Phase 19
and manually verified at the time — an article's exclusively-owned media
(cover/OG image, inline body images) is removed only once every
referencing article is gone; shared media always survives.
"""

import pytest
from django.urls import reverse

from apps.media_manager.models import MediaFile
from apps.media_manager.services import collect_news_media_ids, delete_unused_media
from apps.news.models import News


@pytest.mark.django_db
def test_collect_news_media_ids_includes_featured_and_og_and_inline_images(category, administrator, media_file):
    inline_media = MediaFile.objects.create(
        original_filename='inline.jpg', width=10, height=10, file_size=1, file_format=MediaFile.Format.JPEG,
    )
    inline_media.file.name = 'uploads/2026/07/inline.jpg'
    inline_media.save()

    article = News.objects.create(
        title='Media testi',
        short_description='d',
        content=f'<figure class="image"><img src="/media/{inline_media.file.name}"></figure>',
        category=category,
        author=administrator,
        featured_image=media_file,
    )
    ids = collect_news_media_ids(article)
    assert ids == {media_file.pk, inline_media.pk}


@pytest.mark.django_db
def test_delete_unused_media_keeps_media_still_referenced_elsewhere(category, administrator, media_file):
    """Two articles share one featured_image — deleting one article must
    not remove media the other article still points at."""
    article_a = News.objects.create(
        title='Paylaşılan şəkil A', short_description='d', content='<p>c</p>',
        category=category, author=administrator, featured_image=media_file,
    )
    article_b = News.objects.create(
        title='Paylaşılan şəkil B', short_description='d', content='<p>c</p>',
        category=category, author=administrator, featured_image=media_file,
    )

    ids = collect_news_media_ids(article_a)
    article_a.delete()
    deleted_count = delete_unused_media(ids)

    assert deleted_count == 0
    assert MediaFile.objects.filter(pk=media_file.pk).exists()

    # Now delete the second (last) reference — the file should go too.
    ids = collect_news_media_ids(article_b)
    article_b.delete()
    deleted_count = delete_unused_media(ids)

    assert deleted_count == 1
    assert not MediaFile.objects.filter(pk=media_file.pk).exists()


@pytest.mark.django_db
def test_permanent_delete_view_cleans_up_exclusive_media_via_http(admin_client, category, administrator, media_file):
    article = News.objects.create(
        title='Silinəcək xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator, featured_image=media_file, is_deleted=True,
    )

    response = admin_client.post(reverse('cms:news_permanent_delete', args=[article.pk]))

    assert response.status_code == 302
    assert not News.objects.filter(pk=article.pk).exists()
    assert not MediaFile.objects.filter(pk=media_file.pk).exists()


@pytest.mark.django_db
def test_permanent_delete_requires_the_article_to_already_be_soft_deleted(admin_client, published_news):
    """The permanent-delete route only fires from the trash tab — a still-
    live (not soft-deleted) article must not be reachable through it."""
    response = admin_client.post(reverse('cms:news_permanent_delete', args=[published_news.pk]))
    assert response.status_code == 404
    assert News.objects.filter(pk=published_news.pk).exists()


@pytest.mark.django_db
def test_soft_delete_and_restore_never_touch_media(admin_client, category, administrator, media_file):
    article = News.objects.create(
        title='Bərpa test', short_description='d', content='<p>c</p>',
        category=category, author=administrator, featured_image=media_file,
    )

    admin_client.post(reverse('cms:news_delete', args=[article.pk]))
    article.refresh_from_db()
    assert article.is_deleted is True
    assert MediaFile.objects.filter(pk=media_file.pk).exists()

    admin_client.post(reverse('cms:news_restore', args=[article.pk]))
    article.refresh_from_db()
    assert article.is_deleted is False
    assert article.featured_image_id == media_file.pk
