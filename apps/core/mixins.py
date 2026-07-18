from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class AdministratorRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Restricts a view to Administrators (CLAUDE.md ch.9: user management
    is scoped to Administrators). Superusers always pass — Django's own
    convention, and the only way `createsuperuser`-made accounts (whose
    `role` field defaults to Journalist since it doesn't set custom
    fields) aren't locked out of the very screen that would fix their role.
    """

    def test_func(self):
        user = self.request.user
        return user.is_superuser or user.role == user.Role.ADMINISTRATOR


class StructureManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Categories, Advertisements — Administrator, Baş redaktor, Kontent
    meneceri (`User.can_manage_structure`)."""

    def test_func(self):
        return self.request.user.can_manage_structure


class ContentManagerRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Tags, Pages, SEO overview — everyone except Jurnalist
    (`User.can_manage_content`)."""

    def test_func(self):
        return self.request.user.can_manage_content


class NewsAccessRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """News screens — everyone except Kontent meneceri
    (`User.can_write_news`). Doesn't by itself restrict a Jurnalist to
    only their own articles — that's a per-view queryset/object filter,
    since "can reach the screen" and "can see/edit everything on it" are
    different questions here."""

    def test_func(self):
        return self.request.user.can_write_news
