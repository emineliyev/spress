from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from apps.news.models import News

from .models import Category

CATEGORY_ARTICLES_PER_PAGE = 9
SIDEBAR_POPULAR_COUNT = 5


class CategoryIndexView(ListView):
    """The footer's "Bütün bölmələr" destination (apps.core.context_processors.site's
    FOOTER_VISIBLE_CATEGORY_COUNT cap) — every category that leads
    somewhere for a reader, not just the handful shown directly in the
    nav/footer."""

    template_name = 'categories/category_index.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.navigable()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['breadcrumb_items'] = [('Bölmələr', None)]
        return context


class CategoryDetailView(ListView):
    """Serves both /category/<slug>/ and /category/<slug>/<slug>/ (same template)."""

    template_name = 'categories/category_detail.html'
    context_object_name = 'articles'
    paginate_by = CATEGORY_ARTICLES_PER_PAGE

    def get(self, request, *args, **kwargs):
        self.category = self._resolve_category()
        return super().get(request, *args, **kwargs)

    def _resolve_category(self):
        category_slug = self.kwargs['category_slug']
        subcategory_slug = self.kwargs.get('subcategory_slug')
        if subcategory_slug:
            return get_object_or_404(
                Category.objects.active().visible(), slug=subcategory_slug, parent__slug=category_slug,
            )
        return get_object_or_404(Category.objects.active().visible().top_level(), slug=category_slug)

    def get_queryset(self):
        return News.objects.in_category(self.category).select_related('category', 'featured_image')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = self.category
        context['nav_active_category'] = self.category
        context['popular_news'] = News.objects.published().order_by('-view_count')[:SIDEBAR_POPULAR_COUNT]
        return context
