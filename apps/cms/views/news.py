from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.core.mixins import NewsAccessRequiredMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog
from apps.media_manager.services import collect_news_media_ids, delete_unused_media
from apps.news.forms import NewsForm
from apps.news.models import News
from apps.news.services import sync_video_covers

NEWS_LIST_PER_PAGE = 15


def _scope_to_author(queryset, user):
    """A Jurnalist only ever sees/touches their own articles — every other
    role that can reach these screens at all can reach any article
    (`User.is_senior_editor`, CLAUDE.md ch.9 "Each role has clearly
    defined permissions")."""
    if user.is_senior_editor:
        return queryset
    return queryset.filter(author=user)


class NewsListView(NewsAccessRequiredMixin, ListView):
    template_name = 'cms/news_list.html'
    context_object_name = 'articles'
    paginate_by = NEWS_LIST_PER_PAGE

    def get_queryset(self):
        self.show_deleted = self.request.GET.get('deleted') == '1'
        queryset = News.objects.select_related('category', 'author').filter(is_deleted=self.show_deleted)
        queryset = _scope_to_author(queryset, self.request.user)

        self.category_id = self.request.GET.get('category', '')
        if self.category_id:
            queryset = queryset.filter(category_id=self.category_id)

        self.status = self.request.GET.get('status', '')
        if self.status:
            queryset = queryset.filter(status=self.status)

        self.query = self.request.GET.get('q', '').strip()
        if self.query:
            queryset = queryset.filter(title__icontains=self.query)

        return queryset.order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'show_deleted': self.show_deleted,
            'category_choices': NewsForm._category_choices()[1:],
            'status_choices': News.Status.choices,
            'selected_category': self.category_id,
            'selected_status': self.status,
            'query': self.query,
        })
        return context


class NewsCreateView(NewsAccessRequiredMixin, CreateView):
    model = News
    form_class = NewsForm
    template_name = 'cms/news_form.html'

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.author = self.request.user
        response = super().form_valid(form)
        sync_video_covers(self.object, self.request.POST.get('video_covers_json'))
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.ARTICLE_CREATED,
            description=self.object.title,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Xəbər yaradıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:news_list')


class NewsUpdateView(NewsAccessRequiredMixin, UpdateView):
    model = News
    form_class = NewsForm
    template_name = 'cms/news_form.html'

    def get_queryset(self):
        return _scope_to_author(News.objects.filter(is_deleted=False), self.request.user)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        sync_video_covers(self.object, self.request.POST.get('video_covers_json'))
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.ARTICLE_UPDATED,
            description=self.object.title,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:news_edit', kwargs={'pk': self.object.pk})


class NewsDeleteView(NewsAccessRequiredMixin, View):
    """GET renders a confirmation page, POST performs the (soft) delete.

    A dedicated page rather than a JS modal — the shared Modal component
    doesn't exist yet, and CLAUDE.md ch.9 requires confirmation for
    destructive actions regardless of which UI pattern delivers it.
    """

    def get(self, request, pk):
        article = get_object_or_404(_scope_to_author(News.objects.filter(is_deleted=False), request.user), pk=pk)
        return render(request, 'cms/news_confirm_delete.html', {'article': article})

    def post(self, request, pk):
        article = get_object_or_404(_scope_to_author(News.objects.filter(is_deleted=False), request.user), pk=pk)
        article.is_deleted = True
        article.save(update_fields=['is_deleted'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.ARTICLE_DELETED,
            description=article.title,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{article.title}" silindi.')
        return redirect('cms:news_list')


class NewsPermanentDeleteView(NewsAccessRequiredMixin, View):
    """Only reachable from the "Silinənlər" (trash) tab — a real, hard
    delete, unlike `NewsDeleteView`'s soft delete. This is the one point
    where attached media (featured/OG image, inline body-content images)
    also gets removed: doing that at soft-delete time instead would leave
    a later `NewsRestoreView` restoring an article with broken images,
    since soft-deleted rows are meant to stay fully recoverable
    (CLAUDE.md ch.10 "Deleted records should remain recoverable")."""

    def get(self, request, pk):
        article = get_object_or_404(_scope_to_author(News.objects.filter(is_deleted=True), request.user), pk=pk)
        return render(request, 'cms/news_confirm_permanent_delete.html', {'article': article})

    def post(self, request, pk):
        article = get_object_or_404(_scope_to_author(News.objects.filter(is_deleted=True), request.user), pk=pk)
        title = article.title
        media_ids = collect_news_media_ids(article)

        article.delete()
        deleted_media_count = delete_unused_media(media_ids)

        description = title
        if deleted_media_count:
            description += f' (+ {deleted_media_count} media fayl)'
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.ARTICLE_PURGED,
            description=description,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{title}" həmişəlik silindi.')
        return redirect('cms:news_list')


class NewsRestoreView(NewsAccessRequiredMixin, View):
    def post(self, request, pk):
        article = get_object_or_404(_scope_to_author(News.objects.filter(is_deleted=True), request.user), pk=pk)
        article.is_deleted = False
        article.save(update_fields=['is_deleted'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.ARTICLE_RESTORED,
            description=article.title,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{article.title}" bərpa olundu.')
        return redirect('cms:news_list')


class NewsDuplicateView(NewsAccessRequiredMixin, View):
    def post(self, request, pk):
        original = get_object_or_404(_scope_to_author(News.objects.filter(is_deleted=False), request.user), pk=pk)
        duplicate = News(
            title=f'{original.title} (surət)',
            short_description=original.short_description,
            content=original.content,
            category=original.category,
            author=request.user,
            status=News.Status.DRAFT,
            featured_image=original.featured_image,
            meta_title=original.meta_title,
            meta_description=original.meta_description,
        )
        duplicate.save()
        duplicate.tags.set(original.tags.all())
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.ARTICLE_CREATED,
            description=f'{duplicate.title} (dublikat, mənbə: {original.title})',
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{original.title}" dublikat edildi.')
        return redirect('cms:news_edit', pk=duplicate.pk)


class NewsBulkActionView(NewsAccessRequiredMixin, View):
    ACTION_LABELS = {
        'delete': 'silindi',
        'publish': 'dərc olundu',
        'archive': 'arxivləşdirildi',
    }

    def post(self, request):
        ids = request.POST.getlist('selected')
        action = request.POST.get('bulk_action')

        if not ids or action not in self.ACTION_LABELS:
            messages.error(request, 'Əməliyyat üçün xəbər seçilməyib.')
            return redirect('cms:news_list')

        if action != 'delete' and not request.user.is_senior_editor:
            messages.error(request, 'Bu əməliyyat üçün səlahiyyətiniz yoxdur.')
            return redirect('cms:news_list')

        queryset = _scope_to_author(News.objects.filter(pk__in=ids, is_deleted=False), request.user)
        count = queryset.count()

        if action == 'delete':
            queryset.update(is_deleted=True)
            log_action = ActivityLog.Action.ARTICLE_DELETED
        elif action == 'publish':
            queryset.update(status=News.Status.PUBLISHED, published_at=timezone.now())
            log_action = ActivityLog.Action.ARTICLE_UPDATED
        else:
            queryset.update(status=News.Status.ARCHIVED)
            log_action = ActivityLog.Action.ARTICLE_UPDATED

        ActivityLog.objects.create(
            actor=request.user,
            action=log_action,
            description=f'Kütləvi əməliyyat ({action}): {count} xəbər',
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'{count} xəbər {self.ACTION_LABELS[action]}.')
        return redirect('cms:news_list')
