from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import News
from .views import HOME_CACHE_KEY


@receiver(post_save, sender=News)
@receiver(post_delete, sender=News)
def invalidate_home_cache(sender, **kwargs):
    """Covers every individual .save()/.delete() call on News — create,
    edit, soft delete, restore, permanent delete, duplicate. Deliberately
    does NOT cover the view-count increment
    (News.objects.filter(pk=...).update(...) in NewsDetailView.get_object)
    — that's a bulk .update(), which Django never routes through signals
    at all, and that's convenient here: busting the homepage cache on
    every single article view would defeat the point of caching it.
    The two other bulk .update() call sites that *do* need this
    (NewsBulkActionView, publish_scheduled) call cache.delete() directly
    instead, since no signal fires for them.
    """

    cache.delete(HOME_CACHE_KEY)
