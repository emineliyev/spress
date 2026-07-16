from django.db.models import F
from django.shortcuts import get_object_or_404, redirect
from django.views import View

from .models import Advertisement


class AdClickView(View):
    """Public, unauthenticated — clicking a banner just counts and
    redirects (CLAUDE.md ch.9 "Click tracking"). No impressions tracking
    (deliberately deferred — see Advertisement docstring/ARCHITECTURE.md)."""

    def get(self, request, pk):
        ad = get_object_or_404(Advertisement, pk=pk, is_deleted=False)
        Advertisement.objects.filter(pk=pk).update(click_count=F('click_count') + 1)
        return redirect(ad.target_url)
