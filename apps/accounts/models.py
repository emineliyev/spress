from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Custom auth user with the CMS role attached (CLAUDE.md ch.9 "User Roles")."""

    class Role(models.TextChoices):
        ADMINISTRATOR = 'administrator', 'Administrator'
        EDITOR_IN_CHIEF = 'editor_in_chief', 'Baş redaktor'
        EDITOR = 'editor', 'Redaktor'
        JOURNALIST = 'journalist', 'Jurnalist'
        CONTENT_MANAGER = 'content_manager', 'Kontent meneceri'

    # Role groups behind each permission tier (CLAUDE.md ch.9 "Each role
    # has clearly defined permissions", ch.12 "Every protected action must
    # verify permissions on the server"). Administrator/superuser always
    # passes every check — handled once in `is_administrator`, not
    # repeated in each set below.
    _STRUCTURE_ROLES = {Role.EDITOR_IN_CHIEF, Role.CONTENT_MANAGER}
    _CONTENT_MANAGEMENT_ROLES = {Role.EDITOR_IN_CHIEF, Role.EDITOR, Role.CONTENT_MANAGER}
    _NEWS_WRITER_ROLES = {Role.EDITOR_IN_CHIEF, Role.EDITOR, Role.JOURNALIST}
    _SENIOR_EDITOR_ROLES = {Role.EDITOR_IN_CHIEF, Role.EDITOR}

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.JOURNALIST,
    )
    # Same shape as SiteSettings.contact_phone / ContactMessage.phone —
    # optional, no format validation (international numbers vary).
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return self.get_full_name() or self.username

    @property
    def is_administrator(self):
        return self.is_superuser or self.role == self.Role.ADMINISTRATOR

    @property
    def can_manage_structure(self):
        """Categories, Advertisements — structural/monetization decisions,
        not day-to-day editorial work."""
        return self.is_administrator or self.role in self._STRUCTURE_ROLES

    @property
    def can_manage_content(self):
        """Tags, Pages, SEO overview."""
        return self.is_administrator or self.role in self._CONTENT_MANAGEMENT_ROLES

    @property
    def can_write_news(self):
        """News screens — everyone whose job includes writing articles."""
        return self.is_administrator or self.role in self._NEWS_WRITER_ROLES

    @property
    def is_senior_editor(self):
        """Can edit/publish/delete any article, not just their own — the
        line a plain Journalist doesn't cross (apps/news/forms.py's
        `NewsForm`, apps/cms/views/news.py's ownership checks)."""
        return self.is_administrator or self.role in self._SENIOR_EDITOR_ROLES
