import io
import re
import uuid
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, UnidentifiedImageError

from .models import Folder, MediaFile

MAX_UPLOAD_SIZE_BYTES = 15 * 1024 * 1024
ALLOWED_CONTENT_TYPES = {
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
}
MAX_DIMENSION = 2400
THUMBNAIL_WIDTH = 400
WEBP_QUALITY = 82
TEMP_DIR = 'temp'


def _validate_upload(uploaded_file):
    if uploaded_file.size > MAX_UPLOAD_SIZE_BYTES:
        raise ValidationError('Fayl 15MB-dan böyük ola bilməz.')

    content_type = uploaded_file.content_type
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise ValidationError('Yalnız JPEG, PNG, WebP və ya SVG formatları dəstəklənir.')

    if content_type != 'image/svg+xml':
        uploaded_file.seek(0)
        try:
            with Image.open(uploaded_file) as image:
                image.verify()
        except (UnidentifiedImageError, OSError):
            # A declared content-type only says what the browser *claims*
            # the file is (CLAUDE.md ch.12 "Never trust the file extension
            # alone") — bytes that don't actually decode as that format
            # must fail the same friendly way as an outright disallowed
            # type, not bubble up as an unhandled Pillow exception (ch.5
            # "Never expose stack traces to users").
            raise ValidationError('Fayl zədələnib və ya düzgün şəkil formatı deyil.')
        uploaded_file.seek(0)

    return content_type


def stage_upload(uploaded_file):
    """Step 1 of the upload pipeline: validate and park the raw file under
    `media/temp/` so the client can load it into Cropper.js. No DB row yet
    — `temp_id` (the generated filename) is the only handle needed until
    `process_crop()` either commits or discards it.
    """
    content_type = _validate_upload(uploaded_file)
    extension = ALLOWED_CONTENT_TYPES[content_type]
    temp_id = f'{uuid.uuid4().hex}.{extension}'
    saved_path = default_storage.save(f'{TEMP_DIR}/{temp_id}', uploaded_file)

    width = height = None
    if content_type != 'image/svg+xml':
        with default_storage.open(saved_path, 'rb') as opened:
            with Image.open(opened) as image:
                width, height = image.size

    return {
        'temp_id': temp_id,
        'url': default_storage.url(saved_path),
        'width': width,
        'height': height,
        'is_svg': content_type == 'image/svg+xml',
    }


def _resize_to_width(image, max_width):
    if image.width <= max_width:
        return image.copy()
    ratio = max_width / image.width
    return image.resize((max_width, round(image.height * ratio)), Image.LANCZOS)


def process_crop(temp_id, *, crop_box=None, folder_id=None, user, alt_text='', caption='', media_file=None):
    """Step 2: crop (Pillow, using Cropper.js's reported box), resize,
    convert to WebP, generate a thumbnail, store as a `MediaFile`.

    SVGs skip crop/resize/WebP entirely (CLAUDE.md ch.3 "SVG files should
    not be converted") and are stored verbatim.

    If `media_file` is given (the "Əvəz et" / Replace flow), that row is
    updated in place — its pk, and therefore every FK pointing at it,
    survives — instead of a new row being created.
    """
    temp_path = f'{TEMP_DIR}/{temp_id}'
    if not default_storage.exists(temp_path):
        raise ValidationError('Yüklənmiş fayl tapılmadı, səhifəni yeniləyib yenidən cəhd edin.')

    extension = temp_id.rsplit('.', 1)[-1].lower()
    folder = Folder.objects.filter(pk=folder_id).first() if folder_id else None
    instance = media_file or MediaFile()
    instance.folder = folder
    instance.alt_text = alt_text
    instance.caption = caption
    instance.created_by = instance.created_by or user

    with default_storage.open(temp_path, 'rb') as opened:
        raw_bytes = opened.read()

    if extension == 'svg':
        instance.file = ContentFile(raw_bytes, name=temp_id)
        instance.original_file = None
        instance.thumbnail = None
        instance.original_filename = temp_id
        instance.width = None
        instance.height = None
        instance.file_size = len(raw_bytes)
        instance.file_format = MediaFile.Format.SVG
        instance.save()
        default_storage.delete(temp_path)
        return instance

    image = Image.open(io.BytesIO(raw_bytes))
    image.load()
    if image.mode not in ('RGB', 'RGBA'):
        image = image.convert('RGB')

    if crop_box:
        left, top = round(crop_box['x']), round(crop_box['y'])
        right = left + round(crop_box['width'])
        bottom = top + round(crop_box['height'])
        image = image.crop((left, top, right, bottom))

    if max(image.size) > MAX_DIMENSION:
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    main_buffer = io.BytesIO()
    image.save(main_buffer, format='WEBP', quality=WEBP_QUALITY)

    thumbnail_image = _resize_to_width(image, THUMBNAIL_WIDTH)
    thumbnail_buffer = io.BytesIO()
    thumbnail_image.save(thumbnail_buffer, format='WEBP', quality=WEBP_QUALITY)

    base_name = Path(temp_id).stem
    instance.file = ContentFile(main_buffer.getvalue(), name=f'{base_name}.webp')
    instance.thumbnail = ContentFile(thumbnail_buffer.getvalue(), name=f'{base_name}_thumb.webp')
    instance.original_file = ContentFile(raw_bytes, name=temp_id)
    instance.original_filename = temp_id
    instance.width = image.width
    instance.height = image.height
    instance.file_size = main_buffer.tell()
    instance.file_format = MediaFile.Format.WEBP
    instance.save()

    default_storage.delete(temp_path)
    return instance


def delete_media_file(media_file):
    """Deletes a `MediaFile` row and its on-disk files (main/original/
    thumbnail). DB row first, then files (`apps/cms/views/media.py`'s
    `MediaDeleteView` established this order in Phase 10) — a delete
    blocked by a PROTECT relation (e.g. a live ad banner) can't leave
    files gone with the row still pointing at them.
    """
    media_file.delete()
    for field in (media_file.file, media_file.original_file, media_file.thumbnail):
        if field:
            field.delete(save=False)


def _media_ids_referenced_in_html(html):
    """Maps every `<img src="...">` in rich-text HTML back to `MediaFile`
    rows via their stored file path. Inline body images aren't tracked
    by a ForeignKey the way featured_image/og_image are — they're just
    plain URLs inside the saved HTML — so this is the only way to find
    them for cleanup purposes.
    """
    if not html:
        return set()

    media_url_prefix = settings.MEDIA_URL.strip('/') + '/'
    paths = []
    for src in re.findall(r'<img[^>]+src="([^"]+)"', html):
        path = urlparse(src).path.lstrip('/')
        if path.startswith(media_url_prefix):
            path = path[len(media_url_prefix):]
        paths.append(path)

    if not paths:
        return set()
    return set(MediaFile.objects.filter(file__in=paths).values_list('pk', flat=True))


def collect_news_media_ids(article):
    """Every `MediaFile` id potentially exclusively owned by `article` —
    its featured/OG image FKs, any inline body-content image, and any
    per-video cover image (`apps.news.models.NewsVideoCover`, Phase 24).
    Call this *before* deleting the article; the ids are only meaningful
    once paired with `delete_unused_media()` called *after* the article
    is gone (so `MediaFile.usage_count` reflects the post-deletion
    state, not a stale count that still includes this article's own
    reference). Must run before `article.delete()` for another reason
    too here: `NewsVideoCover.news` is `on_delete=CASCADE`, so those
    rows — and the only record of which cover images this article
    used — are gone the moment the article itself is.
    """
    ids = set()
    if article.featured_image_id:
        ids.add(article.featured_image_id)
    if article.og_image_id:
        ids.add(article.og_image_id)
    ids |= _media_ids_referenced_in_html(article.content)
    ids |= set(article.video_covers.values_list('cover_image_id', flat=True))
    return ids


def delete_unused_media(media_ids):
    """Deletes every `MediaFile` in `media_ids` that's now completely
    unused (`usage_count == 0`) — one still used by another article, an
    ad banner, or site settings survives untouched. Returns how many
    were actually deleted, for an activity-log description.
    """
    deleted = 0
    for media_file in MediaFile.objects.filter(pk__in=media_ids):
        if media_file.usage_count == 0:
            delete_media_file(media_file)
            deleted += 1
    return deleted
