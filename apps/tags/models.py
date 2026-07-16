from django.db import models
from django.urls import reverse

from apps.core.models import BaseModel
from apps.core.utils import generate_unique_slug


class Tag(BaseModel):
    name = models.CharField(max_length=60, unique=True)
    # blank=True so TagForm can submit it empty and let save() below
    # auto-generate it — same reasoning as News.slug (apps/news/models.py).
    slug = models.SlugField(max_length=80, unique=True, blank=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = generate_unique_slug(self, self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('tags:detail', kwargs={'slug': self.slug})
