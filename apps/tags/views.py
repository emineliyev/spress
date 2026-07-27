from django.shortcuts import get_object_or_404
from django.views.generic import ListView

from apps.news.models import News

from .models import Tag

TAG_ARTICLES_PER_PAGE = 9


class TagDetailView(ListView):
    template_name = 'tags/tag_detail.html'
    context_object_name = 'articles'
    paginate_by = TAG_ARTICLES_PER_PAGE

    def get(self, request, *args, **kwargs):
        self.tag = get_object_or_404(Tag, slug=self.kwargs['slug'])
        return super().get(request, *args, **kwargs)

    def get_queryset(self):
        return News.objects.published().filter(tags=self.tag).select_related('category__parent', 'featured_image')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tag'] = self.tag
        context['breadcrumb_items'] = [(f'Mövzu: {self.tag.name}', None)]
        return context
