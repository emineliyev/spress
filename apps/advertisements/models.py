from django.db import models
from django.db.models import Q
from django.utils import timezone

from apps.core.models import BaseModel


class AdPosition(BaseModel):
    """A named banner slot (CLAUDE.md ch.4 "Advertisement → Position").

    Kept as its own model, not a hardcoded choices field, precisely so new
    slots can be added from the CMS/seed data without a template edit
    (CLAUDE.md ch.9 "Advertisements should never require template
    modifications") — templates reference a position by `code` via the
    `{% ad_slot %}` tag, never by editing markup per campaign.
    """

    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=60, unique=True)
    width = models.PositiveIntegerField()
    height = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.width}×{self.height})'


class AdvertisementQuerySet(models.QuerySet):
    def visible(self):
        """Excludes soft-deleted campaigns (CLAUDE.md ch.10 lists
        Advertisements among soft-delete entities)."""
        return self.filter(is_deleted=False)

    def active(self):
        """Currently eligible to actually show — paused/scheduled/expired
        campaigns are excluded (query-time only, same as `News.published()`
        — no Celery Beat schedule exists in this project to flip a stored
        status automatically)."""
        now = timezone.now()
        return self.visible().filter(is_active=True, start_date__lte=now).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=now)
        )


class Advertisement(BaseModel):
    """A banner campaign assigned to one `AdPosition`."""

    STATUS_LABELS = {
        'active': 'Aktiv',
        'scheduled': 'Planlaşdırılıb',
        'paused': 'Dayandırılıb',
        'expired': 'Bitib',
    }

    title = models.CharField(max_length=150)
    position = models.ForeignKey(AdPosition, on_delete=models.PROTECT, related_name='advertisements')
    banner = models.ForeignKey('media_manager.MediaFile', on_delete=models.PROTECT, related_name='+')
    target_url = models.URLField()
    client_name = models.CharField(max_length=150, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    click_count = models.PositiveIntegerField(default=0)

    objects = AdvertisementQuerySet.as_manager()

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def status(self):
        """Computed, not stored (CLAUDE.md ch.10 "Avoid storing derived
        information") — there's no multi-step workflow here to justify a
        real status field (ch.10 "Avoid boolean fields for workflows"
        applies to state machines; this is just a manual on/off toggle
        plus a date range, the same shape as `News.published()`)."""
        now = timezone.now()
        if not self.is_active:
            return 'paused'
        if self.start_date > now:
            return 'scheduled'
        if self.end_date and self.end_date < now:
            return 'expired'
        return 'active'

    def get_status_display(self):
        return self.STATUS_LABELS[self.status]
