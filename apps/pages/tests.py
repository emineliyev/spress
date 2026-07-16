import pytest
from django.core import mail
from django.urls import reverse

from apps.pages.forms import ContactForm
from apps.pages.models import Page


@pytest.mark.django_db
def test_contact_form_required_fields_are_azerbaijani():
    form = ContactForm(data={})
    assert not form.is_valid()
    assert form.errors['name'] == ['Bu sahənin doldurulması mütləqdir.']
    assert form.errors['email'] == ['Bu sahənin doldurulması mütləqdir.']


@pytest.mark.django_db
def test_contact_form_invalid_email_is_azerbaijani():
    form = ContactForm(data={
        'name': 'Test', 'email': 'not-an-email', 'subject': 'Mövzu', 'message': 'Mesaj',
    })
    assert not form.is_valid()
    assert form.errors['email'] == ['Düzgün e-poçt ünvanı daxil edin.']


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
    Page.objects.create(title='Haqqımızda', content='<p>test</p>', is_published=True)
    from django.test import Client

    response = Client().get(reverse('pages:about'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_about_page_404_when_missing(client):
    response = client.get(reverse('pages:about'))
    assert response.status_code == 404


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
