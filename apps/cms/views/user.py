from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.crypto import get_random_string
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.accounts.forms import UserForm
from apps.accounts.services import send_password_setup_email
from apps.core.mixins import AdministratorRequiredMixin, FormErrorToastMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog

User = get_user_model()
USER_LIST_PER_PAGE = 30
# A newly created account gets a real (if unknown) password — see
# apps/accounts/services.py's docstring: PasswordResetForm.get_users()
# silently skips any user with an unusable password, so
# set_unusable_password() here would make the setup email never arrive.
RANDOM_PASSWORD_LENGTH = 32


class UserListView(AdministratorRequiredMixin, ListView):
    template_name = 'cms/user_list.html'
    context_object_name = 'users'
    paginate_by = USER_LIST_PER_PAGE

    def get_queryset(self):
        queryset = User.objects.all()
        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            queryset = queryset.filter(
                Q(username__icontains=self.query)
                | Q(first_name__icontains=self.query)
                | Q(last_name__icontains=self.query)
                | Q(email__icontains=self.query)
            )
        return queryset.order_by('first_name', 'last_name', 'username')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        if self.query:
            context['query_string'] = urlencode({'q': self.query}) + '&'
        return context


class UserCreateView(FormErrorToastMixin, AdministratorRequiredMixin, CreateView):
    model = User
    form_class = UserForm
    template_name = 'cms/user_form.html'

    def form_valid(self, form):
        form.instance.set_password(get_random_string(RANDOM_PASSWORD_LENGTH))
        response = super().form_valid(form)

        send_password_setup_email(self.request, self.object)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.USER_CREATED,
            description=self.object.get_full_name() or self.object.username,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'İstifadəçi yaradıldı, şifrə təyin etmək üçün email göndərildi.')
        return response

    def get_success_url(self):
        return reverse('cms:user_list')


class UserUpdateView(FormErrorToastMixin, AdministratorRequiredMixin, UpdateView):
    model = User
    form_class = UserForm
    template_name = 'cms/user_form.html'

    def form_valid(self, form):
        role_changed = 'role' in form.changed_data
        old_role = self.get_object().get_role_display() if role_changed else None

        response = super().form_valid(form)

        if role_changed:
            ActivityLog.objects.create(
                actor=self.request.user,
                action=ActivityLog.Action.USER_ROLE_CHANGED,
                description=f'{self.object.get_full_name() or self.object.username}: {old_role} → {self.object.get_role_display()}',
                ip_address=get_client_ip(self.request),
            )
        else:
            ActivityLog.objects.create(
                actor=self.request.user,
                action=ActivityLog.Action.USER_UPDATED,
                description=self.object.get_full_name() or self.object.username,
                ip_address=get_client_ip(self.request),
            )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:user_list')


class UserDeactivateView(AdministratorRequiredMixin, View):
    """GET renders a confirmation page, POST performs the deactivation —
    CLAUDE.md ch.9 "Confirmation Dialogs" explicitly lists "Deactivate
    User" among actions that require confirmation. Self-deactivation is
    refused outright (an administrator locking themselves out has no
    recovery path in this UI)."""

    def get(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        return render(request, 'cms/user_confirm_deactivate.html', {'target': target})

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        if target.pk == request.user.pk:
            messages.error(request, 'Öz hesabınızı deaktiv edə bilməzsiniz.')
            return redirect('cms:user_list')

        target.is_active = False
        target.save(update_fields=['is_active'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.USER_DEACTIVATED,
            description=target.get_full_name() or target.username,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{target.get_full_name() or target.username}" deaktiv edildi.')
        return redirect('cms:user_list')


class UserActivateView(AdministratorRequiredMixin, View):
    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        target.is_active = True
        target.save(update_fields=['is_active'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.USER_ACTIVATED,
            description=target.get_full_name() or target.username,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{target.get_full_name() or target.username}" aktivləşdirildi.')
        return redirect('cms:user_list')


class UserDeleteView(AdministratorRequiredMixin, View):
    """Only reachable for an already-deactivated user (`user_list.html`'s
    row menu only shows "Həmişəlik sil" once "Deaktiv et" already has
    been) — mirrors the soft-delete-then-purge two-step every other
    model in the CMS uses (News/Category/Advertisement), even though
    User has no `is_deleted` field of its own to soft-delete with;
    `is_active=False` is that checkpoint here. A real, hard DB delete,
    unlike `UserDeactivateView` — self-deletion is refused for the same
    reason self-deactivation is.

    `News.author` is `on_delete=PROTECT` (unlike every other reference
    to User, which is `SET_NULL` — `ActivityLog.actor`,
    `BaseModel.created_by`/`updated_by` across categories/tags/pages/
    ads/media/social links/settings) — deleting an author outright would
    raise a raw `ProtectedError`, so it's checked and blocked with a
    clear message first instead.
    """

    def get(self, request, pk):
        target = get_object_or_404(User, pk=pk, is_active=False)
        return render(request, 'cms/user_confirm_delete.html', {
            'target': target,
            'article_count': target.articles.count(),
        })

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk, is_active=False)
        if target.pk == request.user.pk:
            messages.error(request, 'Öz hesabınızı silə bilməzsiniz.')
            return redirect('cms:user_list')

        article_count = target.articles.count()
        if article_count:
            messages.error(
                request,
                f'"{target.get_full_name() or target.username}" silinmədi — {article_count} xəbərin müəllifidir. '
                'Əvvəlcə həmin xəbərləri həmişəlik silin və ya başqa müəllifə köçürün.',
            )
            return redirect('cms:user_list')

        name = target.get_full_name() or target.username
        target.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.USER_DELETED,
            description=name,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{name}" həmişəlik silindi.')
        return redirect('cms:user_list')


class UserResetPasswordView(AdministratorRequiredMixin, View):
    """Not destructive — it only sends an email; the target's password
    doesn't change until they follow the link — so no confirm page,
    same reasoning as NewsDuplicateView's plain one-click POST."""

    def post(self, request, pk):
        target = get_object_or_404(User, pk=pk)
        sent = send_password_setup_email(request, target)

        if sent:
            ActivityLog.objects.create(
                actor=request.user,
                action=ActivityLog.Action.USER_PASSWORD_RESET,
                description=target.get_full_name() or target.username,
                ip_address=get_client_ip(request),
            )
            messages.success(request, f'"{target.get_full_name() or target.username}" üçün şifrə sıfırlama linki göndərildi.')
        else:
            messages.error(request, 'Email göndərilmədi — istifadəçinin e-poçt ünvanını yoxlayın.')
        return redirect('cms:user_list')
