"""Phase 24 — optional per-video YouTube cover images
(apps.news.models.NewsVideoCover, apps.news.services.sync_video_covers).
"""

import json

import pytest
from django.urls import reverse

from apps.media_manager.models import MediaFile
from apps.media_manager.services import collect_news_media_ids, delete_unused_media
from apps.news.models import News, NewsVideoCover
from apps.news.services import sync_video_covers


def _make_media(sample_image_bytes, name):
    from django.core.files.base import ContentFile

    media = MediaFile(
        original_filename=name, width=800, height=600,
        file_size=len(sample_image_bytes()), file_format=MediaFile.Format.JPEG,
    )
    media.file.save(name, ContentFile(sample_image_bytes()), save=False)
    media.save()
    return media


@pytest.mark.django_db
def test_sync_video_covers_creates_rows_from_payload(category, administrator, media_file):
    article = News.objects.create(
        title='Video xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )
    payload = json.dumps([{'video_id': 'abc123', 'cover_media_id': media_file.pk}])

    sync_video_covers(article, payload)

    cover = NewsVideoCover.objects.get(news=article)
    assert cover.video_id == 'abc123'
    assert cover.cover_image_id == media_file.pk


@pytest.mark.django_db
def test_sync_video_covers_replaces_previous_set(category, administrator, media_file, sample_image_bytes):
    other_media = _make_media(sample_image_bytes, 'other.jpg')
    article = News.objects.create(
        title='Video xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )

    sync_video_covers(article, json.dumps([
        {'video_id': 'first', 'cover_media_id': media_file.pk},
        {'video_id': 'second', 'cover_media_id': other_media.pk},
    ]))
    assert NewsVideoCover.objects.filter(news=article).count() == 2

    sync_video_covers(article, json.dumps([{'video_id': 'second', 'cover_media_id': other_media.pk}]))

    remaining = list(NewsVideoCover.objects.filter(news=article))
    assert len(remaining) == 1
    assert remaining[0].video_id == 'second'


@pytest.mark.django_db
def test_sync_video_covers_ignores_malformed_entries(category, administrator, media_file):
    article = News.objects.create(
        title='Video xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )
    payload = json.dumps([
        {'video_id': '', 'cover_media_id': media_file.pk},
        {'video_id': 'no-media'},
        {'video_id': 'bad-media', 'cover_media_id': 999999},
        {'video_id': 'dup', 'cover_media_id': media_file.pk},
        {'video_id': 'dup', 'cover_media_id': media_file.pk},
        'not-a-dict',
    ])

    sync_video_covers(article, payload)

    assert list(NewsVideoCover.objects.filter(news=article).values_list('video_id', flat=True)) == ['dup']


@pytest.mark.django_db
def test_sync_video_covers_handles_empty_or_invalid_payload(category, administrator):
    article = News.objects.create(
        title='Video xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )
    sync_video_covers(article, '')
    sync_video_covers(article, 'not json')
    assert NewsVideoCover.objects.filter(news=article).count() == 0


@pytest.mark.django_db
def test_collect_news_media_ids_includes_video_cover_images(category, administrator, media_file):
    article = News.objects.create(
        title='Video xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
    )
    NewsVideoCover.objects.create(news=article, video_id='abc123', cover_image=media_file)

    ids = collect_news_media_ids(article)

    assert media_file.pk in ids


@pytest.mark.django_db
def test_permanent_delete_cleans_up_exclusive_video_cover_via_http(admin_client, category, administrator, media_file):
    article = News.objects.create(
        title='Silinəcək video xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=administrator, is_deleted=True,
    )
    NewsVideoCover.objects.create(news=article, video_id='abc123', cover_image=media_file)

    response = admin_client.post(reverse('cms:news_permanent_delete', args=[article.pk]))

    assert response.status_code == 302
    assert not News.objects.filter(pk=article.pk).exists()
    assert not MediaFile.objects.filter(pk=media_file.pk).exists()


@pytest.mark.django_db
def test_video_cover_survives_if_image_still_used_elsewhere(category, administrator, media_file):
    """A cover image also used as another article's featured_image must
    not be deleted just because the video-cover article is purged."""
    article = News.objects.create(
        title='Video xəbəri', short_description='d', content='<p>c</p>',
        category=category, author=administrator, is_deleted=True,
    )
    NewsVideoCover.objects.create(news=article, video_id='abc123', cover_image=media_file)
    News.objects.create(
        title='Başqa xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator, featured_image=media_file,
    )

    ids = collect_news_media_ids(article)
    article.delete()
    deleted_count = delete_unused_media(ids)

    assert deleted_count == 0
    assert MediaFile.objects.filter(pk=media_file.pk).exists()


@pytest.mark.django_db
def test_news_create_view_persists_video_covers_from_form_submission(admin_client, category, media_file):
    payload = json.dumps([{'video_id': 'xyz789', 'cover_media_id': media_file.pk}])
    response = admin_client.post(reverse('cms:news_create'), {
        'title': 'Yeni video xəbəri',
        'short_description': 'Qısa təsvir',
        'content': '<div class="media-embed media-embed--youtube">'
                    '<iframe src="https://www.youtube-nocookie.com/embed/xyz789"></iframe></div>',
        'category': category.pk,
        'status': News.Status.DRAFT,
        'video_covers_json': payload,
    })

    assert response.status_code == 302
    article = News.objects.get(title='Yeni video xəbəri')
    cover = NewsVideoCover.objects.get(news=article)
    assert cover.video_id == 'xyz789'
    assert cover.cover_image_id == media_file.pk
