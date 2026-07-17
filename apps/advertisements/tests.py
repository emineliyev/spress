import pytest
from django.utils import timezone

from apps.advertisements.forms import AdvertisementForm
from apps.advertisements.models import AdPosition, Advertisement


@pytest.mark.django_db
def test_missing_start_date_shows_azerbaijani_error(media_file):
    """A blank required field used to render Django's stock English
    "This field is required." — easy to miss, which made the form look
    like it was silently failing to save rather than rejecting a
    specific field (reported by the user testing the CMS directly)."""
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    form = AdvertisementForm(data={
        'title': 'Test kampaniya',
        'position': position.pk,
        'banner': media_file.pk,
        'target_url': 'https://example.com',
        'price': '0',
        # start_date deliberately omitted
    })
    assert not form.is_valid()
    assert form.errors['start_date'] == ['Bu sahənin doldurulması mütləqdir.']


@pytest.mark.django_db
def test_missing_title_shows_azerbaijani_error(media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    form = AdvertisementForm(data={
        'position': position.pk,
        'banner': media_file.pk,
        'target_url': 'https://example.com',
        'price': '0',
        'start_date': '2026-01-01T00:00',
    })
    assert not form.is_valid()
    assert form.errors['title'] == ['Bu sahənin doldurulması mütləqdir.']


@pytest.mark.django_db
def test_overlapping_active_campaign_in_same_slot_is_blocked(media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    Advertisement.objects.create(
        title='Mövcud kampaniya', position=position, banner=media_file, target_url='https://example.com',
        start_date=timezone.now(), is_active=True,
    )

    form = AdvertisementForm(data={
        'title': 'Yeni kampaniya', 'position': position.pk, 'banner': media_file.pk,
        'target_url': 'https://example.com', 'price': '0',
        'start_date': (timezone.now() + timezone.timedelta(hours=1)).strftime('%Y-%m-%dT%H:%M'),
        'is_active': 'on',
    })
    assert not form.is_valid()
    assert 'Mövcud kampaniya' in form.errors['position'][0]


@pytest.mark.django_db
def test_non_overlapping_campaign_in_same_slot_is_allowed(media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    Advertisement.objects.create(
        title='Bitmiş kampaniya', position=position, banner=media_file, target_url='https://example.com',
        start_date=timezone.now() - timezone.timedelta(days=10),
        end_date=timezone.now() - timezone.timedelta(days=1),
        is_active=True,
    )

    form = AdvertisementForm(data={
        'title': 'Yeni kampaniya', 'position': position.pk, 'banner': media_file.pk,
        'target_url': 'https://example.com', 'price': '0',
        'start_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        'is_active': 'on',
    })
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_inactive_campaign_does_not_conflict(media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    Advertisement.objects.create(
        title='Deaktiv kampaniya', position=position, banner=media_file, target_url='https://example.com',
        start_date=timezone.now(), is_active=False,
    )

    form = AdvertisementForm(data={
        'title': 'Yeni kampaniya', 'position': position.pk, 'banner': media_file.pk,
        'target_url': 'https://example.com', 'price': '0',
        'start_date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        'is_active': 'on',
    })
    assert form.is_valid(), form.errors


@pytest.mark.django_db
def test_editing_a_campaign_does_not_conflict_with_itself(media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    ad = Advertisement.objects.create(
        title='Kampaniya', position=position, banner=media_file, target_url='https://example.com',
        start_date=timezone.now(), is_active=True,
    )

    form = AdvertisementForm(data={
        'title': 'Kampaniya (redaktə)', 'position': position.pk, 'banner': media_file.pk,
        'target_url': 'https://example.com', 'price': '0',
        'start_date': ad.start_date.strftime('%Y-%m-%dT%H:%M'),
        'is_active': 'on',
    }, instance=ad)
    assert form.is_valid(), form.errors
