from django.contrib import messages
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.urls import reverse_lazy

from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog

from .forms import LoginForm
from .services import clear_login_failures, is_login_locked_out, register_login_failure


class LoginView(DjangoLoginView):
    """Editorial sign-in (CLAUDE.md ch.12 "must use Django's built-in authentication system").

    Public readers have no accounts (TZ scopes "Users" to CMS roles only) —
    this is the entry point staff use to reach the CMS.
    """

    template_name = 'accounts/login.html'
    authentication_form = LoginForm
    redirect_authenticated_user = True

    def post(self, request, *args, **kwargs):
        # Checked before Django's own auth backend runs at all (CLAUDE.md
        # ch.12 "Brute Force Protection") — a locked-out (IP, username)
        # pair never reaches password verification, not even to fail it
        # again.
        ip_address = get_client_ip(request)
        username = request.POST.get('username', '')
        if username and is_login_locked_out(ip_address, username):
            ActivityLog.objects.create(
                action=ActivityLog.Action.LOGIN_BLOCKED,
                description=f'İstifadəçi adı: {username}',
                ip_address=ip_address,
            )
            form = self.get_form()
            form.add_error(None, 'Həddindən artıq uğursuz giriş cəhdi. Bir neçə dəqiqədən sonra yenidən cəhd edin.')
            return self.render_to_response(self.get_context_data(form=form))
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.get_user()
        clear_login_failures(get_client_ip(self.request), user.get_username())
        messages.success(self.request, f'Xoş gəldiniz, {user.get_full_name() or user.username}.')
        ActivityLog.objects.create(
            actor=user,
            action=ActivityLog.Action.LOGIN_SUCCESS,
            ip_address=get_client_ip(self.request),
        )
        return super().form_valid(form)

    def form_invalid(self, form):
        ip_address = get_client_ip(self.request)
        username = self.request.POST.get('username', '')
        if username:
            register_login_failure(ip_address, username)
        ActivityLog.objects.create(
            action=ActivityLog.Action.LOGIN_FAILED,
            description=f'İstifadəçi adı: {username}',
            ip_address=ip_address,
        )
        return super().form_invalid(form)


class LogoutView(DjangoLogoutView):
    next_page = reverse_lazy('news:home')

    def dispatch(self, request, *args, **kwargs):
        user = request.user if request.user.is_authenticated else None
        response = super().dispatch(request, *args, **kwargs)
        messages.info(request, 'Hesabdan çıxış edildi.')
        if user is not None:
            ActivityLog.objects.create(
                actor=user,
                action=ActivityLog.Action.LOGOUT,
                ip_address=get_client_ip(request),
            )
        return response
