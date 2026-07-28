from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.urls import reverse

from apps.accounts.forms import ChangePasswordForm
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog


class ChangePasswordView(LoginRequiredMixin, PasswordChangeView):
    """Self-service — any logged-in CMS user can change their own
    password here. Plain `LoginRequiredMixin`, not one of
    apps.core.mixins' role-scoped mixins: every other user-management
    view in apps/cms/views/user.py is Administrator-only because it acts
    on *someone else's* account; this one only ever acts on
    `request.user`, so any authenticated CMS user needs to reach it.

    No email involved, unlike `UserResetPasswordView`/the "forgot
    password" flow (apps/accounts) — old password + new password,
    verified and applied immediately. Works regardless of whether SMTP
    is configured yet (docs/EMAIL_SETUP.md notes that flow 500s without
    it today).
    """

    form_class = ChangePasswordForm
    template_name = 'cms/change_password.html'

    def form_valid(self, form):
        # PasswordChangeView.form_valid() already calls
        # update_session_auth_hash() internally — changing your own
        # password mid-session doesn't log you out.
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.USER_PASSWORD_CHANGED,
            description=self.request.user.get_full_name() or self.request.user.username,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Şifrəniz yeniləndi.')
        return response

    def get_success_url(self):
        return reverse('cms:change_password')
