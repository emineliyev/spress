from django import template

from apps.advertisements.models import Advertisement

register = template.Library()


@register.inclusion_tag('components/advertisement.html')
def ad_slot(position_code, css_class='ad-slot--sidebar'):
    """Renders whichever campaign is currently live for `position_code`
    (one banner per slot — no rotation/carousel; see ARCHITECTURE.md).
    Positions/campaigns are entirely CMS/DB-managed so templates never
    need editing again once a slot exists here (CLAUDE.md ch.9
    "Advertisements should never require template modifications")."""

    ad = Advertisement.objects.active().filter(position__code=position_code).order_by('-created_at').first()
    return {'ad': ad, 'css_class': css_class}
