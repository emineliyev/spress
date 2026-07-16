import uuid
from urllib.parse import urlparse

import bleach
from bleach.css_sanitizer import CSSSanitizer
from django.utils.text import slugify

# Azerbaijani Latin letters that have no ASCII decomposition. Django's
# default slugify(allow_unicode=False) silently drops any character it
# cannot decompose to ASCII, which would mangle almost every slug on a
# site written entirely in Azerbaijani (CLAUDE.md ch.14 "Slug Rules").
# 'İ'/'I' are handled as explicit replacements (not str.lower()) to avoid
# the "Turkish/Azerbaijani dotted-I" locale bug where 'İ'.lower() produces
# a combining-dot artifact instead of a plain ASCII 'i'.
_AZ_TRANSLITERATION = {
    'ə': 'e', 'Ə': 'e',
    'ğ': 'g', 'Ğ': 'g',
    'ı': 'i', 'I': 'i',
    'i': 'i', 'İ': 'i',
    'ö': 'o', 'Ö': 'o',
    'ü': 'u', 'Ü': 'u',
    'ş': 's', 'Ş': 's',
    'ç': 'c', 'Ç': 'c',
}


def az_slugify(value):
    """Slugify Azerbaijani text without losing letters that have no ASCII form."""

    transliterated = ''.join(_AZ_TRANSLITERATION.get(char, char) for char in value)
    return slugify(transliterated, allow_unicode=False)


def generate_unique_slug(instance, value, slug_field_name='slug'):
    """Slugifies `value` into a slug guaranteed unique for `instance`'s
    model and never empty.

    Every `save()` override that auto-generates a slug (News, Page,
    Category, Tag) used to do just `az_slugify(value)` with no further
    checks. Two bugs followed from that: (1) a title with no
    Azerbaijani/ASCII-representable characters (e.g. pasted in another
    script) slugifies to `''`, which then saves as a literal empty slug
    — a broken `/xeber//` URL, and the *next* such title collides with
    it via the unique constraint since `''` is now taken; (2) two
    ordinary titles that happen to produce the same real slug (a common
    thing for a news portal reusing similar headlines) hit the same
    unique constraint, but only at the database `INSERT`, after
    `ModelForm` validation already passed — an unhandled
    `IntegrityError` (CLAUDE.md ch.12 "Never expose stack traces to
    users"), not a friendly validation error. Appending `-2`, `-3`, ...
    on collision, with a short random fallback when slugify itself
    yields nothing, closes both.
    """
    base_slug = az_slugify(value) or uuid.uuid4().hex[:8]
    model = type(instance)
    slug = base_slug
    suffix = 2
    while True:
        queryset = model._default_manager.filter(**{slug_field_name: slug})
        if instance.pk:
            queryset = queryset.exclude(pk=instance.pk)
        if not queryset.exists():
            return slug
        slug = f'{base_slug}-{suffix}'
        suffix += 1


# Only <iframe src> pointed at YouTube's privacy-enhanced domain survives
# sanitization — the CKEditor UI only ever offers a YouTube provider
# (config/settings/base.py's CKEDITOR_5_CONFIGS), but the UI isn't the
# security boundary; this function is (applied in save(), protects every
# write path, not just the form).
_YOUTUBE_IFRAME_HOSTS = {'www.youtube-nocookie.com', 'youtube-nocookie.com'}


def _validate_iframe_attribute(tag, name, value):
    if name != 'src':
        return name in ('allow', 'allowfullscreen', 'loading')
    parsed = urlparse(value)
    return parsed.scheme == 'https' and parsed.hostname in _YOUTUBE_IFRAME_HOSTS


# Mirrors CKEDITOR_5_CONFIGS['default']['toolbar'] (config/settings/base.py)
# — whatever the toolbar can't produce shouldn't be allowed to survive
# save() either (CLAUDE.md ch.12 "CKEditor content must be filtered
# before rendering"). Shared by every model with a CKEditor5Field content
# field (News, Page) — one allow-list, one toolbar config, kept in sync.
# figure/figcaption: CKEditor5's block-image output (ImageCaption +
# ImageStyle, both bundled) — also reused, with figure's class="media", as
# MediaEmbed's own outer wrapper around the custom YouTube provider's
# markup (static/js/cms/ckeditor-youtube-embed.js): with
# mediaEmbed.previewsInData, CKEditor always wraps a provider's returned
# HTML in its own <figure class="media"><div data-oembed-url="...">…
# </div></figure>, regardless of what the provider's html() callback
# returns.
_ALLOWED_TAGS = [
    'p', 'h2', 'h3', 'h4', 'br',
    'strong', 'b', 'em', 'i', 'u',
    'ol', 'ul', 'li', 'blockquote',
    'a', 'img', 'figure', 'figcaption',
    'div', 'iframe',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
]
_ALLOWED_ATTRIBUTES = {
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'width', 'height'],
    'figure': ['class', 'style'],
    'div': ['class', 'data-oembed-url'],
    'iframe': _validate_iframe_attribute,
    '*': ['style'],
}
# 'width'/'aspect-ratio' are for <figure style="width: NN%"> (CKEditor5's
# ImageResize output on the figure wrapper) and <img style="aspect-ratio:
# W/H"> (CKEditor5 stamps this on every inserted image to prevent layout
# shift — CLAUDE.md ch.13 "Images should not cause layout shifts").
_CSS_SANITIZER = CSSSanitizer(allowed_css_properties=['text-align', 'width', 'aspect-ratio'])


def sanitize_rich_text_html(html):
    """Strips anything the CKEditor toolbar can't legitimately produce.

    Applied in each model's `save()`, not just in the form — protects
    every write path (CMS, seed command, future imports) equally.
    """
    return bleach.clean(
        html or '',
        tags=_ALLOWED_TAGS,
        attributes=_ALLOWED_ATTRIBUTES,
        css_sanitizer=_CSS_SANITIZER,
        strip=True,
    )


def get_client_ip(request):
    """Best-effort client IP for security/audit logging (CLAUDE.md ch.12).

    Trusts X-Forwarded-For only because production sits behind Nginx
    (CLAUDE.md ch.3) — a reverse proxy is expected to set it.
    """
    forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_for:
        return forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR')
