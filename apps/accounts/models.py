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

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.JOURNALIST,
    )

    def __str__(self):
        return self.get_full_name() or self.username
