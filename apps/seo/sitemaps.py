from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.categories.models import Category
from apps.news.models import News
from apps.pages.models import Page
from apps.tags.models import Tag


class NewsSitemap(Sitemap):
    changefreq = 'hourly'
    priority = 0.8

    def items(self):
        return News.objects.published()

    def lastmod(self, obj):
        return obj.updated_at


class CategorySitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.6

    def items(self):
        return Category.objects.active().visible()


class TagSitemap(Sitemap):
    """Only tags with at least one published article — an empty tag page
    isn't worth a sitemap entry."""

    changefreq = 'weekly'
    priority = 0.4

    def items(self):
        return Tag.objects.filter(news__in=News.objects.published()).distinct()


class PageSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return Page.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


class StaticSitemap(Sitemap):
    priority = 1.0
    changefreq = 'hourly'

    def items(self):
        return ['news:home']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'news': NewsSitemap,
    'categories': CategorySitemap,
    'tags': TagSitemap,
    'pages': PageSitemap,
    'static': StaticSitemap,
}
