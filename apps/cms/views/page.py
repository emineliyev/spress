from urllib.parse import urlencode

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.mixins import ContentManagerRequiredMixin, FormErrorToastMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog
from apps.pages.forms import PageForm
from apps.pages.models import Page

PAGE_LIST_PER_PAGE = 30


class PageListView(ContentManagerRequiredMixin, ListView):
    template_name = 'cms/page_list.html'
    context_object_name = 'pages'
    paginate_by = PAGE_LIST_PER_PAGE

    def get_queryset(self):
        queryset = Page.objects.all()
        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            queryset = queryset.filter(title__icontains=self.query)
        return queryset.order_by('title')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        if self.query:
            context['query_string'] = urlencode({'q': self.query}) + '&'
        return context


class PageCreateView(FormErrorToastMixin, ContentManagerRequiredMixin, CreateView):
    model = Page
    form_class = PageForm
    template_name = 'cms/page_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.PAGE_CREATED,
            description=self.object.title,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Səhifə yaradıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:page_edit', kwargs={'pk': self.object.pk})


class PageUpdateView(FormErrorToastMixin, ContentManagerRequiredMixin, UpdateView):
    model = Page
    form_class = PageForm
    template_name = 'cms/page_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.PAGE_UPDATED,
            description=self.object.title,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:page_edit', kwargs={'pk': self.object.pk})


class PageDeleteView(ContentManagerRequiredMixin, View):
    """No soft delete (Page has no is_deleted, unlike News/Category) —
    plain hard delete, same shape as TagDeleteView."""

    def get(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        return render(request, 'cms/page_confirm_delete.html', {'page': page})

    def post(self, request, pk):
        page = get_object_or_404(Page, pk=pk)
        title = page.title
        page.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.PAGE_DELETED,
            description=title,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{title}" silindi.')
        return redirect('cms:page_list')
