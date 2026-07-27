from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from apps.core.models import BaseModel

HOME_CATEGORY_SECTIONS_MIN = 1
HOME_CATEGORY_SECTIONS_MAX = 8


class SocialLink(BaseModel):
    """A single social-network link (CLAUDE.md ch.9 "Settings" — social
    links, kept flexible per user request rather than one fixed field per
    platform, so an editor can add e.g. Telegram or WhatsApp without a
    code change).

    `platform` is a fixed choice list, not free text — the CMS shouldn't
    require an editor to know or type a CSS icon class name (CLAUDE.md
    ch.9 "must never be designed for technical users only"). `OTHER`
    covers any platform not explicitly listed, with a generic link icon,
    so the feature never hard-blocks an unlisted platform.

    Flat list, no hierarchy — same shape as `Tag`
    (`apps/tags/models.py`), including hard delete (not in CLAUDE.md
    ch.10's soft-delete list; a social link is trivial to re-add).
    """

    class Platform(models.TextChoices):
        FACEBOOK = 'facebook', 'Facebook'
        INSTAGRAM = 'instagram', 'Instagram'
        X = 'x', 'X (Twitter)'
        YOUTUBE = 'youtube', 'YouTube'
        TELEGRAM = 'telegram', 'Telegram'
        WHATSAPP = 'whatsapp', 'WhatsApp'
        LINKEDIN = 'linkedin', 'LinkedIn'
        TIKTOK = 'tiktok', 'TikTok'
        PINTEREST = 'pinterest', 'Pinterest'
        THREADS = 'threads', 'Threads'
        OTHER = 'other', 'Digər'

    # Every value here is confirmed present in static/vendors/bootstrap-
    # icons/bootstrap-icons.css (CLAUDE.md ch.7 "Use Bootstrap Icons
    # only") — not guessed.
    _ICON_CLASSES = {
        Platform.FACEBOOK: 'bi-facebook',
        Platform.INSTAGRAM: 'bi-instagram',
        Platform.X: 'bi-twitter-x',
        Platform.YOUTUBE: 'bi-youtube',
        Platform.TELEGRAM: 'bi-telegram',
        Platform.WHATSAPP: 'bi-whatsapp',
        Platform.LINKEDIN: 'bi-linkedin',
        Platform.TIKTOK: 'bi-tiktok',
        Platform.PINTEREST: 'bi-pinterest',
        Platform.THREADS: 'bi-threads',
        Platform.OTHER: 'bi-link-45deg',
    }

    platform = models.CharField(max_length=20, choices=Platform.choices)
    url = models.URLField()
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return self.get_platform_display()

    @property
    def icon_class(self):
        return self._ICON_CLASSES.get(self.platform, 'bi-link-45deg')


class SiteSettings(BaseModel):
    """Singleton row holding site-wide chrome settings (CLAUDE.md ch.9 "Settings").

    Only the fields needed by the base template (header/footer) are here.
    SMTP, analytics and maintenance-mode fields belong to the CMS Settings
    phase, once there is a form to manage them — adding them now would be
    schema nobody uses yet.
    """

    site_name = models.CharField(max_length=100, default='XəbərPortal')
    logo = models.ForeignKey(
        'media_manager.MediaFile', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    favicon = models.ForeignKey(
        'media_manager.MediaFile', null=True, blank=True, on_delete=models.SET_NULL, related_name='+'
    )
    footer_text = models.CharField(max_length=255, blank=True)
    contact_email = models.EmailField(blank=True)
    contact_phone = models.CharField(max_length=30, blank=True)
    contact_address = models.CharField(max_length=255, blank=True)

    # How many top-level categories HomeView.get_context_data (apps/news/
    # views.py) turns into a section on the homepage — was a hardcoded
    # constant (HOME_CATEGORY_SECTIONS=2) until an admin asked to control
    # it without a code change. Capped at 8, same reasoning as
    # NAV_VISIBLE_CATEGORY_COUNT (apps/core/context_processors.py): a
    # sane upper bound on how much one page reasonably shows, not a hard
    # technical limit. Ignored entirely when home_show_all_categories is
    # True — a separate boolean rather than a "0 means unlimited" sentinel
    # value on this field, so the settings screen reads as an explicit
    # choice instead of a magic number an editor has to already know about.
    home_category_sections_count = models.PositiveSmallIntegerField(
        default=2,
        validators=[
            MinValueValidator(HOME_CATEGORY_SECTIONS_MIN),
            MaxValueValidator(HOME_CATEGORY_SECTIONS_MAX),
        ],
    )
    home_show_all_categories = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Site Settings'
        verbose_name_plural = 'Site Settings'

    def __str__(self):
        return self.site_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def get_solo(cls):
        # select_related so the instance apps.core.context_processors.site()
        # caches in Redis carries logo/favicon already resolved — without
        # it, base.html's site_settings.logo.file.url would still fire a
        # fresh query on every cache *hit*, quietly undermining the point
        # of caching this at all.
        obj, _ = cls.objects.select_related('logo', 'favicon').get_or_create(pk=1)
        return obj
