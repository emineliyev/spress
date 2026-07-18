import json

from django.contrib import messages
from django.db.models import Count, Max, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.categories.forms import CategoryForm
from apps.categories.models import Category
from apps.core.mixins import StructureManagerRequiredMixin
from apps.core.utils import get_client_ip
from apps.logs.models import ActivityLog

# Article counts should never include soft-deleted articles — otherwise the
# "Xəbər sayı" column (and the delete guard below) would count trashed News
# rows as a reason a category can't be removed.
VISIBLE_NEWS_COUNT = Count('news', filter=Q(news__is_deleted=False))


class CategoryListView(StructureManagerRequiredMixin, ListView):
    """No pagination — matches `CMS Categories.dc.html`, which assumes a
    short, manageable list (CLAUDE.md's two-level hierarchy caps the total
    size naturally, unlike News)."""

    template_name = 'cms/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        self.show_deleted = self.request.GET.get('deleted') == '1'
        top_level = list(
            Category.objects.filter(is_deleted=self.show_deleted, parent__isnull=True)
            .annotate(news_count=VISIBLE_NEWS_COUNT)
            .order_by('order', 'name')
        )

        children = (
            Category.objects.filter(is_deleted=self.show_deleted, parent_id__in=[c.pk for c in top_level])
            .annotate(news_count=VISIBLE_NEWS_COUNT)
            .order_by('order', 'name')
        )
        children_by_parent = {}
        for child in children:
            children_by_parent.setdefault(child.parent_id, []).append(child)
        for parent in top_level:
            parent.visible_children = children_by_parent.get(parent.pk, [])

        return top_level

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['show_deleted'] = self.show_deleted
        return context


class CategoryCreateView(StructureManagerRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'cms/category_form.html'

    def form_valid(self, form):
        siblings = Category.objects.filter(parent=form.instance.parent)
        max_order = siblings.aggregate(Max('order'))['order__max']
        form.instance.order = 0 if max_order is None else max_order + 1

        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.CATEGORY_CREATED,
            description=self.object.name,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Kateqoriya yaradıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:category_list')


class CategoryUpdateView(StructureManagerRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'cms/category_form.html'

    def get_queryset(self):
        return Category.objects.filter(is_deleted=False)

    def form_valid(self, form):
        response = super().form_valid(form)
        ActivityLog.objects.create(
            actor=self.request.user,
            action=ActivityLog.Action.CATEGORY_UPDATED,
            description=self.object.name,
            ip_address=get_client_ip(self.request),
        )
        messages.success(self.request, 'Dəyişikliklər yadda saxlanıldı.')
        return response

    def get_success_url(self):
        return reverse('cms:category_list')


class CategoryDeleteView(StructureManagerRequiredMixin, View):
    """GET renders a confirmation page, POST performs the (soft) delete —
    same split as `NewsDeleteView`. Unlike News, delete is refused outright
    (not just warned about) when the category still has visible articles or
    sub-categories attached, since removing it from `.visible()` would
    silently break their category link/breadcrumb/URL."""

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk, is_deleted=False)
        return render(request, 'cms/category_confirm_delete.html', {
            'category': category,
            'news_count': category.news.filter(is_deleted=False).count(),
            'children_count': category.children.filter(is_deleted=False).count(),
        })

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk, is_deleted=False)
        news_count = category.news.filter(is_deleted=False).count()
        children_count = category.children.filter(is_deleted=False).count()

        if news_count or children_count:
            messages.error(
                request,
                f'"{category.name}" silinmədi — ona bağlı {news_count} xəbər və '
                f'{children_count} alt-kateqoriya var.',
            )
            return redirect('cms:category_list')

        category.is_deleted = True
        category.save(update_fields=['is_deleted'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.CATEGORY_DELETED,
            description=category.name,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{category.name}" silindi.')
        return redirect('cms:category_list')


class CategoryRestoreView(StructureManagerRequiredMixin, View):
    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk, is_deleted=True)
        category.is_deleted = False
        category.save(update_fields=['is_deleted'])
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.CATEGORY_RESTORED,
            description=category.name,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{category.name}" bərpa olundu.')
        return redirect('cms:category_list')


class CategoryPermanentDeleteView(StructureManagerRequiredMixin, View):
    """Only reachable from the "Silinənlər" trash tab — a real, hard
    delete, unlike `CategoryDeleteView`'s soft delete.

    Unlike `NewsPermanentDeleteView`, this can't just delete and let
    Django's FK behavior sort itself out: `News.category` is
    `on_delete=PROTECT` (a `ProtectedError` would surface as a raw 500)
    and `Category.parent` is `on_delete=CASCADE` (a child category would
    silently vanish along with its parent). Both are checked — against
    *every* row, not just visible ones, since a soft-deleted News or
    Category can still hold the reference — and blocked with a clear
    message rather than either failing loudly or cascading quietly.
    """

    def get(self, request, pk):
        category = get_object_or_404(Category, pk=pk, is_deleted=True)
        return render(request, 'cms/category_confirm_permanent_delete.html', {
            'category': category,
            'news_count': category.news.count(),
            'children_count': category.children.count(),
        })

    def post(self, request, pk):
        category = get_object_or_404(Category, pk=pk, is_deleted=True)
        news_count = category.news.count()
        children_count = category.children.count()

        if news_count or children_count:
            messages.error(
                request,
                f'"{category.name}" həmişəlik silinmədi — ona bağlı {news_count} xəbər və '
                f'{children_count} alt-kateqoriya var (silinənlər də daxil). Əvvəlcə onları '
                'həmişəlik silin və ya başqa kateqoriyaya köçürün.',
            )
            return redirect('cms:category_list')

        name = category.name
        category.delete()
        ActivityLog.objects.create(
            actor=request.user,
            action=ActivityLog.Action.CATEGORY_PURGED,
            description=name,
            ip_address=get_client_ip(request),
        )
        messages.success(request, f'"{name}" həmişəlik silindi.')
        return redirect('cms:category_list')


class CategoryReorderView(StructureManagerRequiredMixin, View):
    """AJAX drag-and-drop reorder (CLAUDE.md ch.8 "CMS actions" is a named
    legitimate AJAX use case). Body: `{"parent": null|pk, "order": [pk, ...]}`
    — every pk must belong to that exact sibling group, or the request is
    rejected rather than silently reordering a different group."""

    def post(self, request):
        try:
            payload = json.loads(request.body)
        except (TypeError, ValueError):
            return JsonResponse({'error': 'Yanlış sorğu formatı.'}, status=400)

        parent_id = payload.get('parent')
        ordered_ids = payload.get('order') or []

        categories = list(
            Category.objects.filter(pk__in=ordered_ids, parent_id=parent_id, is_deleted=False)
        )
        if len(categories) != len(ordered_ids):
            return JsonResponse({'error': 'Kateqoriya qrupu uyğun gəlmir.'}, status=400)

        categories_by_id = {category.pk: category for category in categories}
        for index, category_id in enumerate(ordered_ids):
            categories_by_id[int(category_id)].order = index
        Category.objects.bulk_update(categories, ['order'])

        return JsonResponse({'ok': True})
