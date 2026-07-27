"""Stage → crop-preview flow (apps.cms.views.media.MediaUploadStageView,
MediaTempPreviewView, static/js/cms/media-uploader.js's Cropper.js step).

MediaTempPreviewView exists because deploy/nginx.conf denies all access
to /media/temp/ outright (CLAUDE.md ch.12 — temp uploads must never be
servable publicly), which broke the crop preview in production: the
browser has to load that exact not-yet-confirmed file to show it inside
Cropper.js. This login-gated view is the replacement for that direct
nginx-served URL.
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse


@pytest.mark.django_db
def test_stage_upload_requires_login(client, sample_image_bytes):
    upload = SimpleUploadedFile('test.jpg', sample_image_bytes(), content_type='image/jpeg')
    response = client.post(reverse('cms:media_upload_stage'), {'file': upload})
    assert response.status_code == 302
    assert '/accounts/login' in response.url


@pytest.mark.django_db
def test_stage_upload_returns_a_login_gated_preview_url_not_the_raw_media_url(admin_client, sample_image_bytes):
    """Regression test: stage_upload() itself returns the raw
    /media/temp/ storage URL, which nginx blocks in production — the
    view must override it with the reversed media_temp_preview URL
    before the JSON reaches the browser."""
    upload = SimpleUploadedFile('test.jpg', sample_image_bytes(), content_type='image/jpeg')

    response = admin_client.post(reverse('cms:media_upload_stage'), {'file': upload})

    assert response.status_code == 200
    data = response.json()
    assert data['url'] == reverse('cms:media_temp_preview', kwargs={'temp_id': data['temp_id']})
    assert '/media/temp/' not in data['url']


@pytest.mark.django_db
def test_temp_preview_requires_login(client):
    response = client.get(reverse('cms:media_temp_preview', kwargs={'temp_id': f'{"a" * 32}.jpg'}))
    assert response.status_code == 302
    assert '/accounts/login' in response.url


@pytest.mark.django_db
def test_temp_preview_serves_a_freshly_staged_file(admin_client, sample_image_bytes):
    upload = SimpleUploadedFile('test.jpg', sample_image_bytes(), content_type='image/jpeg')
    staged = admin_client.post(reverse('cms:media_upload_stage'), {'file': upload}).json()

    response = admin_client.get(staged['url'])

    assert response.status_code == 200
    assert response['Content-Type'] == 'image/jpeg'
    assert b''.join(response.streaming_content) == sample_image_bytes()


@pytest.mark.django_db
def test_temp_preview_404s_for_a_nonexistent_temp_id(admin_client):
    response = admin_client.get(reverse('cms:media_temp_preview', kwargs={'temp_id': f'{"a" * 32}.jpg'}))
    assert response.status_code == 404


@pytest.mark.django_db
@pytest.mark.parametrize('malformed_temp_id', [
    'not-a-uuid.jpg',
    f'{"a" * 32}.exe',
    f'{"A" * 32}.jpg',  # uppercase hex — stage_upload() only ever generates lowercase
    f'{"a" * 31}.jpg',  # one char short of a real uuid4().hex
])
def test_temp_preview_404s_for_a_malformed_id(admin_client, malformed_temp_id):
    """temp_id becomes part of a filesystem path — it must be validated
    against exactly what stage_upload() generates, not merely trusted."""
    response = admin_client.get(reverse('cms:media_temp_preview', kwargs={'temp_id': malformed_temp_id}))
    assert response.status_code == 404


@pytest.mark.django_db
def test_temp_preview_404s_for_a_path_traversal_attempt(admin_client):
    """Values containing '/' can't even be expressed via reverse() for a
    plain <str:temp_id> segment — construct the URL by hand to confirm
    Django's own routing (not just TEMP_ID_PATTERN) also refuses to
    treat this as a match for the view at all."""
    base = reverse('cms:media_upload_stage').rsplit('/', 2)[0]  # .../media/
    response = admin_client.get(f'{base}/muveqqeti/../../../../etc/passwd/')
    assert response.status_code == 404
