from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import TemplateView

from apps.news.models import News
from apps.pages.models import Page


class SeoOverviewView(LoginRequiredMixin, TemplateView):
    """Read-only SEO status overview (design/CMS SEO.dc.html).

    Per-article/page meta tags are edited on the article/page's own edit
    form (apps/news/forms.py, apps/pages/forms.py) — this screen only
    reports on the technical SEO surface (sitemap, robots.txt, indexing
    coverage) to avoid a second, duplicate place to edit the same fields.
    """

    template_name = 'cms/seo.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        unindexed_count = (
            News.objects.published().filter(robots_index=False).count()
            + Page.objects.filter(is_published=True, robots_index=False).count()
        )
        context.update({
            'sitemap_url': reverse('seo:sitemap'),
            'robots_url': reverse('seo:robots_txt'),
            'unindexed_count': unindexed_count,
        })
        return context
