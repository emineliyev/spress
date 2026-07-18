"""Moving a MediaFile between folders (templates/cms/partials/media_grid.html's
per-card "Qovluğa köçür" select, apps.cms.views.media.MediaMoveView)."""

import pytest
from django.urls import reverse

from apps.logs.models import ActivityLog
from apps.media_manager.models import Folder


@pytest.mark.django_db
def test_move_view_requires_login(client, media_file):
    response = client.post(reverse('cms:media_move', args=[media_file.pk]), {'folder': ''})
    assert response.status_code == 302
    assert '/accounts/login' in response.url


@pytest.mark.django_db
def test_move_assigns_a_folder(admin_client, media_file):
    folder = Folder.objects.create(name='Bannerlər')

    response = admin_client.post(reverse('cms:media_move', args=[media_file.pk]), {'folder': folder.pk})

    assert response.status_code == 302
    media_file.refresh_from_db()
    assert media_file.folder_id == folder.pk
    assert ActivityLog.objects.filter(action=ActivityLog.Action.MEDIA_MOVED).exists()


@pytest.mark.django_db
def test_move_between_two_folders(admin_client, media_file):
    folder_a = Folder.objects.create(name='A')
    folder_b = Folder.objects.create(name='B')
    media_file.folder = folder_a
    media_file.save(update_fields=['folder'])

    admin_client.post(reverse('cms:media_move', args=[media_file.pk]), {'folder': folder_b.pk})

    media_file.refresh_from_db()
    assert media_file.folder_id == folder_b.pk


@pytest.mark.django_db
def test_move_to_unfiled_clears_the_folder(admin_client, media_file):
    folder = Folder.objects.create(name='Bannerlər')
    media_file.folder = folder
    media_file.save(update_fields=['folder'])

    admin_client.post(reverse('cms:media_move', args=[media_file.pk]), {'folder': '__unfiled__'})

    media_file.refresh_from_db()
    assert media_file.folder_id is None


@pytest.mark.django_db
def test_move_redirects_back_to_the_filtered_grid_it_came_from(admin_client, media_file):
    folder = Folder.objects.create(name='Bannerlər')

    response = admin_client.post(reverse('cms:media_move', args=[media_file.pk]), {
        'folder': folder.pk, 'return_folder': '', 'return_format': 'webp', 'return_q': 'logo', 'return_page': '2',
    })

    assert response.status_code == 302
    assert 'format=webp' in response.url
    assert 'q=logo' in response.url
    assert 'page=2' in response.url
