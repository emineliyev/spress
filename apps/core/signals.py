from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from apps.categories.models import Category
from apps.settings_app.models import SiteSettings, SocialLink

from .context_processors import SITE_CONTEXT_CACHE_KEY


@receiver(post_save, sender=Category)
@receiver(post_delete, sender=Category)
@receiver(post_save, sender=SiteSettings)
@receiver(post_save, sender=SocialLink)
@receiver(post_delete, sender=SocialLink)
def invalidate_site_context_cache(sender, **kwargs):
    """Covers every individual .save()/.delete() on the three models
    apps.core.context_processors.site() reads. Deliberately does NOT
    cover CategoryReorderView's bulk_update() (apps/cms/views/category.py)
    — Django never routes bulk_update() through signals, same class of
    gap as News's bulk .update() call sites (apps/news/signals.py) — that
    view calls cache.delete() directly instead.
    """

    cache.delete(SITE_CONTEXT_CACHE_KEY)
