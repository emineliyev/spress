from django.contrib import admin

from .models import AdPosition, Advertisement


@admin.register(AdPosition)
class AdPositionAdmin(admin.ModelAdmin):
    """No dedicated CMS screen — positions are seed/admin-managed lookup
    data (CLAUDE.md ch.10 "Seed Data... Default advertisement positions"),
    rarely changed. Campaigns (Advertisement) get the full CMS section."""

    list_display = ('name', 'code', 'width', 'height', 'is_active')
    list_filter = ('is_active',)
    prepopulated_fields = {'code': ('name',)}


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ('title', 'position', 'is_active', 'start_date', 'end_date', 'click_count')
    list_filter = ('is_active', 'is_deleted', 'position')
    search_fields = ('title', 'client_name')
