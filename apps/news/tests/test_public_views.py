import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
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


def _make_articles(n, category, administrator, title_prefix='Xəbər'):
    return [
        News.objects.create(
            title=f'{title_prefix} {i}', short_description='d', content='<p>c</p>',
            category=category, author=administrator,
            status=News.Status.PUBLISHED, published_at=timezone.now(),
        )
        for i in range(n)
    ]


@pytest.mark.django_db
def test_home_page_query_count_does_not_scale_with_article_count(client, subcategory, administrator):
    """category_sections (HomeView.get_context_data) shows subcategory
    articles too (News.objects.in_category on the parent top-level
    category) — each renders via news_card.html, whose category link
    needs category.parent.slug. Without select_related('category__parent')
    that was one extra query per article instead of one join: invisible
    with a single article in a smoke test, real at any actual traffic
    scale. Asserting the query count is identical for 1 vs 3 articles is
    what actually proves it, not a fixed expected count (which would just
    be a magic number unrelated to the bug this guards against)."""

    # A warm-up request, not just SiteSettings.get_solo() — two things
    # lazily populate on first access and must not fall unevenly across
    # the two captures below: SiteSettings' own row (get_or_create), and
    # now also apps.core.context_processors.site()'s Redis cache (Phase
    # 36), which only a real request through the context processor
    # actually populates.
    client.get(reverse('news:home'))

    _make_articles(1, subcategory, administrator)
    with CaptureQueriesContext(connection) as one:
        client.get(reverse('news:home'))

    _make_articles(2, subcategory, administrator, title_prefix='Başqa xəbər')
    with CaptureQueriesContext(connection) as three:
        client.get(reverse('news:home'))

    assert len(three.captured_queries) == len(one.captured_queries)


@pytest.mark.django_db
def test_article_detail_related_articles_query_count_does_not_scale(client, subcategory, administrator):
    """related_articles (NewsDetailView.get_context_data) falls back to
    News.objects.in_category(article.category) when the article has no
    manually curated related_articles — same category.parent.slug
    concern as above, this time for a subcategory article's siblings."""

    articles = _make_articles(4, subcategory, administrator)
    main = articles[0]

    # NewsDetailView.get_object() only fires the view_count UPDATE once
    # per session (SESSION_VIEWED_KEY, see test_viewing_an_article_
    # increments_view_count_once_per_session above) — this warm-up visit
    # spends that one-time query so it doesn't fall unevenly on whichever
    # capture happens to run first below.
    client.get(main.get_absolute_url())

    with CaptureQueriesContext(connection) as few_siblings:
        client.get(main.get_absolute_url())

    _make_articles(3, subcategory, administrator, title_prefix='Əlavə xəbər')
    with CaptureQueriesContext(connection) as more_siblings:
        client.get(main.get_absolute_url())

    assert len(more_siblings.captured_queries) == len(few_siblings.captured_queries)


@pytest.mark.django_db
def test_search_results_query_count_does_not_scale_with_match_count(client, subcategory, administrator):
    # Warm-up request, not just SiteSettings.get_solo() — see
    # test_home_page_query_count_does_not_scale_with_article_count above.
    client.get(reverse('news:search'))
    _make_articles(1, subcategory, administrator, title_prefix='Axtarışlıq xəbər')
    with CaptureQueriesContext(connection) as one_match:
        client.get(reverse('news:search'), {'q': 'Axtarışlıq'})

    _make_articles(3, subcategory, administrator, title_prefix='Axtarışlıq xəbər')
    with CaptureQueriesContext(connection) as four_matches:
        client.get(reverse('news:search'), {'q': 'Axtarışlıq'})

    assert len(four_matches.captured_queries) == len(one_match.captured_queries)


@pytest.mark.django_db
def test_article_detail_shows_the_short_description_as_a_deck(client, published_news):
    """short_description previously only fed <meta> tags (SEO/social
    preview) — never actually rendered as visible text on the article
    page itself, despite its own form widget already being labeled
    "Qısa təsvir (dek)..." implying it should be."""
    response = client.get(published_news.get_absolute_url())
    assert response.status_code == 200
    assert published_news.short_description in response.content.decode()


@pytest.mark.django_db
def test_article_byline_shows_redaksiya_by_default(client, published_news):
    """show_author_name defaults to False (editor request — most
    articles are aggregated/edited by staff, not individually bylined)
    — the public byline falls back to a generic "Redaksiya" label
    instead of the real author's name unless explicitly opted into."""
    response = client.get(published_news.get_absolute_url())
    content = response.content.decode()
    assert 'Redaksiya' in content
    # published_news's author fixture has no first/last name, so the
    # template's own display fallback is the username — that must not
    # leak into the page while show_author_name is off.
    assert published_news.author.username not in content


@pytest.mark.django_db
def test_article_byline_shows_the_real_name_when_enabled(client, published_news):
    published_news.show_author_name = True
    published_news.save(update_fields=['show_author_name'])

    response = client.get(published_news.get_absolute_url())
    content = response.content.decode()
    assert published_news.author.username in content
    assert 'Redaksiya' not in content


@pytest.mark.django_db
def test_news_card_shows_the_short_description(client, published_news):
    """CLAUDE.md ch.6 "Cards" lists Short description as a standard
    news-card field — search_results.html renders every result through
    components/news_card.html, so this covers every page that reuses it
    (category, search, tag, related articles)."""
    response = client.get(reverse('news:search'), {'q': published_news.title[:5]})
    assert response.status_code == 200
    assert published_news.short_description in response.content.decode()
