from django.http import HttpResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from apps.news.models import News

# Kept separate from apps.news.views.POPULAR_NEWS_COUNT — that constant
# sizes the home page sidebar list; this one sizes a one-row news_card
# grid (3 columns via col-span-4), a different layout with a different
# natural count.
ERROR_PAGE_POPULAR_NEWS_COUNT = 3


def handler404(request, exception):
    """Wired as `handler404` in config/urls.py. Only reached when
    DEBUG=False (CLAUDE.md ch.14 "404 Optimization" — search is already
    global via the header, so this only needs to add popular articles;
    categories come for free from the site() context processor)."""

    context = {
        'popular_news': News.objects.published()
        .select_related('category', 'featured_image')
        .order_by('-view_count')[:ERROR_PAGE_POPULAR_NEWS_COUNT],
    }
    return render(request, 'errors/404.html', context, status=404)


def handler500(request):
    """Wired as `handler500` in config/urls.py. Deliberately does not
    extend base.html or touch the database — a 500 can itself be caused
    by the database being unreachable, and base.html's header/footer
    depend on apps.core.context_processors.site() querying it. Renders
    via render_to_string() with no `request=` argument on purpose:
    django.shortcuts.render() always forwards the request into a
    RequestContext, which runs every configured context processor
    (including that DB query) whether or not the template ends up using
    the result — passing no request skips them entirely. Django's own
    default server_error view follows the same rule, for the same
    reason; this custom view exists only so the page matches the site's
    design language (CLAUDE.md ch.6) instead of Django's unstyled
    fallback."""

    return HttpResponse(render_to_string('errors/500.html'), status=500)


def csrf_failure(request, reason=''):
    """Registered as CSRF_FAILURE_VIEW (config/settings/production.py).
    A CSRF failure is a 403, but Django routes it through this dedicated
    setting instead of handler403 — without this override it falls back
    to Django's built-in unstyled csrf_403.html. This is the one 403 a
    public visitor can realistically trigger (a form, e.g. the contact
    form, submitted from a tab left open past the session/CSRF cookie's
    lifetime) — no public view raises PermissionDenied directly (grep
    confirms every permission mixin in apps/core/mixins.py is CMS-only).
    CMS requests get the existing CMS-styled templates/403.html; public
    requests get the public-styled errors/403.html."""

    template_name = '403.html' if request.path.startswith('/cms/') else 'errors/403.html'
    return render(request, template_name, {'reason': reason}, status=403)
