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
