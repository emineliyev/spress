from django.db import models

from apps.core.models import BaseModel


class Folder(BaseModel):
    """Flat media folder (CLAUDE.md ch.9 "Folder organization").

    Deliberately flat — no parent/children. Categories already own the
    project's one real hierarchy (two levels); giving media folders their
    own nesting isn't asked for by TZ and would be a second, unrelated
    tree to maintain for no current benefit.
    """

    name = models.CharField(max_length=100)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'name']

    def __str__(self):
        return self.name


class MediaFile(BaseModel):
    """Media library entry.

    `file` is the processed result of the upload→crop→optimize→WebP
    pipeline (`apps/media_manager/services.py`) — what the rest of the
    project links to and what gets served. `original_file` is the
    as-uploaded source, kept only so an item can be re-cropped later
    without another quality-losing generation; it's never linked to
    from outside this app. `thumbnail` is a small rendition for grid/
    card contexts (CLAUDE.md ch.9 "Generate thumbnails").

    Rows created before this pipeline existed (Phase 4's direct-upload
    fallback) have `original_file`/`thumbnail` as `NULL` — callers must
    fall back to `file` when `thumbnail` is empty, not assume it's set.
    """

    class Format(models.TextChoices):
        JPEG = 'jpeg', 'JPEG'
        PNG = 'png', 'PNG'
        WEBP = 'webp', 'WebP'
        SVG = 'svg', 'SVG'

    file = models.FileField(upload_to='uploads/%Y/%m/')
    original_file = models.FileField(upload_to='uploads/originals/%Y/%m/', null=True, blank=True)
    thumbnail = models.FileField(upload_to='thumbnails/%Y/%m/', null=True, blank=True)
    folder = models.ForeignKey(Folder, null=True, blank=True, on_delete=models.SET_NULL, related_name='files')

    original_filename = models.CharField(max_length=255)
    width = models.PositiveIntegerField(null=True, blank=True)
    height = models.PositiveIntegerField(null=True, blank=True)
    file_size = models.PositiveIntegerField(help_text='Size in bytes')
    file_format = models.CharField(max_length=10, choices=Format.choices)
    alt_text = models.CharField(max_length=255, blank=True)
    caption = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.original_filename

    @property
    def usage_count(self):
        """Live count across every FK that can point at a MediaFile.

        Not stored (CLAUDE.md ch.10 "Avoid storing derived information")
        — cheap enough for a detail/delete-confirm view, not called from
        the grid listing.
        """
        from apps.advertisements.models import Advertisement
        from apps.news.models import News
        from apps.settings_app.models import SiteSettings

        count = News.objects.filter(featured_image=self).count()
        count += News.objects.filter(og_image=self).count()
        count += Advertisement.objects.filter(banner=self).count()
        settings_obj = SiteSettings.objects.filter(pk=1).first()
        if settings_obj:
            count += int(settings_obj.logo_id == self.pk)
            count += int(settings_obj.favicon_id == self.pk)
        return count
