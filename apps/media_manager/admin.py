from django.contrib import admin

from .models import Folder, MediaFile


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ('original_filename', 'file_format', 'folder', 'width', 'height', 'file_size', 'created_at')
    list_filter = ('file_format', 'folder')
    search_fields = ('original_filename', 'alt_text', 'caption')


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
