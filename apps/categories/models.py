from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel
from apps.core.utils import generate_unique_slug


class CategoryQuerySet(models.QuerySet):
    def active(self):
        return self.filter(is_active=True)

    def visible(self):
        """Excludes soft-deleted rows (CLAUDE.md ch.10 lists Categories among
        soft-delete entities) — independent of `active()`, which is a
        separate "hidden from public nav" toggle, not a trash state."""
        return self.filter(is_deleted=False)

    def top_level(self):
        return self.filter(parent__isnull=True)


class Category(BaseModel):
    """Two-level category hierarchy only (CLAUDE.md ch.4/10 — no deeper nesting)."""

    name = models.CharField(max_length=100)
    # blank=True so CategoryForm can submit it empty and let save() below
    # auto-generate it — same reasoning as News.slug (apps/news/models.py).
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
    )
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)

    objects = CategoryQuerySet.as_manager()

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        ordering = ['order', 'name']
        indexes = [
            models.Index(fields=['parent', 'order']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if self.parent_id and self.parent.parent_id:
            raise ValidationError(
                'Only two levels of categories are supported: a subcategory '
                'cannot itself have a parent that is already a subcategory.'
            )
        if self.parent_id and self.parent_id == self.pk:
            raise ValidationError('A category cannot be its own parent.')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        if self.parent_id:
            return reverse(
                'categories:subcategory_detail',
                kwargs={'category_slug': self.parent.slug, 'subcategory_slug': self.slug},
            )
        return reverse('categories:category_detail', kwargs={'category_slug': self.slug})

    @property
    def breadcrumb_items(self):
        items = []
        if self.parent_id:
            items.append((self.parent.name, self.parent.get_absolute_url()))
        items.append((self.name, None))
        return items
