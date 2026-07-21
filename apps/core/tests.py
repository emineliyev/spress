import pytest
from django.test import RequestFactory
from django.utils import timezone

from apps.categories.models import Category
from apps.core.context_processors import NAV_VISIBLE_CATEGORY_COUNT, site
from apps.core.utils import az_slugify, generate_unique_slug, sanitize_rich_text_html
from apps.news.models import News


def test_az_slugify_transliterates_azerbaijani_letters():
    assert az_slugify('Əlaqə') == 'elaqe'
    assert az_slugify('İstifadə şərtləri') == 'istifade-sertleri'


def test_az_slugify_non_representable_text_is_empty():
    # Confirms the edge case generate_unique_slug has to guard against —
    # not itself a bug, just documents why the fallback exists.
    assert az_slugify('Дубликат') == ''


@pytest.mark.django_db
def test_generate_unique_slug_appends_suffix_on_collision():
    first = Category.objects.create(name='Siyasət')
    assert first.slug == 'siyaset'

    second = Category(name='Siyasət')
    slug = generate_unique_slug(second, second.name)
    assert slug == 'siyaset-2'


@pytest.mark.django_db
def test_generate_unique_slug_falls_back_when_slugify_is_empty():
    instance = Category(name='Дубликат')
    slug = generate_unique_slug(instance, instance.name)
    assert slug != ''
    assert len(slug) == 8


@pytest.mark.django_db
def test_generate_unique_slug_excludes_own_pk_on_update():
    category = Category.objects.create(name='Mədəniyyət')
    # Re-slugifying the same instance (e.g. re-saving without a title
    # change) must not collide with itself.
    slug = generate_unique_slug(category, category.name)
    assert slug == category.slug


def test_sanitize_keeps_referrerpolicy_on_youtube_iframe():
    """Without `referrerpolicy`, YouTube's player fails with a generic
    "Error 153 / player configuration error" instead of actually loading
    — SecurityMiddleware's site-wide `Referrer-Policy: same-origin`
    strips the referrer on any cross-origin request, and YouTube's
    player can't initialize without one (confirmed by reproducing the
    error with and without this attribute). If the sanitizer ever
    dropped `referrerpolicy` again, every embedded video on the site
    would silently start failing the same way."""
    html = (
        '<figure class="media"><div class="media-embed media-embed--youtube">'
        '<iframe src="https://www.youtube-nocookie.com/embed/dQw4w9WgXcQ" '
        'allow="accelerometer; autoplay" referrerpolicy="strict-origin-when-cross-origin" '
        'allowfullscreen loading="lazy"></iframe></div></figure>'
    )
    cleaned = sanitize_rich_text_html(html)
    assert 'referrerpolicy="strict-origin-when-cross-origin"' in cleaned


def test_sanitize_rejects_iframe_from_a_non_youtube_host():
    html = '<iframe src="https://evil.example.com/embed"></iframe>'
    cleaned = sanitize_rich_text_html(html)
    assert 'evil.example.com' not in cleaned


@pytest.mark.django_db
def test_nav_category_split_caps_visible_count_and_keeps_full_list_for_footer(administrator):
    """templates/components/header.html has no wrap/scroll handling for
    the primary nav row — past NAV_VISIBLE_CATEGORY_COUNT top-level
    categories, the rest must go into the "Digər kateqoriyalar" dropdown
    instead of silently overflowing the container. footer.html still
    needs every category (its own full sitemap-style listing), so
    `main_categories` itself must stay uncapped."""
    for i in range(NAV_VISIBLE_CATEGORY_COUNT + 3):
        category = Category.objects.create(name=f'Kateqoriya {i}', order=i)
        News.objects.create(
            title=f'Xəbər {i}', short_description='d', content='<p>c</p>',
            category=category, author=administrator,
            status=News.Status.PUBLISHED, published_at=timezone.now(),
        )

    context = site(RequestFactory().get('/'))

    assert len(context['main_categories']) == NAV_VISIBLE_CATEGORY_COUNT + 3
    assert len(context['nav_categories']) == NAV_VISIBLE_CATEGORY_COUNT
    assert len(context['nav_overflow_categories']) == 3
    assert context['nav_categories'] + context['nav_overflow_categories'] == context['main_categories']


@pytest.mark.django_db
def test_nav_overflow_is_empty_when_categories_fit(administrator):
    category = Category.objects.create(name='Siyasət')
    News.objects.create(
        title='Xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
        status=News.Status.PUBLISHED, published_at=timezone.now(),
    )

    context = site(RequestFactory().get('/'))

    assert context['nav_overflow_categories'] == []
