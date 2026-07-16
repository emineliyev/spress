import pytest
from django.urls import reverse
from django.utils import timezone

from apps.news.models import News


@pytest.mark.django_db
def test_home_page_renders_with_no_content(client):
    response = client.get(reverse('news:home'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_page_hero_prefers_featured_over_latest(client, category, administrator):
    latest = News.objects.create(
        title='Ən son xəbər', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    featured = News.objects.create(
        title='Seçilmiş xəbər', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED,
        published_at=timezone.now() - timezone.timedelta(hours=1), is_featured=True,
    )
    response = client.get(reverse('news:home'))
    assert response.context['hero'].pk == featured.pk
    assert response.context['hero'].pk != latest.pk


@pytest.mark.django_db
def test_home_page_popular_news_ordered_by_view_count(client, category, administrator):
    low = News.objects.create(
        title='Az oxunan', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(), view_count=5,
    )
    high = News.objects.create(
        title='Çox oxunan', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(), view_count=500,
    )
    response = client.get(reverse('news:home'))
    popular_ids = [a.pk for a in response.context['popular_news']]
    assert popular_ids.index(high.pk) < popular_ids.index(low.pk)


@pytest.mark.django_db
def test_anonymous_gets_404_for_unpublished_article(client, draft_news):
    response = client.get(draft_news.get_absolute_url())
    assert response.status_code == 404


@pytest.mark.django_db
def test_staff_can_preview_unpublished_article(admin_client, draft_news):
    response = admin_client.get(draft_news.get_absolute_url())
    assert response.status_code == 200


@pytest.mark.django_db
def test_viewing_an_article_increments_view_count_once_per_session(client, published_news):
    assert published_news.view_count == 0

    client.get(published_news.get_absolute_url())
    published_news.refresh_from_db()
    assert published_news.view_count == 1

    # Second view in the *same* session must not count again.
    client.get(published_news.get_absolute_url())
    published_news.refresh_from_db()
    assert published_news.view_count == 1


@pytest.mark.django_db
def test_viewing_from_a_different_session_counts_again(published_news):
    from django.test import Client

    Client().get(published_news.get_absolute_url())
    Client().get(published_news.get_absolute_url())
    published_news.refresh_from_db()
    assert published_news.view_count == 2


@pytest.mark.django_db
def test_search_matches_title(client, published_news):
    response = client.get(reverse('news:search'), {'q': published_news.title[:5]})
    assert published_news in response.context['results']


@pytest.mark.django_db
def test_search_with_empty_query_does_not_crash(client):
    response = client.get(reverse('news:search'))
    assert response.status_code == 200
    assert list(response.context['results']) == []


@pytest.mark.django_db
def test_sitemap_renders(client, published_news):
    response = client.get(reverse('seo:sitemap'))
    assert response.status_code == 200
    assert response['Content-Type'].startswith('application/xml')


@pytest.mark.django_db
def test_robots_txt_renders(client):
    response = client.get(reverse('seo:robots_txt'))
    assert response.status_code == 200
    assert b'Disallow: /cms/' in response.content
