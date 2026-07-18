from django.db.models import Exists, OuterRef, Prefetch, Q

from apps.categories.models import Category
from apps.news.models import News
from apps.settings_app.models import SiteSettings, SocialLink


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
    main_categories = (
        Category.objects.active().visible().top_level()
        .annotate(has_news=Exists(published_here_or_in_children))
        .filter(has_news=True)
        .prefetch_related(visible_children)
    )

    return {
        'site_settings': SiteSettings.get_solo(),
        'main_categories': main_categories,
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
