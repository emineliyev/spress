from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'status', 'is_featured', 'is_breaking', 'published_at')
    list_filter = ('status', 'is_featured', 'is_breaking', 'category')
    search_fields = ('title', 'short_description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('category', 'tags', 'author', 'featured_image', 'related_articles')
