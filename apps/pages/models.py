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


class ContactMessage(BaseModel):
    """A Contact-form submission (`ContactForm`/`ContactView`), kept in the
    CMS as a real inbox — not just emailed and forgotten — so an editor can
    see what came in and track what's been read (CLAUDE.md ch.10 "Avoid
    boolean fields for workflows... use status values")."""

    class Status(models.TextChoices):
        NEW = 'new', 'Yeni'
        READ = 'read', 'Oxunub'

    name = models.CharField(max_length=120)
    # At least one of email/phone is enforced by ContactForm.clean(), not
    # here — a reply channel is required, but which one is the sender's
    # choice.
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.NEW, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.subject}'
