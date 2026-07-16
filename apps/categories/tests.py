import pytest
from django.core.exceptions import ValidationError
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
