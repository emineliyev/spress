from django.db.models import F, Q
from django.utils.http import urlencode
from django.views.generic import DetailView, ListView, TemplateView

from apps.categories.models import Category

from .models import News

POPULAR_NEWS_COUNT = 5
HOME_CATEGORY_SECTIONS = 2
HOME_SECTION_ARTICLES = 3
BREAKING_TICKER_MAX = 8
BREAKING_TICKER_SECONDS_PER_ITEM = 6
BREAKING_TICKER_MIN_SECONDS = 18
SEARCH_RESULTS_PER_PAGE = 10
SESSION_VIEWED_KEY = 'viewed_articles'
SESSION_VIEWED_MAX = 200


class HomeView(TemplateView):
    template_name = 'news/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        published = News.objects.published().select_related('category', 'featured_image')
        hero = published.filter(is_featured=True).first() or published.first()
        excluded_ids = [hero.pk] if hero else []

        category_sections = []
        for category in Category.objects.active().visible().top_level().order_by('order')[:HOME_CATEGORY_SECTIONS]:
            items = list(
                News.objects.in_category(category)
                .exclude(pk__in=excluded_ids)
                .select_related('category__parent', 'featured_image')[:HOME_SECTION_ARTICLES]
            )
            if items:
                category_sections.append({'category': category, 'articles': items})

        breaking_articles = list(News.objects.breaking().select_related('category')[:BREAKING_TICKER_MAX])

        context.update({
            'breaking_articles': breaking_articles,
            # Constant scroll *speed* regardless of how many headlines are
            # queued — a fixed duration would make 2 headlines crawl by
            # slowly and 8 headlines whip past unreadably fast.
            'breaking_ticker_duration': max(
                BREAKING_TICKER_MIN_SECONDS, len(breaking_articles) * BREAKING_TICKER_SECONDS_PER_ITEM,
            ),
            'hero': hero,
            'category_sections': category_sections,
            'popular_news': published.order_by('-view_count')[:POPULAR_NEWS_COUNT],
        })
        return context


class NewsDetailView(DetailView):
    model = News
    template_name = 'news/detail.html'
    context_object_name = 'article'

    def get_queryset(self):
        base = News.objects.select_related('category__parent', 'author', 'featured_image').prefetch_related('tags')
        if self.request.user.is_authenticated:
            # CMS staff (the only accounts that exist — see Phase 2 ARCHITECTURE.md
            # "Login destination") can preview any non-deleted status via the
            # article's normal public URL — no separate preview URL needed.
            return base.visible()
        return base.published()

    def get_object(self, queryset=None):
        article = super().get_object(queryset)
        viewed = self.request.session.setdefault(SESSION_VIEWED_KEY, [])
        if article.status == News.Status.PUBLISHED and article.pk not in viewed:
            News.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)
            article.view_count += 1
            viewed.append(article.pk)
            self.request.session[SESSION_VIEWED_KEY] = viewed[-SESSION_VIEWED_MAX:]
            self.request.session.modified = True
        return article

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        article = self.object
        related = article.related_articles.published()
        if not related.exists():
            related = News.objects.in_category(article.category).exclude(pk=article.pk)
        context['related_articles'] = related.select_related('category__parent', 'featured_image')[:4]
        context['nav_active_category'] = article.category
        context['video_covers'] = {
            cover.video_id: cover.cover_image.file.url
            for cover in article.video_covers.select_related('cover_image')
        }
        return context


class NewsSearchView(ListView):
    model = News
    template_name = 'news/search_results.html'
    context_object_name = 'results'
    paginate_by = SEARCH_RESULTS_PER_PAGE

    def get_queryset(self):
        self.query = self.request.GET.get('q', '').strip()
        if not self.query:
            return News.objects.none()
        return (
            News.objects.published()
            .filter(
                Q(title__icontains=self.query)
                | Q(short_description__icontains=self.query)
                | Q(content__icontains=self.query)
            )
            .select_related('category__parent', 'featured_image')
            .distinct()
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        if self.query:
            context['query_string'] = urlencode({'q': self.query}) + '&'
        return context
