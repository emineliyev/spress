import pytest
from django.core.exceptions import ValidationError
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from apps.categories.models import Category
from apps.categories.views import CATEGORY_ARTICLES_PER_PAGE
from apps.news.models import News


@pytest.mark.django_db
def test_slug_is_auto_generated_from_name():
    category = Category.objects.create(name='Mədəniyyət')
    assert category.slug == 'medeniyyet'


@pytest.mark.django_db
def test_subcategory_cannot_itself_have_a_subcategory(category, subcategory):
    grandchild = Category(name='Alt-alt kateqoriya', parent=subcategory)
    with pytest.raises(ValidationError):
        grandchild.clean()


@pytest.mark.django_db
def test_category_cannot_be_its_own_parent(category):
    category.parent = category
    with pytest.raises(ValidationError):
        category.clean()


@pytest.mark.django_db
def test_empty_top_level_category_is_hidden_from_nav(client, category):
    # `category` fixture has no published news at all.
    response = client.get('/')
    assert category.name.encode() not in response.content


@pytest.mark.django_db
def test_category_with_published_news_appears_in_nav(client, category, administrator):
    News.objects.create(
        title='Naviqasiya testi', short_description='d', content='<p>c</p>',
        category=category, author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    response = client.get('/')
    assert category.name.encode() in response.content


@pytest.mark.django_db
def test_empty_subcategory_hidden_while_populated_sibling_shows(client, category, administrator):
    populated_child = Category.objects.create(name='Doldurulmuş alt', parent=category)
    empty_child = Category.objects.create(name='Boş alt', parent=category)
    News.objects.create(
        title='Alt kateqoriya xəbəri', short_description='d', content='<p>c</p>',
        category=populated_child, author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )

    response = client.get('/')
    assert populated_child.name.encode() in response.content
    assert empty_child.name.encode() not in response.content


@pytest.mark.django_db
def test_category_detail_page_paginates_articles(client, category, administrator):
    for i in range(CATEGORY_ARTICLES_PER_PAGE + 3):
        News.objects.create(
            title=f'Xəbər {i}', short_description='d', content='<p>c</p>', category=category,
            author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
        )
    response = client.get(reverse('categories:category_detail', kwargs={'category_slug': category.slug}))
    assert response.status_code == 200
    assert len(response.context['articles']) == CATEGORY_ARTICLES_PER_PAGE
    assert response.context['page_obj'].has_next()


@pytest.mark.django_db
def test_top_level_category_page_includes_subcategory_articles(client, category, subcategory, administrator):
    article = News.objects.create(
        title='Alt kateqoriya', short_description='d', content='<p>c</p>', category=subcategory,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    response = client.get(reverse('categories:category_detail', kwargs={'category_slug': category.slug}))
    assert article in response.context['articles']


@pytest.mark.django_db
def test_deleted_category_returns_404(client, category):
    category.is_deleted = True
    category.save()
    response = client.get(reverse('categories:category_detail', kwargs={'category_slug': category.slug}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_category_index_lists_populated_category(client, category, administrator):
    News.objects.create(
        title='İndeks testi', short_description='d', content='<p>c</p>',
        category=category, author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    response = client.get(reverse('categories:index'))
    assert response.status_code == 200
    assert category in response.context['categories']


@pytest.mark.django_db
def test_category_index_excludes_empty_category(client, category):
    # `category` fixture has no published news at all.
    response = client.get(reverse('categories:index'))
    assert category not in response.context['categories']


@pytest.mark.django_db
def test_category_index_shows_subcategory_links(client, category, subcategory, administrator):
    News.objects.create(
        title='Alt kateqoriya xəbəri', short_description='d', content='<p>c</p>',
        category=subcategory, author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    response = client.get(reverse('categories:index'))
    assert subcategory.name.encode() in response.content


@pytest.mark.django_db
def test_category_page_query_count_does_not_scale_with_article_count(client, category, subcategory, administrator):
    """A top-level category page shows its subcategories' articles too
    (News.objects.in_category), each rendered via news_card.html — whose
    category link needs category.parent.slug. Without
    select_related('category__parent') on CategoryDetailView.get_queryset,
    that's one extra query per article instead of one join."""

    # Warm-up request, not just SiteSettings.get_solo() — two things
    # lazily populate on first access and must not fall unevenly across
    # the two captures below: SiteSettings' own row (get_or_create), and
    # apps.core.context_processors.site()'s Redis cache (Phase 36), which
    # only a real request through the context processor actually
    # populates.
    client.get(category.get_absolute_url())

    def make(n, prefix):
        return [
            News.objects.create(
                title=f'{prefix} {i}', short_description='d', content='<p>c</p>',
                category=subcategory, author=administrator,
                status=News.Status.PUBLISHED, published_at=timezone.now(),
            )
            for i in range(n)
        ]

    make(1, 'Xəbər')
    with CaptureQueriesContext(connection) as one:
        client.get(category.get_absolute_url())

    make(2, 'Başqa xəbər')
    with CaptureQueriesContext(connection) as three:
        client.get(category.get_absolute_url())

    assert len(three.captured_queries) == len(one.captured_queries)
