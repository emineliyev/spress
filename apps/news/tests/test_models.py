import pytest
from django.utils import timezone

from apps.news.models import News


@pytest.mark.django_db
def test_slug_is_auto_generated_from_title(category, administrator):
    article = News.objects.create(
        title='Yeni İqtisadi Paket Təqdim Olundu',
        short_description='desc',
        content='<p>content</p>',
        category=category,
        author=administrator,
    )
    assert article.slug == 'yeni-iqtisadi-paket-teqdim-olundu'


@pytest.mark.django_db
def test_duplicate_title_gets_a_distinct_slug(category, administrator):
    kwargs = dict(
        short_description='desc', content='<p>content</p>', category=category, author=administrator,
    )
    first = News.objects.create(title='Eyni Başlıq', **kwargs)
    second = News.objects.create(title='Eyni Başlıq', **kwargs)
    assert first.slug == 'eyni-basliq'
    assert second.slug == 'eyni-basliq-2'


@pytest.mark.django_db
def test_reading_time_scales_with_content_length(category, administrator):
    short_article = News.objects.create(
        title='Qısa xəbər', short_description='d', content='<p>' + ' '.join(['söz'] * 50) + '</p>',
        category=category, author=administrator,
    )
    long_article = News.objects.create(
        title='Uzun xəbər', short_description='d', content='<p>' + ' '.join(['söz'] * 800) + '</p>',
        category=category, author=administrator,
    )
    assert short_article.reading_time_minutes == 1
    assert long_article.reading_time_minutes == 4


@pytest.mark.django_db
def test_visible_excludes_soft_deleted(published_news):
    published_news.is_deleted = True
    published_news.save()
    assert not News.objects.visible().filter(pk=published_news.pk).exists()
    # The row itself still exists — soft delete, not a real delete.
    assert News.objects.filter(pk=published_news.pk).exists()


@pytest.mark.django_db
def test_published_excludes_drafts_and_future_scheduled(category, administrator):
    draft = News.objects.create(
        title='Qaralama', short_description='d', content='<p>c</p>', category=category, author=administrator,
        status=News.Status.DRAFT,
    )
    scheduled_future = News.objects.create(
        title='Planlaşdırılmış', short_description='d', content='<p>c</p>', category=category, author=administrator,
        status=News.Status.PUBLISHED, published_at=timezone.now() + timezone.timedelta(days=1),
    )
    published = News.objects.create(
        title='Dərc olunmuş', short_description='d', content='<p>c</p>', category=category, author=administrator,
        status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    published_ids = set(News.objects.published().values_list('pk', flat=True))
    assert draft.pk not in published_ids
    assert scheduled_future.pk not in published_ids
    assert published.pk in published_ids


@pytest.mark.django_db
def test_breaking_only_returns_published_breaking_articles(category, administrator):
    breaking_draft = News.objects.create(
        title='Təcili qaralama', short_description='d', content='<p>c</p>', category=category, author=administrator,
        status=News.Status.DRAFT, is_breaking=True,
    )
    breaking_published = News.objects.create(
        title='Təcili dərc', short_description='d', content='<p>c</p>', category=category, author=administrator,
        status=News.Status.PUBLISHED, published_at=timezone.now(), is_breaking=True,
    )
    breaking_ids = set(News.objects.breaking().values_list('pk', flat=True))
    assert breaking_draft.pk not in breaking_ids
    assert breaking_published.pk in breaking_ids


@pytest.mark.django_db
def test_in_category_includes_subcategory_articles_on_parent_page(category, subcategory, administrator):
    in_parent = News.objects.create(
        title='Ana kateqoriyada', short_description='d', content='<p>c</p>', category=category,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    in_child = News.objects.create(
        title='Alt kateqoriyada', short_description='d', content='<p>c</p>', category=subcategory,
        author=administrator, status=News.Status.PUBLISHED, published_at=timezone.now(),
    )
    parent_page_ids = set(News.objects.in_category(category).values_list('pk', flat=True))
    assert in_parent.pk in parent_page_ids
    assert in_child.pk in parent_page_ids

    # But the subcategory's own page only shows its own articles.
    child_page_ids = set(News.objects.in_category(subcategory).values_list('pk', flat=True))
    assert in_child.pk in child_page_ids
    assert in_parent.pk not in child_page_ids


@pytest.mark.django_db
def test_breadcrumb_items_include_parent_for_subcategory_articles(subcategory, administrator):
    article = News.objects.create(
        title='Alt kateqoriya xəbəri', short_description='d', content='<p>c</p>', category=subcategory,
        author=administrator,
    )
    items = article.breadcrumb_items
    assert items[0][0] == subcategory.parent.name
    assert items[1][0] == subcategory.name
    assert items[2] == (article.title, None)
