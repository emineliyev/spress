from django.db import models
from django.urls import reverse
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import BaseModel
from apps.core.utils import generate_unique_slug, sanitize_rich_text_html
from apps.seo.models import SEOFieldsMixin


class Page(SEOFieldsMixin, BaseModel):
    """Static informational page (CLAUDE.md ch.4 "pages/ Static pages")."""

    title = models.CharField(max_length=200)
    # blank=True so PageForm can submit it empty and let save() below
    # auto-generate it — same reasoning as News.slug (apps/news/models.py).
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    content = CKEditor5Field('Content', config_name='default')
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        self.content = sanitize_rich_text_html(self.content)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('pages:detail', kwargs={'slug': self.slug})
