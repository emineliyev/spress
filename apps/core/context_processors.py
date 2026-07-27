from django.core.cache import cache

from apps.categories.models import Category
from apps.settings_app.models import SiteSettings, SocialLink

# Runs on every single page across the whole site (base.html always
# includes header.html/footer.html) — the highest-frequency repeated
# query in the project, for data (categories, site settings, social
# links) that only ever changes when an editor touches the CMS.
# Invalidated explicitly by apps/core/signals.py, plus
# CategoryReorderView (apps/cms/views/category.py) directly — that one
# uses Category.objects.bulk_update(), which post_save never fires for.
SITE_CONTEXT_CACHE_KEY = 'core:site_context'
SITE_CONTEXT_CACHE_TIMEOUT = 300

# The primary nav row (templates/components/header.html) has no wrap/
# scroll handling — past this many top-level categories, items would
# silently overflow the container's right edge instead of degrading
# gracefully (confirmed empirically: ~12 categories fit at the
# narrowest standard desktop width of 1280px, but that measurement
# didn't yet account for the overflow trigger itself needing room too).
# A fixed count is simpler and more predictable than measuring pixel
# widths at render time (CLAUDE.md ch.8 "JavaScript is responsible for
# interactivity only" — this doesn't need JS at all with a fixed cap).
# Matches today's real category count exactly, so the "Digər
# kateqoriyalar" dropdown only appears once a 9th one is added.
NAV_VISIBLE_CATEGORY_COUNT = 8

# footer.html's "Bölmələr" column stacks one link per line — a separate
# cap from the nav's (bound by row width, not column height), even
# though both default to the same number today. Past this many, the
# rest are reachable via the "Bütün bölmələr →" link to
# CategoryIndexView instead of stacking the footer taller indefinitely.
FOOTER_VISIBLE_CATEGORY_COUNT = 8


def site(request):
    """Global template context: site chrome settings + main navigation.

    Cached across requests in Redis (CLAUDE.md ch.13 "Caching Strategy")
    — every page on the site triggers this, for data that changes only
    when an editor touches Categories, Settings or Social Links in the
    CMS.
    """

    context = cache.get(SITE_CONTEXT_CACHE_KEY)
    if context is None:
        context = _build_site_context()
        cache.set(SITE_CONTEXT_CACHE_KEY, context, SITE_CONTEXT_CACHE_TIMEOUT)
    return context


def _build_site_context():
    main_categories = list(Category.objects.navigable())

    return {
        'site_settings': SiteSettings.get_solo(),
        # The full list — used by CategoryIndexView (apps/categories/views.py)
        # as its own queryset, and kept here in case a future template
        # needs the uncapped set again.
        'main_categories': main_categories,
        'nav_categories': main_categories[:NAV_VISIBLE_CATEGORY_COUNT],
        'nav_overflow_categories': main_categories[NAV_VISIBLE_CATEGORY_COUNT:],
        'footer_categories': main_categories[:FOOTER_VISIBLE_CATEGORY_COUNT],
        'footer_has_more_categories': len(main_categories) > FOOTER_VISIBLE_CATEGORY_COUNT,
        # Already ordered via SocialLink.Meta.ordering — footer.html just
        # iterates it (CLAUDE.md ch.9 "Social Links" — flexible list, not
        # a fixed field per platform). list()'d for the same reason as
        # everything else here: a cached lazy queryset just re-queries on
        # first access later, defeating the point of caching it at all.
        'social_links': list(SocialLink.objects.all()),
    }


def cms_notifications(request):
    """Unread contact-message count for the CMS sidebar badge
    (`templates/cms/base.html`). Scoped to `/cms/` and authenticated
    requests only — the public site never needs this query, unlike
    `site()` above which every page needs."""

    if not request.path.startswith('/cms/') or not request.user.is_authenticated:
        return {}

    from apps.pages.models import ContactMessage

    return {
        'unread_contact_message_count': ContactMessage.objects.filter(
            status=ContactMessage.Status.NEW,
        ).count(),
    }
