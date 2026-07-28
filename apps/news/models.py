from django.conf import settings
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django_ckeditor_5.fields import CKEditor5Field

from apps.core.models import BaseModel
from apps.core.utils import generate_unique_slug, sanitize_rich_text_html
from apps.seo.models import SEOFieldsMixin

WORDS_PER_MINUTE = 200


class NewsQuerySet(models.QuerySet):
    def visible(self):
        """Excludes soft-deleted articles (CLAUDE.md ch.10 "soft deletion")."""
        return self.filter(is_deleted=False)

    def published(self):
        return self.visible().filter(status=News.Status.PUBLISHED, published_at__lte=timezone.now())

    def featured(self):
        return self.published().filter(is_featured=True)

    def breaking(self):
        return self.published().filter(is_breaking=True)

    def in_category(self, category):
        """Published news for a category page.

        A top-level category page also shows news filed directly under
        its subcategories — mirrors how `News.category` intentionally
        has no separate `subcategory` field (see model docstring).
        """
        if category.parent_id is None:
            return self.published().filter(Q(category=category) | Q(category__parent=category))
        return self.published().filter(category=category)


class News(SEOFieldsMixin, BaseModel):
    """Editorial article (CLAUDE.md ch.9 "News Management", TZ "News").

    `category` points at a `Category` of either level. When it has a
    parent, that parent *is* the top-level category for breadcrumbs —
    there is deliberately no separate `subcategory` field, since that
    would duplicate data already reachable via `category.parent`
    (CLAUDE.md ch.10 "Avoid storing derived information").
    """

    class Status(models.TextChoices):
        DRAFT = 'draft', 'Qaralama'
        PENDING_REVIEW = 'pending_review', 'Nəzərdən keçirilir'
        SCHEDULED = 'scheduled', 'Planlaşdırılıb'
        PUBLISHED = 'published', 'Dərc olunub'
        ARCHIVED = 'archived', 'Arxivləşdirilib'

    title = models.CharField(max_length=255)
    # blank=True so the CMS form can submit it empty and let save() below
    # auto-generate it (TZ "Slugs": "Automatically generated... Editable
    # by administrators.") — always non-blank once saved.
    slug = models.SlugField(max_length=280, unique=True, blank=True)
    short_description = models.CharField(max_length=500)
    content = CKEditor5Field('Content', config_name='default')

    category = models.ForeignKey(
        'categories.Category', on_delete=models.PROTECT, related_name='news',
    )
    tags = models.ManyToManyField('tags.Tag', blank=True, related_name='news')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='articles',
    )
    featured_image = models.ForeignKey(
        'media_manager.MediaFile', null=True, blank=True, on_delete=models.SET_NULL, related_name='+',
    )
    related_articles = models.ManyToManyField('self', blank=True)

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.DRAFT, db_index=True)
    is_featured = models.BooleanField(default=False)
    is_breaking = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)
    # Off by default (editor request) — most articles are aggregated/
    # edited by staff rather than individually bylined, so the public
    # byline (templates/news/detail.html) falls back to "Redaksiya"
    # unless this is explicitly checked for a piece worth crediting to
    # its actual author.
    show_author_name = models.BooleanField(default=False)
    published_at = models.DateTimeField(null=True, blank=True, db_index=True)

    view_count = models.PositiveIntegerField(default=0)
    reading_time_minutes = models.PositiveSmallIntegerField(default=1)

    objects = NewsQuerySet.as_manager()

    class Meta:
        verbose_name = 'News'
        verbose_name_plural = 'News'
        ordering = ['-published_at', '-created_at']
        indexes = [
            models.Index(fields=['status', 'published_at']),
            models.Index(fields=['category', 'status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.title)
        self.content = sanitize_rich_text_html(self.content)
        word_count = len(strip_tags(self.content).split())
        self.reading_time_minutes = max(1, round(word_count / WORDS_PER_MINUTE))
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('news:detail', kwargs={'slug': self.slug})

    @property
    def breadcrumb_items(self):
        items = []
        if self.category.parent_id:
            items.append((self.category.parent.name, self.category.parent.get_absolute_url()))
        items.append((self.category.name, self.category.get_absolute_url()))
        items.append((self.title, None))
        return items


class NewsVideoCover(BaseModel):
    """An optional custom thumbnail for one YouTube video embedded inside
    `News.content` (CMS "Video örtükləri" sidebar, `apps/news/services.py`'s
    `sync_video_covers()`).

    Deliberately its own table rather than anything stored on the embed's
    HTML itself: `CKEDITOR_5_CONFIGS` (config/settings/base.py) has no
    General HTML Support plugin enabled, so a custom attribute added to
    the saved markup isn't guaranteed to survive CKEditor5 regenerating
    its editing view from its internal model on the next edit — this
    model sidesteps that entirely by never touching `content` at all.
    The public article page matches a cover to its video by `video_id`
    at render time (apps/news/views.py's `NewsDetailView`,
    static/js/pages/article.js), not by anything embedded in the HTML.
    """

    news = models.ForeignKey(News, on_delete=models.CASCADE, related_name='video_covers')
    video_id = models.CharField(max_length=32)
    cover_image = models.ForeignKey('media_manager.MediaFile', on_delete=models.CASCADE, related_name='+')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['news', 'video_id'], name='unique_news_video_cover'),
        ]

    def __str__(self):
        return f'{self.news.title} — {self.video_id}'
