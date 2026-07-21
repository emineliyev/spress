from django.db.models import Exists, OuterRef, Prefetch, Q

from apps.categories.models import Category
from apps.news.models import News
from apps.settings_app.models import SiteSettings, SocialLink

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


def site(request):
    """Global template context: site chrome settings + main navigation.

    Cached per-request only (no cross-request caching yet — that is a
    Performance-phase concern, CLAUDE.md ch.13 "Caching Strategy").
    """

    # An empty category (no published articles of its own, and — for a
    # top-level category — none in its subcategories either) is a dead
    # end for a reader, so it's left out of the nav entirely rather than
    # linking to a page that just shows "no articles" (user-requested).
    # `Exists` subqueries keep this to the same 2-query shape as before
    # (one for the top-level list, one for the prefetched children) —
    # no per-category `.exists()` calls, no N+1.
    own_published = News.objects.published().filter(category=OuterRef('pk'))
    visible_children = Prefetch(
        'children',
        queryset=(
            Category.objects.active().visible()
            .annotate(has_news=Exists(own_published))
            .filter(has_news=True)
        ),
    )

    published_here_or_in_children = News.objects.published().filter(
        Q(category=OuterRef('pk')) | Q(category__parent=OuterRef('pk'))
    )
    main_categories = list(
        Category.objects.active().visible().top_level()
        .annotate(has_news=Exists(published_here_or_in_children))
        .filter(has_news=True)
        .prefetch_related(visible_children)
    )

    return {
        'site_settings': SiteSettings.get_solo(),
        # footer.html lists every category (its own "sitemap" column, no
        # overflow concern there) — header.html uses the two split-out
        # values below instead, so the primary nav row never exceeds the
        # width it can actually render without overflowing.
        'main_categories': main_categories,
        'nav_categories': main_categories[:NAV_VISIBLE_CATEGORY_COUNT],
        'nav_overflow_categories': main_categories[NAV_VISIBLE_CATEGORY_COUNT:],
        # Already ordered via SocialLink.Meta.ordering — footer.html just
        # iterates it (CLAUDE.md ch.9 "Social Links" — flexible list, not
        # a fixed field per platform).
        'social_links': SocialLink.objects.all(),
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
