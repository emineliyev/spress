from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.mixins import AdministratorRequiredMixin, FormErrorToastMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog
from apps.settings_app.forms import AboutStatForm
from apps.settings_app.models import AboutStat


class AboutStatListView(AdministratorRequiredMixin, ListView):
    """No pagination/search — same reasoning as SocialLinkListView
    (apps/cms/views/social_link.py): a short, manageable list. Same
    access level too — this is site presentation content, not per-
    article content."""

    model = AboutStat
    template_name = 'cms/about_stat_list.html'
    context_object_name = 'about_stats'


class AboutStatCreateView(FormErrorToastMixin, AdministratorRequiredMixin, CreateView):
    model = AboutStat
    form_class = AboutStatForm
    template_name = 'cms/about_stat_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.ABOUT_STAT_CREATED,
            description=str(self.object),
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Statistika yaradıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:about_stat_list')


class AboutStatUpdateView(FormErrorToastMixin, AdministratorRequiredMixin, UpdateView):
    model = AboutStat
    form_class = AboutStatForm
    template_name = 'cms/about_stat_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.ABOUT_STAT_UPDATED,
            description=str(self.object),
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:about_stat_list')


class AboutStatDeleteView(AdministratorRequiredMixin, View):
    def get(self, request, pk):
        about_stat = get_object_or_404(AboutStat, pk=pk)
        return render(request, 'cms/about_stat_confirm_delete.html', {'about_stat': about_stat})

    def post(self, request, pk):
        about_stat = get_object_or_404(AboutStat, pk=pk)
        description = str(about_stat)
        about_stat.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.ABOUT_STAT_DELETED,
            description=description,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{description}" silindi.')
        return redirect('cms:about_stat_list')
