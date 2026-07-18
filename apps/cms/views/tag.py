from urllib.parse import urlencode

from django.contrib import messages
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.mixins import ContentManagerRequiredMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog
from apps.tags.forms import TagForm
from apps.tags.models import Tag

TAG_LIST_PER_PAGE = 30
# Article counts should never include soft-deleted articles (same reasoning
# as apps/cms/views/category.py's VISIBLE_NEWS_COUNT).
VISIBLE_NEWS_COUNT = Count('news', filter=Q(news__is_deleted=False))


class TagListView(ContentManagerRequiredMixin, ListView):
    template_name = 'cms/tag_list.html'
    context_object_name = 'tags'
    paginate_by = TAG_LIST_PER_PAGE

    def get_queryset(self):
        queryset = Tag.objects.annotate(news_count=VISIBLE_NEWS_COUNT)
        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            queryset = queryset.filter(name__icontains=self.query)
        return queryset.order_by('name')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.query
        if self.query:
            context['query_string'] = urlencode({'q': self.query}) + '&'
        return context


class TagCreateView(ContentManagerRequiredMixin, CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'cms/tag_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.TAG_CREATED,
            description=self.object.name,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Etiket yaradıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:tag_list')


class TagUpdateView(ContentManagerRequiredMixin, UpdateView):
    model = Tag
    form_class = TagForm
    template_name = 'cms/tag_form.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.TAG_UPDATED,
            description=self.object.name,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:tag_list')


class TagDeleteView(ContentManagerRequiredMixin, View):
    """Unlike Category, Tag has no PROTECT relation and isn't in CLAUDE.md's
    soft-delete list — a real delete, warned (not blocked) by usage count,
    the same pattern `MediaDeleteView` uses for `MediaFile.usage_count`."""

    def get(self, request, pk):
        tag = get_object_or_404(Tag, pk=pk)
        return render(request, 'cms/tag_confirm_delete.html', {
            'tag': tag,
            'news_count': tag.news.filter(is_deleted=False).count(),
        })

    def post(self, request, pk):
        tag = get_object_or_404(Tag, pk=pk)
        name = tag.name
        tag.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.TAG_DELETED,
            description=name,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{name}" silindi.')
        return redirect('cms:tag_list')


class TagMergeView(ContentManagerRequiredMixin, View):
    """GET renders a target-tag picker, POST reassigns every News row from
    the source tag to the target and removes the source — the only "safe"
    way to retire a tag that's still in active use (CLAUDE.md ch.9:
    "Editors can: Create, Edit, Merge, Delete, Assign")."""

    def get(self, request, pk):
        tag = get_object_or_404(Tag, pk=pk)
        return render(request, 'cms/tag_confirm_merge.html', {
            'tag': tag,
            'news_count': tag.news.filter(is_deleted=False).count(),
            'target_choices': Tag.objects.exclude(pk=pk).order_by('name'),
        })

    def post(self, request, pk):
        source = get_object_or_404(Tag, pk=pk)
        target_id = request.POST.get('target')
        target = get_object_or_404(Tag, pk=target_id) if target_id else None

        if not target or target.pk == source.pk:
            messages.error(request, 'Birləşdirmək üçün fərqli bir etiket seçin.')
            return redirect('cms:tag_merge', pk=pk)

        for article in source.news.all():
            article.tags.add(target)
            article.tags.remove(source)

        source_name = source.name
        source.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.TAG_MERGED,
            description=f'"{source_name}" → "{target.name}"',
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{source_name}" "{target.name}" etiketinə birləşdirildi.')
        return redirect('cms:tag_list')
