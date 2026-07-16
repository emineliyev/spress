from django.contrib.sitemaps.views import sitemap
from django.urls import path

from . import views
from .sitemaps import sitemaps

app_name = 'seo'

urlpatterns = [
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
