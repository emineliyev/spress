from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.mixins import AdministratorRequiredMixin, FormErrorToastMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog
from apps.settings_app.forms import SocialLinkForm
from apps.settings_app.models import SocialLink


class SocialLinkListView(AdministratorRequiredMixin, ListView):
    """No pagination/search — same reasoning as CategoryListView
    (apps/cms/views/category.py): a short, manageable list. Same access
    level as SettingsUpdateView — this is site-wide branding, not
    per-article content."""

    model = SocialLink
    template_name = 'cms/social_link_list.html'
    context_object_name = 'social_links'


class SocialLinkCreateView(FormErrorToastMixin, AdministratorRequiredMixin, CreateView):
    model = SocialLink
    form_class = SocialLinkForm
    template_name = 'cms/social_link_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.SOCIAL_LINK_CREATED,
            description=self.object.get_platform_display(),
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Sosial şəbəkə linki yaradıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:social_link_list')


class SocialLinkUpdateView(FormErrorToastMixin, AdministratorRequiredMixin, UpdateView):
    model = SocialLink
    form_class = SocialLinkForm
    template_name = 'cms/social_link_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.SOCIAL_LINK_UPDATED,
            description=self.object.get_platform_display(),
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:social_link_list')


class SocialLinkDeleteView(AdministratorRequiredMixin, View):
    """Hard delete, no usage-count warning — unlike Tag/MediaFile, a
    SocialLink has no dependent rows anywhere else in the schema."""

    def get(self, request, pk):
        social_link = get_object_or_404(SocialLink, pk=pk)
        return render(request, 'cms/social_link_confirm_delete.html', {'social_link': social_link})

    def post(self, request, pk):
        social_link = get_object_or_404(SocialLink, pk=pk)
        name = social_link.get_platform_display()
        social_link.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.SOCIAL_LINK_DELETED,
            description=name,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{name}" silindi.')
        return redirect('cms:social_link_list')
