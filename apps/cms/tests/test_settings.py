"""SiteSettings.home_category_sections_count (apps/cms/views/settings.py's
SettingsUpdateView, apps/news/views.py's HomeView) — how many top-level
categories the homepage turns into a section, previously a hardcoded
HOME_CATEGORY_SECTIONS constant until an admin asked to control it
without a code change."""

import pytest
from django.urls import reverse
from django.utils import timezone

from apps.categories.models import Category
from apps.news.models import News
from apps.settings_app.models import SiteSettings


def _valid_settings_payload(**overrides):
    payload = {
        'site_name': 'Spress',
        'footer_text': '',
        'contact_email': '',
        'contact_phone': '',
        'contact_address': '',
        'home_category_sections_count': 2,
    }
    payload.update(overrides)
    return payload


@pytest.mark.django_db
def test_home_page_shows_exactly_the_configured_number_of_category_sections(client, administrator):
    settings = SiteSettings.get_solo()
    settings.home_category_sections_count = 1
    settings.save()

    for i in range(3):
        category = Category.objects.create(name=f'Kateqoriya {i}', order=i)
        News.objects.create(
            title=f'Xəbər {i}', short_description='d', content='<p>c</p>',
            category=category, author=administrator,
            status=News.Status.PUBLISHED, published_at=timezone.now(),
        )

    response = client.get(reverse('news:home'))

    assert len(response.context['category_sections']) == 1


@pytest.mark.django_db
def test_home_page_respects_a_higher_configured_count(client, administrator):
    settings = SiteSettings.get_solo()
    settings.home_category_sections_count = 3
    settings.save()

    # Two articles per category, not one — HomeView excludes whichever
    # single article becomes the hero (the most recently published one
    # overall) from also appearing in its own category's section, so a
    # category with only one article would end up with an empty (and
    # therefore dropped) section purely by chance, unrelated to the
    # setting this test is actually about.
    for i in range(3):
        category = Category.objects.create(name=f'Kateqoriya {i}', order=i)
        for j in range(2):
            News.objects.create(
                title=f'Xəbər {i}-{j}', short_description='d', content='<p>c</p>',
                category=category, author=administrator,
                status=News.Status.PUBLISHED, published_at=timezone.now(),
            )

    response = client.get(reverse('news:home'))

    assert len(response.context['category_sections']) == 3


@pytest.mark.django_db
def test_settings_form_rejects_a_count_below_the_minimum(admin_client):
    response = admin_client.post(reverse('cms:settings_edit'), _valid_settings_payload(home_category_sections_count=0))
    assert response.status_code == 200
    assert 'home_category_sections_count' in response.context['form'].errors
    SiteSettings.get_solo().refresh_from_db()
    assert SiteSettings.get_solo().home_category_sections_count != 0


@pytest.mark.django_db
def test_settings_form_rejects_a_count_above_the_maximum(admin_client):
    response = admin_client.post(reverse('cms:settings_edit'), _valid_settings_payload(home_category_sections_count=9))
    assert response.status_code == 200
    assert 'home_category_sections_count' in response.context['form'].errors


@pytest.mark.django_db
def test_settings_form_accepts_a_count_within_range(admin_client):
    response = admin_client.post(reverse('cms:settings_edit'), _valid_settings_payload(home_category_sections_count=8))
    assert response.status_code == 302
    assert SiteSettings.get_solo().home_category_sections_count == 8
