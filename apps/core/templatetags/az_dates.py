from django import template
from django.utils import timezone

register = template.Library()

MINUTE = 60
HOUR = 60 * MINUTE
DAY = 24 * HOUR
MONTH = 30 * DAY

_AZ_MONTHS = [
    'yanvar', 'fevral', 'mart', 'aprel', 'may', 'iyun',
    'iyul', 'avqust', 'sentyabr', 'oktyabr', 'noyabr', 'dekabr',
]


@register.filter
def az_timesince(value):
    """Relative time in Azerbaijani ("3 saat əvvəl") without Django's i18n system.

    USE_I18N is off project-wide (CLAUDE.md ch.3 "no i18n architecture"),
    so the built-in `timesince` filter would render English unit words.
    This is a plain string-formatting helper, not a translation
    framework — it belongs in core as a shared utility (ch.4).
    """

    if not value:
        return ''

    delta_seconds = (timezone.now() - value).total_seconds()

    if delta_seconds < MINUTE:
        return 'bir neçə saniyə əvvəl'
    if delta_seconds < HOUR:
        return f'{int(delta_seconds // MINUTE)} dəqiqə əvvəl'
    if delta_seconds < DAY:
        return f'{int(delta_seconds // HOUR)} saat əvvəl'
    if delta_seconds < MONTH:
        return f'{int(delta_seconds // DAY)} gün əvvəl'

    return value.strftime('%d.%m.%Y')


@register.filter
def az_full_date(value):
    """Absolute date+time in Azerbaijani ("15 may 2026, 14:30") — Django's
    own `date:"F"` filter would render the English month name (same
    USE_I18N=False reasoning as az_timesince above)."""

    if not value:
        return ''

    return f'{value.day} {_AZ_MONTHS[value.month - 1]} {value.year}, {value.strftime("%H:%M")}'
