import pytest
from django.core import mail
from django.urls import reverse

from apps.pages.forms import ContactForm
from apps.pages.models import Page
from apps.settings_app.models import AboutStat


@pytest.mark.django_db
def test_contact_form_required_fields_are_azerbaijani():
    form = ContactForm(data={})
    assert not form.is_valid()
    assert form.errors['name'] == ['Bu sahənin doldurulması mütləqdir.']
    # Neither email nor phone is required on its own — see the
    # email-or-phone cross-field test below.
    assert 'email' not in form.errors
    assert 'phone' not in form.errors


@pytest.mark.django_db
def test_contact_form_invalid_email_is_azerbaijani():
    form = ContactForm(data={
        'name': 'Test', 'email': 'not-an-email', 'subject': 'Mövzu', 'message': 'Mesaj',
    })
    assert not form.is_valid()
    assert form.errors['email'] == ['Düzgün e-poçt ünvanı daxil edin.']


@pytest.mark.django_db
def test_contact_form_requires_email_or_phone():
    form = ContactForm(data={'name': 'Test', 'subject': 'Mövzu', 'message': 'Mesaj'})
    assert not form.is_valid()
    assert 'E-poçt və ya telefon nömrəsindən ən azı birini daxil edin.' in form.non_field_errors()


@pytest.mark.django_db
def test_contact_form_valid_with_phone_only():
    form = ContactForm(data={
        'name': 'Test', 'phone': '+994501234567', 'subject': 'Mövzu', 'message': 'Mesaj',
    })
    assert form.is_valid()


@pytest.mark.django_db
def test_contact_form_valid_submission_sends_email(client, settings):
    settings.CELERY_TASK_ALWAYS_EAGER = True
    response = client.post(reverse('pages:contact'), {
        'name': 'Test İstifadəçi', 'email': 'test@example.com', 'subject': 'Sual', 'message': 'Salam.',
    })
    assert response.status_code == 302
    assert len(mail.outbox) == 1


@pytest.mark.django_db
def test_about_page_renders_when_published():
    # slug='about' explicitly — apps.pages.views.ABOUT_SLUG is a fixed
    # literal, not derived from the title, so relying on auto-generation
    # here would slugify to 'haqqimizda' and never match.
    Page.objects.create(title='Haqqımızda', slug='about', content='<p>test</p>', is_published=True)
    from django.test import Client

    response = Client().get(reverse('pages:about'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_about_page_404_when_missing(client):
    response = client.get(reverse('pages:about'))
    assert response.status_code == 404


@pytest.mark.django_db
def test_about_page_shows_cms_managed_stats():
    """Previously three "number + label" cards were hardcoded directly
    in templates/pages/about.html with no CMS control at all — now
    AboutStat rows (apps/cms/views/about_stat.py) drive them."""
    from django.test import Client

    Page.objects.create(title='Haqqımızda', slug='about', content='<p>test</p>', is_published=True)
    AboutStat.objects.create(number='2018', label='Fəaliyyətə başlayıb', order=0)
    AboutStat.objects.create(number='40+', label='Jurnalist və redaktor', order=1)

    response = Client().get(reverse('pages:about'))

    assert response.status_code == 200
    content = response.content.decode()
    assert '2018' in content
    assert 'Fəaliyyətə başlayıb' in content
    assert '40+' in content


@pytest.mark.django_db
def test_unpublished_static_page_is_not_publicly_reachable(client):
    page = Page.objects.create(title='Gizli səhifə', content='<p>c</p>', is_published=False)
    response = client.get(page.get_absolute_url())
    assert response.status_code == 404


@pytest.mark.django_db
def test_published_static_page_renders_via_generic_detail_route(client):
    page = Page.objects.create(title='İstifadə şərtləri', content='<p>Şərtlər</p>', is_published=True)
    response = client.get(page.get_absolute_url())
    assert response.status_code == 200
    assert 'Şərtlər'.encode() in response.content
