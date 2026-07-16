from django.conf import settings
from django.db import models


class ActivityLog(models.Model):
    """Read-only audit trail (CLAUDE.md ch.9 "Activity Logs" — "Logs are read-only").

    Only the action types this phase actually produces are enumerated
    (login/logout). Article, category and settings actions get their own
    `Action` choices in the phase that starts producing them — additive
    migrations, not upfront guesses. `description` is a plain string
    rather than a GenericForeignKey to a target object: enough for
    login/logout today, and still enough headroom to add a real target
    reference later without touching this schema.
    """

    class Action(models.TextChoices):
        LOGIN_SUCCESS = 'login_success', 'Uğurlu giriş'
        LOGIN_FAILED = 'login_failed', 'Uğursuz giriş cəhdi'
        LOGIN_BLOCKED = 'login_blocked', 'Bloklanmış giriş cəhdi (həddindən artıq cəhd)'
        LOGOUT = 'logout', 'Çıxış'
        ARTICLE_CREATED = 'article_created', 'Xəbər yaratdı'
        ARTICLE_UPDATED = 'article_updated', 'Xəbəri redaktə etdi'
        ARTICLE_DELETED = 'article_deleted', 'Xəbəri sildi'
        ARTICLE_RESTORED = 'article_restored', 'Xəbəri bərpa etdi'
        ARTICLE_PURGED = 'article_purged', 'Xəbəri həmişəlik sildi'
        MEDIA_UPLOADED = 'media_uploaded', 'Fayl yüklədi'
        MEDIA_REPLACED = 'media_replaced', 'Faylı əvəz etdi'
        MEDIA_DELETED = 'media_deleted', 'Faylı sildi'
        CATEGORY_CREATED = 'category_created', 'Kateqoriya yaratdı'
        CATEGORY_UPDATED = 'category_updated', 'Kateqoriyanı redaktə etdi'
        CATEGORY_DELETED = 'category_deleted', 'Kateqoriyanı sildi'
        CATEGORY_RESTORED = 'category_restored', 'Kateqoriyanı bərpa etdi'
        TAG_CREATED = 'tag_created', 'Etiket yaratdı'
        TAG_UPDATED = 'tag_updated', 'Etiketi redaktə etdi'
        TAG_DELETED = 'tag_deleted', 'Etiketi sildi'
        TAG_MERGED = 'tag_merged', 'Etiketləri birləşdirdi'
        FOLDER_CREATED = 'folder_created', 'Qovluq yaratdı'
        FOLDER_RENAMED = 'folder_renamed', 'Qovluğun adını dəyişdi'
        FOLDER_DELETED = 'folder_deleted', 'Qovluğu sildi'
        USER_CREATED = 'user_created', 'İstifadəçi yaratdı'
        USER_UPDATED = 'user_updated', 'İstifadəçini redaktə etdi'
        USER_ROLE_CHANGED = 'user_role_changed', 'İstifadəçinin rolunu dəyişdi'
        USER_ACTIVATED = 'user_activated', 'İstifadəçini aktivləşdirdi'
        USER_DEACTIVATED = 'user_deactivated', 'İstifadəçini deaktiv etdi'
        USER_PASSWORD_RESET = 'user_password_reset', 'Şifrə sıfırlama göndərdi'
        SETTINGS_UPDATED = 'settings_updated', 'Tənzimləmələri yenilədi'
        PAGE_CREATED = 'page_created', 'Səhifə yaratdı'
        PAGE_UPDATED = 'page_updated', 'Səhifəni redaktə etdi'
        PAGE_DELETED = 'page_deleted', 'Səhifəni sildi'
        AD_CREATED = 'ad_created', 'Reklam kampaniyası yaratdı'
        AD_UPDATED = 'ad_updated', 'Reklam kampaniyasını redaktə etdi'
        AD_DELETED = 'ad_deleted', 'Reklam kampaniyasını sildi'
        AD_RESTORED = 'ad_restored', 'Reklam kampaniyasını bərpa etdi'
        SOCIAL_LINK_CREATED = 'social_link_created', 'Sosial şəbəkə linki yaratdı'
        SOCIAL_LINK_UPDATED = 'social_link_updated', 'Sosial şəbəkə linkini redaktə etdi'
        SOCIAL_LINK_DELETED = 'social_link_deleted', 'Sosial şəbəkə linkini sildi'

    actor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text='Null when the action has no known user (e.g. a failed login attempt).',
    )
    action = models.CharField(max_length=30, choices=Action.choices)
    description = models.CharField(max_length=255, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['action', 'created_at']),
        ]

    def __str__(self):
        return f'{self.get_action_display()} — {self.actor or "—"}'
