import io

import pytest
from django.core.cache import cache
from django.core.files.base import ContentFile
from PIL import Image


@pytest.fixture(autouse=True)
def _clear_cache():
    # Every test shares the same real Redis-backed cache as dev/prod
    # (config/settings/base.py — no LocMemCache override for tests) —
    # login-lockout counters (apps/accounts/services.py) and the
    # homepage context cache (apps/news/views.py's HOME_CACHE_KEY) both
    # live there, so one test's state could otherwise leak into the
    # next entirely unrelated one.
    cache.clear()
    yield
    cache.clear()


@pytest.fixture
def administrator(django_user_model):
    return django_user_model.objects.create_user(
        username='administrator',
        password='test-pass-12345',
        role=django_user_model.Role.ADMINISTRATOR,
        email='administrator@example.com',
    )


@pytest.fixture
def journalist(django_user_model):
    return django_user_model.objects.create_user(
        username='journalist',
        password='test-pass-12345',
        role=django_user_model.Role.JOURNALIST,
        email='journalist@example.com',
    )


@pytest.fixture
def editor_in_chief(django_user_model):
    return django_user_model.objects.create_user(
        username='editor_in_chief',
        password='test-pass-12345',
        role=django_user_model.Role.EDITOR_IN_CHIEF,
        email='editor-in-chief@example.com',
    )


@pytest.fixture
def editor(django_user_model):
    return django_user_model.objects.create_user(
        username='editor',
        password='test-pass-12345',
        role=django_user_model.Role.EDITOR,
        email='editor@example.com',
    )


@pytest.fixture
def content_manager(django_user_model):
    return django_user_model.objects.create_user(
        username='content_manager',
        password='test-pass-12345',
        role=django_user_model.Role.CONTENT_MANAGER,
        email='content-manager@example.com',
    )


@pytest.fixture
def admin_client(client, administrator):
    """A test client already logged in as an Administrator — most CMS
    tests care about behavior once inside, not the login flow itself."""
    client.force_login(administrator)
    return client


@pytest.fixture
def journalist_client(client, journalist):
    client.force_login(journalist)
    return client


@pytest.fixture
def editor_in_chief_client(client, editor_in_chief):
    client.force_login(editor_in_chief)
    return client


@pytest.fixture
def editor_client(client, editor):
    client.force_login(editor)
    return client


@pytest.fixture
def content_manager_client(client, content_manager):
    client.force_login(content_manager)
    return client


@pytest.fixture
def category(db):
    from apps.categories.models import Category

    return Category.objects.create(name='İqtisadiyyat')


@pytest.fixture
def subcategory(db, category):
    from apps.categories.models import Category

    return Category.objects.create(name='Bank sektoru', parent=category)


@pytest.fixture
def published_news(db, category, administrator):
    from django.utils import timezone

    from apps.news.models import News

    return News.objects.create(
        title='Test xəbəri',
        short_description='Qısa təsvir',
        content='<p>Məzmun</p>',
        category=category,
        author=administrator,
        status=News.Status.PUBLISHED,
        published_at=timezone.now(),
    )


@pytest.fixture
def draft_news(db, category, administrator):
    from apps.news.models import News

    return News.objects.create(
        title='Qaralama xəbər',
        short_description='Qısa təsvir',
        content='<p>Məzmun</p>',
        category=category,
        author=administrator,
        status=News.Status.DRAFT,
    )


@pytest.fixture
def sample_image_bytes():
    """A tiny real JPEG generated in memory — used everywhere a test needs
    to upload/attach an actual (not fake-extension) image file."""

    def _make(width=800, height=600, fmt='JPEG'):
        buffer = io.BytesIO()
        Image.new('RGB', (width, height), color=(200, 30, 30)).save(buffer, format=fmt)
        buffer.seek(0)
        return buffer.read()

    return _make


@pytest.fixture
def sample_image_file(sample_image_bytes):
    return ContentFile(sample_image_bytes(), name='sample.jpg')


@pytest.fixture
def media_file(db, sample_image_bytes):
    """A ready-to-use `MediaFile` row, bypassing the upload/crop pipeline
    (that pipeline gets its own dedicated tests in
    apps/media_manager/tests/) — this fixture is for tests that just need
    *some* valid MediaFile to attach as a featured_image/banner/etc."""
    from apps.media_manager.models import MediaFile

    media = MediaFile(
        original_filename='sample.jpg',
        width=800,
        height=600,
        file_size=len(sample_image_bytes()),
        file_format=MediaFile.Format.JPEG,
    )
    media.file.save('sample.jpg', ContentFile(sample_image_bytes()), save=False)
    media.save()
    return media
