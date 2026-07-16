import io

import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models import ProtectedError
from PIL import Image

from apps.advertisements.models import AdPosition, Advertisement
from apps.media_manager.models import MediaFile
from apps.media_manager.services import MAX_UPLOAD_SIZE_BYTES, process_crop, stage_upload
from apps.settings_app.models import SiteSettings


def _jpeg_upload(width=800, height=600, size_bytes=None):
    buffer = io.BytesIO()
    Image.new('RGB', (width, height), color=(10, 20, 30)).save(buffer, format='JPEG')
    content = buffer.getvalue()
    upload = SimpleUploadedFile('test.jpg', content, content_type='image/jpeg')
    if size_bytes is not None:
        upload.size = size_bytes
    return upload


@pytest.mark.django_db
def test_stage_upload_accepts_a_real_image():
    result = stage_upload(_jpeg_upload(800, 600))
    assert result['width'] == 800
    assert result['height'] == 600
    assert result['is_svg'] is False


@pytest.mark.django_db
def test_stage_upload_rejects_disallowed_content_type():
    upload = SimpleUploadedFile('test.txt', b'not an image', content_type='text/plain')
    with pytest.raises(ValidationError):
        stage_upload(upload)


@pytest.mark.django_db
def test_stage_upload_rejects_oversized_file():
    upload = _jpeg_upload(size_bytes=MAX_UPLOAD_SIZE_BYTES + 1)
    with pytest.raises(ValidationError):
        stage_upload(upload)


@pytest.mark.django_db
def test_stage_upload_rejects_a_file_with_an_image_extension_but_no_real_image_data():
    """Never trust the file extension/declared content-type alone
    (CLAUDE.md ch.12 "File Upload Security") — Pillow's own `.verify()`
    must reject bytes that just aren't a valid image."""
    upload = SimpleUploadedFile('fake.jpg', b'this is not actually a jpeg', content_type='image/jpeg')
    with pytest.raises(ValidationError):
        stage_upload(upload)


@pytest.mark.django_db
def test_process_crop_converts_to_webp_and_generates_thumbnail(administrator):
    staged = stage_upload(_jpeg_upload(1000, 800))
    media = process_crop(staged['temp_id'], user=administrator)

    assert media.file_format == MediaFile.Format.WEBP
    assert media.thumbnail
    assert media.original_file
    assert media.width == 1000
    assert media.height == 800


@pytest.mark.django_db
def test_process_crop_respects_the_reported_crop_box(administrator):
    staged = stage_upload(_jpeg_upload(1000, 800))
    media = process_crop(
        staged['temp_id'], crop_box={'x': 0, 'y': 0, 'width': 400, 'height': 300}, user=administrator,
    )

    assert media.width == 400
    assert media.height == 300


@pytest.mark.django_db
def test_usage_count_zero_for_a_completely_unused_media_file(media_file):
    assert media_file.usage_count == 0


@pytest.mark.django_db
def test_usage_count_reflects_featured_image_usage(media_file, published_news):
    published_news.featured_image = media_file
    published_news.save()
    assert media_file.usage_count == 1


@pytest.mark.django_db
def test_usage_count_reflects_advertisement_banner_usage(media_file):
    position = AdPosition.objects.create(name='Header', code='header', width=728, height=90)
    Advertisement.objects.create(
        title='Test ad', position=position, banner=media_file, target_url='https://example.com',
    )
    assert media_file.usage_count == 1


@pytest.mark.django_db
def test_usage_count_reflects_site_settings_logo_usage(media_file):
    settings_obj = SiteSettings.get_solo()
    settings_obj.logo = media_file
    settings_obj.save()
    assert media_file.usage_count == 1


@pytest.mark.django_db
def test_advertisement_banner_is_protected_from_direct_media_deletion(media_file):
    position = AdPosition.objects.create(name='Sidebar', code='sidebar', width=300, height=250)
    Advertisement.objects.create(
        title='Protected ad', position=position, banner=media_file, target_url='https://example.com',
    )

    with pytest.raises(ProtectedError):
        media_file.delete()
