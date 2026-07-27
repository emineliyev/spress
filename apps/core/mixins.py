from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin


class FormErrorToastMixin:
    """Adds a toast notification alongside a ModelForm's usual inline
    field errors when validation fails (CLAUDE.md ch.9 "Notifications" —
    every action should give clear feedback). Inline errors alone are
    easy to miss on a long form (the News editor, for instance, prompted
    this — a missing required Category showed its inline error exactly
    as intended, but nothing else on the page signaled that anything had
    gone wrong) — this adds the same visible signal every other CMS
    action already gets for success/failure.

    Placed before the CreateView/UpdateView in the MRO so this
    form_invalid() runs first and still calls super() through to
    Django's own (which re-renders the template with the form's inline
    errors intact) — this only adds a toast, never replaces the
    field-level messages.
    """

    form_error_message = 'Formada xətalar var — bütün məcburi sahələri düzgün doldurun.'

    def form_invalid(self, form):
        messages.error(self.request, self.form_error_message)
        return super().form_invalid(form)


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
