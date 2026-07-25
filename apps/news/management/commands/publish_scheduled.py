from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.logs.models import ActivityLog
from apps.news.models import News


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
            for article in due_articles:
                ActivityLog.objects.create(
                    action=ActivityLog.Action.ARTICLE_UPDATED,
                    description=f'{article.title} (planlaşdırılmış nəşr avtomatik icra olundu)',
                )

        self.stdout.write(self.style.SUCCESS(f'Published {len(due_articles)} scheduled article(s).'))
