from django.contrib import messages
from django.urls import reverse
from django.views.generic import UpdateView

from apps.core.mixins import AdministratorRequiredMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog
from apps.settings_app.forms import SiteSettingsForm
from apps.settings_app.models import SiteSettings


class SettingsUpdateView(AdministratorRequiredMixin, UpdateView):
    """Singleton screen — no pk in the URL, `get_object()` always resolves
    to `SiteSettings.get_solo()` (CLAUDE.md ch.9 "Settings"). Same access
    level as user management (`AdministratorRequiredMixin`): site-wide
    branding/contact/social settings are just as sensitive."""

    model = SiteSettings
    form_class = SiteSettingsForm
    template_name = 'cms/settings.html'

    def get_object(self, queryset=None):
        return SiteSettings.get_solo()

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.SETTINGS_UPDATED,
            description='Sayt tənzimləmələri',
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Tənzimləmələr yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:settings_edit')
