"""
URL configuration for the news_portal project.

Public and CMS routes are added app-by-app as those apps gain views
(CLAUDE.md ch.4 "URL Architecture" — organized per application, never
a single flat file). Django Admin is mounted only in DEBUG as an
internal developer tool for inspecting migrations — it is not the CMS
(CLAUDE.md ch.9 "The CMS is not a customized Django Admin").

Order matters: `apps.news.urls` (home/search/article) and
`apps.pages.urls` are both included at the root. `pages.urls` ends with
a catch-all `<slug:slug>/` for static pages, so it must be included
last — otherwise it would swallow `search/` or any other root path
before the more specific app gets a chance to match it.
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('', include('apps.news.urls')),
    path('category/', include('apps.categories.urls')),
    path('tag/', include('apps.tags.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('cms/', include('apps.cms.urls')),
    # 'reklam-klik/', not 'reklam/' — the latter is reserved for the
    # seeded "advertise with us" Page (apps.pages' root catch-all).
    path('reklam-klik/', include('apps.advertisements.urls')),
    path('', include('apps.seo.urls')),
    # The CKEditor5Widget always reverses 'ck_editor_5_upload_file' when it
    # renders, even though no toolbar button triggers it (config/settings/base.py)
    # — the route must exist or every News editor page 500s.
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('', include('apps.pages.urls')),
]

if settings.DEBUG:
    from django.conf.urls.static import static

    urlpatterns += [
        path('django-admin/', admin.site.urls),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Only used when DEBUG=False — Django shows its own interactive
# traceback page in DEBUG mode regardless of these (CLAUDE.md ch.5
# "Error Handling" — never expose stack traces to users).
handler404 = 'apps.core.views.handler404'
handler500 = 'apps.core.views.handler500'
