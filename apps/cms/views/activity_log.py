from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from apps.logs.models import ActivityLog

ACTIVITY_LOG_PER_PAGE = 20


class ActivityLogListView(LoginRequiredMixin, ListView):
    template_name = 'cms/activity_log.html'
    context_object_name = 'logs'
    paginate_by = ACTIVITY_LOG_PER_PAGE

    def get_queryset(self):
        queryset = ActivityLog.objects.select_related('actor')

        self.actor_id = self.request.GET.get('user', '')
        if self.actor_id:
            queryset = queryset.filter(actor_id=self.actor_id)

        self.action = self.request.GET.get('action', '')
        if self.action:
            queryset = queryset.filter(action=self.action)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['action_choices'] = ActivityLog.Action.choices
        context['selected_action'] = self.action
        context['selected_user'] = self.actor_id
        context['actors'] = (
            get_user_model().objects.filter(pk__in=ActivityLog.objects.values_list('actor_id', flat=True).distinct())
        )
        return context
