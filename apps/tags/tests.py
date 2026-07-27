import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from apps.news.models import News
from apps.tags.models import Tag


@pytest.mark.django_db
def test_slug_is_auto_generated_from_name():
    tag = Tag.objects.create(name='İqtisadiyyat')
    assert tag.slug == 'iqtisadiyyat'


@pytest.mark.django_db
def test_tag_detail_only_lists_published_articles_tagged_with_it(client, category, administrator):
    tag = Tag.objects.create(name='Test mövzusu')
    other_tag = Tag.objects.create(name='Digər mövzu')

    tagged = News.objects.create(
        title='Etiketlənmiş xəbər', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    tagged.tags.add(tag)

    not_tagged = News.objects.create(
        title='Digər xəbər', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    not_tagged.tags.add(other_tag)

    response = client.get(reverse('tags:detail', kwargs={'slug': tag.slug}))
    assert response.status_code == 200
    assert tagged in response.context['articles']
    assert not_tagged not in response.context['articles']


@pytest.mark.django_db
def test_unknown_tag_slug_404s(client):
    response = client.get(reverse('tags:detail', kwargs={'slug': 'yoxdur'}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_tag_detail_query_count_does_not_scale_with_article_count(client, subcategory, administrator):
    """Same category.parent.slug concern as apps/news and apps/categories
    — TagDetailView.get_queryset needs select_related('category__parent'),
    not just 'category', once a tagged article's category is itself a
    subcategory."""

    tag = Tag.objects.create(name='Sınaq mövzusu')

    # Warm-up request, not just SiteSettings.get_solo() — see
    # apps/categories/tests.py's identical comment.
    client.get(reverse('tags:detail', kwargs={'slug': tag.slug}))

    def make(n, prefix):
        articles = [
            News.objects.create(
                title=f'{prefix} {i}', short_description='d', content='<p>c</p>',
                category=subcategory, author=administrator,
                status=News.Status.PUBLISHED, published_at=timezone.now(),
            )
            for i in range(n)
        ]
        for article in articles:
            article.tags.add(tag)
        return articles

    make(1, 'Xəbər')
    with CaptureQueriesContext(connection) as one:
        client.get(reverse('tags:detail', kwargs={'slug': tag.slug}))

    make(2, 'Başqa xəbər')
    with CaptureQueriesContext(connection) as three:
        client.get(reverse('tags:detail', kwargs={'slug': tag.slug}))

    assert len(three.captured_queries) == len(one.captured_queries)
