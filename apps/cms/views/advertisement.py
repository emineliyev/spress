from urllib.parse import urlencode

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.advertisements.forms import AdvertisementForm
from apps.advertisements.models import Advertisement
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog

AD_LIST_PER_PAGE = 20


class AdListView(LoginRequiredMixin, ListView):
    template_name = 'cms/ad_list.html'
    context_object_name = 'ads'
    paginate_by = AD_LIST_PER_PAGE

    def get_queryset(self):
        self.show_deleted = self.request.GET.get('deleted') == '1'
        queryset = Advertisement.objects.select_related('position').filter(is_deleted=self.show_deleted)

        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            queryset = queryset.filter(title__icontains=self.query)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        # No per-click log exists (just a running counter on the row), so
        # "this month's clicks" is approximated as the total clicks on
        # campaigns that are live right now, not a true monthly tally.
        clicks_this_month = Advertisement.objects.visible().active().aggregate(
            total=Sum('click_count'),
        )['total'] or 0
        revenue_this_month = Advertisement.objects.visible().filter(
            start_date__gte=month_start,
        ).aggregate(total=Sum('price'))['total'] or 0

        preserved_params = {
            key: value for key, value in (('deleted', '1' if self.show_deleted else ''), ('q', self.query)) if value
        }

        context.update({
            'show_deleted': self.show_deleted,
            'query': self.query,
            'active_count': Advertisement.objects.active().count(),
            'clicks_this_month': clicks_this_month,
            'revenue_this_month': revenue_this_month,
            'query_string': urlencode(preserved_params) + '&' if preserved_params else '',
        })
        return context


class AdCreateView(LoginRequiredMixin, CreateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'cms/ad_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.AD_CREATED,
            description=self.object.title,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Kampaniya yaradıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:ad_edit', kwargs={'pk': self.object.pk})


class AdUpdateView(LoginRequiredMixin, UpdateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'cms/ad_form.html'

    def get_queryset(self):
        return Advertisement.objects.filter(is_deleted=False)

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.AD_UPDATED,
            description=self.object.title,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:ad_edit', kwargs={'pk': self.object.pk})


class AdDeleteView(LoginRequiredMixin, View):
    """Soft delete (CLAUDE.md ch.10 lists Advertisements among soft-delete
    entities) — no dependency guard needed, unlike Category: nothing else
    in the project references an Advertisement."""

    def get(self, request, pk):
        ad = get_object_or_404(Advertisement, pk=pk, is_deleted=False)
        return render(request, 'cms/ad_confirm_delete.html', {'ad': ad})

    def post(self, request, pk):
        ad = get_object_or_404(Advertisement, pk=pk, is_deleted=False)
        ad.is_deleted = True
        ad.save(update_fields=['is_deleted'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.AD_DELETED,
            description=ad.title,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{ad.title}" silindi.')
        return redirect('cms:ad_list')


class AdRestoreView(LoginRequiredMixin, View):
    def post(self, request, pk):
        ad = get_object_or_404(Advertisement, pk=pk, is_deleted=True)
        ad.is_deleted = False
        ad.save(update_fields=['is_deleted'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.AD_RESTORED,
            description=ad.title,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{ad.title}" bərpa olundu.')
        return redirect('cms:ad_list')
