"""HomeView's Redis cache (apps.news.views.HOME_CACHE_KEY) — added once
home_show_all_categories (Phase 34) made the homepage's render cost
scale with however many categories an admin has, uncapped. Covers both
that the cache actually avoids re-querying, and that every real way a
News article's public visibility can change still invalidates it
correctly — including the two bulk .update() call sites that no
post_save/post_delete signal ever sees.
"""

from unittest.mock import patch

import pytest
from django.core.cache import cache
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.news.models import News
from apps.news.views import HomeView, HOME_CACHE_KEY


@pytest.mark.django_db
def test_second_home_page_request_does_not_rebuild_the_context(client, category, administrator):
    News.objects.create(
        title='Xəbər', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )

    client.get(reverse('news:home'))  # populates HOME_CACHE_KEY
    assert cache.get(HOME_CACHE_KEY) is not None

    with patch.object(HomeView, '_build_home_context') as build_mock:
        client.get(reverse('news:home'))
        build_mock.assert_not_called()


@pytest.mark.django_db
def test_creating_a_published_article_invalidates_the_cache(client, category, administrator):
    client.get(reverse('news:home'))
    assert cache.get(HOME_CACHE_KEY) is not None

    News.objects.create(
        title='Yeni xəbər', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )

    assert cache.get(HOME_CACHE_KEY) is None


@pytest.mark.django_db
def test_a_freshly_created_article_appears_on_the_next_home_request_without_manual_cache_clearing(
    client, category, administrator,
):
    client.get(reverse('news:home'))  # caches a homepage with nothing in this category yet

    article = News.objects.create(
        title='Təzə xəbər', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )

    response = client.get(reverse('news:home'))
    assert response.context['hero_slides'][0].pk == article.pk


@pytest.mark.django_db
def test_permanent_delete_invalidates_the_cache(admin_client, published_news):
    admin_client.get(reverse('news:home'))
    assert cache.get(HOME_CACHE_KEY) is not None

    published_news.is_deleted = True
    published_news.save(update_fields=['is_deleted'])
    admin_client.post(reverse('cms:news_permanent_delete', args=[published_news.pk]))

    assert cache.get(HOME_CACHE_KEY) is None


@pytest.mark.django_db
def test_bulk_publish_action_invalidates_the_cache_despite_using_a_bulk_update(admin_client, category, administrator):
    """NewsBulkActionView uses queryset.update(), which post_save never
    fires for — this only passes if the view invalidates by hand."""
    draft = News.objects.create(
        title='Kütləvi dərc ediləcək', short_description='d', content='<p>c</p>',
        category=category, author=administrator, status=News.Status.DRAFT,
    )

    admin_client.get(reverse('news:home'))
    assert cache.get(HOME_CACHE_KEY) is not None

    admin_client.post(reverse('cms:news_bulk_action'), {'selected': [draft.pk], 'bulk_action': 'publish'})

    assert cache.get(HOME_CACHE_KEY) is None


@pytest.mark.django_db
def test_publish_scheduled_invalidates_the_cache_despite_using_a_bulk_update(category, administrator):
    """Same bulk-.update() concern as the test above, for the cron-driven
    command (docs/DEPLOYMENT.md) that flips a due Scheduled article to
    Published — the whole point of that command is the article becoming
    visible without anyone touching the CMS, so this is the one path
    where staleness would matter most."""
    from datetime import timedelta

    News.objects.create(
        title='Planlaşdırılmış xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
        status=News.Status.SCHEDULED, published_at=timezone.now() - timedelta(minutes=1),
    )

    Client().get(reverse('news:home'))
    assert cache.get(HOME_CACHE_KEY) is not None

    call_command('publish_scheduled')

    assert cache.get(HOME_CACHE_KEY) is None
