"""apps.news.management.commands.publish_scheduled — the only mechanism
that ever transitions a Scheduled article to Published. Discovered while
auditing the project before deployment: News.objects.published() only
ever matches status=PUBLISHED, so without this command (run periodically
via cron — see docs/DEPLOYMENT.md) a Scheduled article's published_at
passing does nothing at all; it just sits there forever, never visible
to a public reader.
"""

from datetime import timedelta

import pytest
from django.core.management import call_command
from django.utils import timezone

from apps.logs.models import ActivityLog
from apps.news.models import News


@pytest.mark.django_db
def test_publishes_a_due_scheduled_article(category, administrator):
    article = News.objects.create(
        title='Vaxtı çatmış xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
        status=News.Status.SCHEDULED, published_at=timezone.now() - timedelta(minutes=1),
    )

    call_command('publish_scheduled')

    article.refresh_from_db()
    assert article.status == News.Status.PUBLISHED
    assert ActivityLog.objects.filter(description__icontains=article.title).exists()


@pytest.mark.django_db
def test_leaves_a_not_yet_due_scheduled_article_alone(category, administrator):
    article = News.objects.create(
        title='Gələcək xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
        status=News.Status.SCHEDULED, published_at=timezone.now() + timedelta(hours=1),
    )

    call_command('publish_scheduled')

    article.refresh_from_db()
    assert article.status == News.Status.SCHEDULED


@pytest.mark.django_db
def test_ignores_a_soft_deleted_scheduled_article(category, administrator):
    article = News.objects.create(
        title='Silinmiş planlaşdırılmış xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator, is_deleted=True,
        status=News.Status.SCHEDULED, published_at=timezone.now() - timedelta(minutes=1),
    )

    call_command('publish_scheduled')

    article.refresh_from_db()
    assert article.status == News.Status.SCHEDULED


@pytest.mark.django_db
def test_published_article_becomes_publicly_visible_afterward(client, category, administrator):
    article = News.objects.create(
        title='Artıq görünən xəbər', short_description='d', content='<p>c</p>',
        category=category, author=administrator,
        status=News.Status.SCHEDULED, published_at=timezone.now() - timedelta(minutes=1),
    )

    call_command('publish_scheduled')

    assert article in News.objects.published()


@pytest.mark.django_db
def test_reports_zero_when_nothing_is_due():
    call_command('publish_scheduled')
    assert ActivityLog.objects.count() == 0
