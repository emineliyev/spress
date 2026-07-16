from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from django.views.generic import TemplateView

from apps.categories.models import Category
from apps.logs.models import ActivityLog
from apps.news.models import News

RECENT_ITEMS_COUNT = 5
TREND_DAYS = 7
TREND_CHART_WIDTH = 640
TREND_CHART_HEIGHT = 160
TREND_CHART_PADDING = 10


class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'cms/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'stats': self._stats(),
            'recent_articles': News.objects.select_related('category', 'author').order_by('-created_at')[:RECENT_ITEMS_COUNT],
            'recent_activity': ActivityLog.objects.select_related('actor')[:RECENT_ITEMS_COUNT],
            'publish_trend': self._publish_trend(),
            'category_distribution': self._category_distribution(),
        })
        return context

    def _stats(self):
        return {
            'total_articles': News.objects.count(),
            'published_articles': News.objects.published().count(),
            'draft_articles': News.objects.filter(status=News.Status.DRAFT).count(),
            'scheduled_articles': News.objects.filter(status=News.Status.SCHEDULED).count(),
            'categories': Category.objects.visible().count(),
            'users': get_user_model().objects.count(),
        }

    def _publish_trend(self):
        """Articles published per day, last 7 days — real data (CLAUDE.md ch.15
        "no placeholder implementations"; we don't track daily page views)."""
        today = timezone.localdate()
        days = [today - timedelta(days=offset) for offset in range(TREND_DAYS - 1, -1, -1)]
        counts = [News.objects.published().filter(published_at__date=day).count() for day in days]
        max_count = max(counts) or 1

        usable_height = TREND_CHART_HEIGHT - 2 * TREND_CHART_PADDING
        step = TREND_CHART_WIDTH / (len(days) - 1) if len(days) > 1 else 0
        points = []
        for index, count in enumerate(counts):
            x = round(index * step)
            y = round(TREND_CHART_HEIGHT - TREND_CHART_PADDING - (count / max_count) * usable_height)
            points.append(f'{x},{y}')

        return {
            'points': ' '.join(points),
            'width': TREND_CHART_WIDTH,
            'height': TREND_CHART_HEIGHT,
            'labels': [day.strftime('%d.%m') for day in days],
            'total': sum(counts),
        }

    def _category_distribution(self):
        published = News.objects.published()
        total = published.count()
        distribution = []
        for category in Category.objects.active().visible().top_level().order_by('order'):
            count = News.objects.in_category(category).count()
            percentage = round(count / total * 100) if total else 0
            distribution.append({'category': category, 'count': count, 'percentage': percentage})
        return distribution
