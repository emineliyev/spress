"""CMS-side Contact Message inbox — a submitted contact form message is
stored (apps.pages.models.ContactMessage), listed/filterable in the CMS,
and its read/unread status can be tracked (opening it marks it read;
CMS staff can flip it back)."""

import pytest
from django.urls import reverse

from apps.pages.models import ContactMessage


@pytest.mark.django_db
def test_contact_form_submission_creates_a_cms_visible_message(client):
    client.post(reverse('pages:contact'), {
        'name': 'Test İstifadəçi', 'email': 'test@example.com',
        'subject': 'Sual', 'message': 'Salam, sualım var.',
    })

    message = ContactMessage.objects.get()
    assert message.name == 'Test İstifadəçi'
    assert message.subject == 'Sual'
    assert message.status == ContactMessage.Status.NEW


@pytest.mark.django_db
def test_contact_message_list_requires_login(client):
    response = client.get(reverse('cms:contact_message_list'))
    assert response.status_code == 302


@pytest.mark.django_db
def test_contact_message_list_shows_submitted_messages(admin_client):
    ContactMessage.objects.create(name='Ali', email='ali@example.com', subject='Sual 1', message='m')

    response = admin_client.get(reverse('cms:contact_message_list'))

    assert response.status_code == 200
    assert 'Ali' in response.content.decode()


@pytest.mark.django_db
def test_contact_message_list_filters_by_status(admin_client):
    ContactMessage.objects.create(
        name='Yeni müraciət', email='a@example.com', subject='s', message='m',
        status=ContactMessage.Status.NEW,
    )
    ContactMessage.objects.create(
        name='Oxunmuş müraciət', email='b@example.com', subject='s', message='m',
        status=ContactMessage.Status.READ,
    )

    response = admin_client.get(reverse('cms:contact_message_list'), {'status': 'new'})
    html = response.content.decode()

    assert 'Yeni müraciət' in html
    assert 'Oxunmuş müraciət' not in html


@pytest.mark.django_db
def test_opening_a_message_marks_it_read(admin_client):
    message = ContactMessage.objects.create(name='Ali', email='a@example.com', subject='s', message='m')
    assert message.status == ContactMessage.Status.NEW

    response = admin_client.get(reverse('cms:contact_message_detail', args=[message.pk]))

    assert response.status_code == 200
    message.refresh_from_db()
    assert message.status == ContactMessage.Status.READ


@pytest.mark.django_db
def test_toggle_status_flips_read_back_to_new(admin_client):
    message = ContactMessage.objects.create(
        name='Ali', email='a@example.com', subject='s', message='m',
        status=ContactMessage.Status.READ,
    )

    response = admin_client.post(reverse('cms:contact_message_toggle_status', args=[message.pk]))

    assert response.status_code == 302
    message.refresh_from_db()
    assert message.status == ContactMessage.Status.NEW


@pytest.mark.django_db
def test_sidebar_unread_count_reflects_new_messages(admin_client):
    ContactMessage.objects.create(name='Ali', email='a@example.com', subject='s', message='m')
    ContactMessage.objects.create(name='Vəli', email='b@example.com', subject='s', message='m')
    ContactMessage.objects.create(
        name='Baxılmış', email='c@example.com', subject='s', message='m',
        status=ContactMessage.Status.READ,
    )

    response = admin_client.get(reverse('cms:dashboard'))

    assert response.context['unread_contact_message_count'] == 2
