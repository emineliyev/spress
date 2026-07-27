from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.logs.models import ActivityLog
from apps.news.models import News
from apps.news.views import HOME_CACHE_KEY


class Command(BaseCommand):
    help = (
        'Flips due Scheduled articles to Published (CLAUDE.md ch.9 editorial '
        'lifecycle: Draft → Editing → Review → Scheduled Publication → '
        'Published). News.objects.published() only ever matches '
        'status=PUBLISHED — nothing else in the project transitions a '
        'Scheduled article once its published_at time arrives, so this must '
        'run periodically. No Celery Beat schedule is configured yet, so run '
        'this via an external cron in production (see docs/DEPLOYMENT.md), '
        'the same way clean_temp_uploads already is.'
    )

    def handle(self, *args, **options):
        due_articles = list(
            News.objects.filter(
                status=News.Status.SCHEDULED, is_deleted=False, published_at__lte=timezone.now(),
            ).only('pk', 'title')
        )

        if due_articles:
            News.objects.filter(pk__in=[article.pk for article in due_articles]).update(
                status=News.Status.PUBLISHED,
            )
            # A bulk .update() above, not .save() — apps/news/signals.py
            # never sees it, so the homepage cache needs invalidating by
            # hand. This is the one path where staleness matters most:
            # the entire point of this command is a scheduled article
            # becoming visible without anyone touching it, so it should
            # actually appear immediately, not after HOME_CACHE_TIMEOUT.
            cache.delete(HOME_CACHE_KEY)
            for article in due_articles:
                ActivityLog.objects.create(
                    action=ActivityLog.Action.ARTICLE_UPDATED,
                    description=f'{article.title} (planlaşdırılmış nəşr avtomatik icra olundu)',
                )

        self.stdout.write(self.style.SUCCESS(f'Published {len(due_articles)} scheduled article(s).'))
