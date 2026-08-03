from django.core.cache import cache
from django.db.models import F, Q
from django.utils.http import urlencode
from django.views.generic import DetailView, ListView, TemplateView

from apps.categories.models import Category
from apps.settings_app.models import SiteSettings

from .models import News

POPULAR_NEWS_COUNT = 5
HOME_SECTION_ARTICLES = 3
HERO_SLIDES_COUNT = 5
HERO_SECONDARY_COUNT = 2
LATEST_NEWS_COUNT = 6
BREAKING_TICKER_MAX = 8
BREAKING_TICKER_SECONDS_PER_ITEM = 6
BREAKING_TICKER_MIN_SECONDS = 18
SEARCH_RESULTS_PER_PAGE = 10
SESSION_VIEWED_KEY = 'viewed_articles'
SESSION_VIEWED_MAX = 200

# CLAUDE.md ch.13 "Caching Strategy" lists the homepage as a prime cache
# target — with home_show_all_categories (Phase 34) an admin can put
# dozens of category sections on one page, each costing its own query,
# so the render cost is now uncapped without this. Invalidated
# explicitly (apps/news/signals.py, plus the two places that publish
# articles via a bulk .update() that no signal ever sees:
# NewsBulkActionView and publish_scheduled) rather than relied on to
# expire — TIMEOUT is a backstop for any path that isn't, not the
# primary invalidation mechanism.
HOME_CACHE_KEY = 'news:home:context'
HOME_CACHE_TIMEOUT = 300


class HomeView(TemplateView):
    template_name = 'news/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        home_context = cache.get(HOME_CACHE_KEY)
        if home_context is None:
            home_context = self._build_home_context()
            cache.set(HOME_CACHE_KEY, home_context, HOME_CACHE_TIMEOUT)
        context.update(home_context)
        return context

    def _build_home_context(self):
        published = News.objects.published().select_related('category__parent', 'featured_image')

        # Carousel slides: every featured article, newest first (`published`
        # is already ordered `-published_at` — see News.Meta). No featured
        # article at all still needs *something* in the hero position, so
        # falls back to the single latest article — a 1-slide "carousel"
        # (the template omits prev/next/dots whenever there's only one).
        featured = list(published.filter(is_featured=True)[:HERO_SLIDES_COUNT])
        hero_slides = featured or list(published[:1])
        hero_ids = {article.pk for article in hero_slides}

        hero_secondary = list(published.exclude(pk__in=hero_ids)[:HERO_SECONDARY_COUNT])
        hero_and_secondary_ids = hero_ids | {article.pk for article in hero_secondary}

        # Cross-category, pure reverse-chronological — the actual "Son
        # xəbərlər" feed. Distinct from category_sections below, which are
        # ordered by Category.order (an editorial/nav decision) and so
        # don't reflect what was *just* published (the original complaint
        # this section fixes: a newer article in a lower-ordered category
        # sat visually below an older one in a higher-ordered category).
        # Excludes hero_secondary too (both sit "above the fold" together)
        # but *not* category_sections' own picks below — see there for why.
        latest_news = list(published.exclude(pk__in=hero_and_secondary_ids)[:LATEST_NEWS_COUNT])

        home_settings = SiteSettings.get_solo()
        top_level_categories = Category.objects.active().visible().top_level().order_by('order')
        if not home_settings.home_show_all_categories:
            top_level_categories = top_level_categories[:home_settings.home_category_sections_count]

        # Only hero_slides is excluded here — never hero_secondary or
        # latest_news. home_show_all_categories guarantees every populated
        # category gets its own section; excluding more than the single
        # most-prominent placement risks a small category losing every
        # article it has to some other section and disappearing entirely.
        # A story repeating here and in Latest News (much further up the
        # page) is normal on a news homepage, not a bug.
        category_sections = []
        for category in top_level_categories:
            items = list(
                News.objects.in_category(category)
                .exclude(pk__in=hero_ids)
                .select_related('category__parent', 'featured_image')[:HOME_SECTION_ARTICLES]
            )
            if items:
                category_sections.append({'category': category, 'articles': items})

        breaking_articles = list(News.objects.breaking().select_related('category')[:BREAKING_TICKER_MAX])

        return {
            'breaking_articles': breaking_articles,
            # Constant scroll *speed* regardless of how many headlines are
            # queued — a fixed duration would make 2 headlines crawl by
            # slowly and 8 headlines whip past unreadably fast.
            'breaking_ticker_duration': max(
                BREAKING_TICKER_MIN_SECONDS, len(breaking_articles) * BREAKING_TICKER_SECONDS_PER_ITEM,
            ),
            'hero_slides': hero_slides,
            'hero_secondary': hero_secondary,
            'latest_news': latest_news,
            'category_sections': category_sections,
            'popular_news': list(published.order_by('-view_count')[:POPULAR_NEWS_COUNT]),
        }


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
