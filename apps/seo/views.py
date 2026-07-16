from django.http import HttpResponse
from django.urls import reverse


def robots_txt(request):
    """Dynamic, not a static file — so the sitemap URL always matches the
    live domain (CLAUDE.md ch.14 "Robots.txt": generate dynamically, allow
    public content, block CMS/admin/private/temp)."""

    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /cms/',
        'Disallow: /accounts/',
        'Disallow: /media/temp/',
        '',
        f"Sitemap: {request.build_absolute_uri(reverse('seo:sitemap'))}",
    ]
    return HttpResponse('\n'.join(lines), content_type='text/plain')
