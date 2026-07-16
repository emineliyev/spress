from django.db import models


class SEOFieldsMixin(models.Model):
    """Reusable SEO metadata fields (CLAUDE.md ch.14).

    Mixed into any publicly indexable content model (News now; Page/Category
    once those apps grow content of their own).
    """

    meta_title = models.CharField(max_length=70, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    meta_keywords = models.CharField(max_length=255, blank=True)
    canonical_url = models.URLField(blank=True)
    og_title = models.CharField(max_length=70, blank=True)
    og_description = models.CharField(max_length=200, blank=True)
    og_image = models.ForeignKey(
        'media_manager.MediaFile',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    robots_index = models.BooleanField(default=True)
    robots_follow = models.BooleanField(default=True)

    class Meta:
        abstract = True
