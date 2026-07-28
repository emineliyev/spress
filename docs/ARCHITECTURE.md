# Architecture Decisions — Phase 1 (Project Scaffolding)

This file records decisions made while building the project skeleton that
aren't obvious from reading the code alone, so future work doesn't
re-litigate them (CLAUDE.md ch.15 "Documentation").

## App layout

All 13 applications required by CLAUDE.md ch.4 exist under `apps/` and are
registered in `INSTALLED_APPS`. Apps without a Phase-1 feature
(`advertisements`, `pages`, `cms`, `logs`, `users`) are valid, empty Django
apps — no models yet, not placeholder code. They gain models when the
phase that implements their feature starts.

Each app's `AppConfig.name` is `apps.<name>` (since apps live under the
`apps` package) but `AppConfig.label` is kept as the short name (e.g.
`news`, not `apps_news`) so migrations, the admin, and `related_name`
lookups read the same as if the apps lived at the project root.

## `News.category` — no separate `subcategory` field

`Category` is a two-level self-referential tree (`parent`/`children`).
`News.category` is a single FK that may point at a top-level category or
a subcategory. When it points at a subcategory, `category.parent` *is*
the top-level category for breadcrumbs — there is no second FK, because
that would store the same fact twice (CLAUDE.md ch.10 "Avoid storing
derived information whenever possible").

## `MediaFile` has no `uploaded_by` field

`BaseModel.created_by` already means "who created this record." For
`MediaFile` that is identical in meaning to "uploaded by" — a separate
field would duplicate the same fact (CLAUDE.md ch.10 "Avoid duplicated
fields"). `News.author`, by contrast, stays a distinct field from
`created_by`: an editor can enter an article on behalf of a journalist,
so "who wrote it" and "who created the DB record" are allowed to differ.

## Azerbaijani slugs — `apps.core.utils.az_slugify`

Django's `slugify(allow_unicode=False)` silently **drops** any character
it can't decompose to ASCII. Azerbaijani has seven Latin letters with no
ASCII decomposition (`ə ğ ı İ ö ü ş ç`), so the stock function would
mangle nearly every title on a site that is Azerbaijani-only (CLAUDE.md
ch.3 "Language", ch.14 "Slug Rules"). `apps/core/utils.py` transliterates
those letters first (`ə→e, ğ→g, ı/İ→i, ö→o, ü→u, ş→s, ç→c`) before
calling Django's slugify. `İ`/`I` are replaced as literal characters, not
via `.str.lower()`, to avoid the "Turkish/Azerbaijani dotted-I" Unicode
casing bug (`'İ'.lower()` produces a combining-dot artifact, not a plain
`i`). Every future model that generates slugs from Azerbaijani text
(`News`, `Page`, `Tag` auto-suggestions) should reuse `az_slugify`
instead of calling `slugify` directly.

## `SEOFieldsMixin` lives in `apps/seo`, not `apps/core`

`core` is documented as containing no business logic (CLAUDE.md ch.4). SEO
metadata is a business concern with its own app (`apps/seo`) per the
architecture chapter, so the abstract mixin lives there, not in `core`.
`News` inherits it now; `Page`/`Category` will once those apps have their
own publicly indexable content.

## Django Admin is mounted for development only

`config/urls.py` only adds `django-admin/` when `DEBUG=True`. It exists
purely so a developer can eyeball that migrations and model relationships
work correctly while there is no real CMS yet — CLAUDE.md ch.9 forbids
building the actual CMS on top of Django Admin, it does not forbid having
it available as an internal debugging tool. It must not be relied on, or
exposed, once the real CMS exists; remove or continue to gate it behind
`DEBUG` before production deployment.

## Self-hosted fonts and icons, no CDNs

`design/Design System.dc.html` loads Noto Sans/Noto Serif from Google
Fonts and icons from the Lucide CDN. CLAUDE.md ch.13 prefers self-hosted
fonts, and ch.4 requires vendor assets under `static/vendors/` rather
than pulled from a CDN at runtime, so both were downloaded once and
committed under `static/fonts/` and `static/vendors/bootstrap-icons/`.
Only the `latin` + `latin-ext` Google Fonts subsets were kept — together
they cover the full Azerbaijani alphabet, and the site has no other
language to support.

## Icons: Bootstrap Icons, not Lucide (deviation from the mockups)

The design mockups use Lucide icons throughout. CLAUDE.md ch.7/11
explicitly mandates Bootstrap Icons and forbids mixing icon libraries.
Confirmed with the project owner: **Bootstrap Icons wins** — every icon
in the mockups will be re-implemented with its closest Bootstrap Icons
equivalent when the corresponding templates are built.

## Known gap: Redis / Celery are configured but unverified

`CACHES` and `CELERY_BROKER_URL` point at Redis (`django-redis`), which
is not installed in this local dev environment (no Docker, no native
Windows Redis/Memurai found). Phase 1 has no caching or background-task
feature yet, so this doesn't block anything here — but before any phase
that adds real caching or Celery tasks, Redis needs to be running
locally. Recommended: Docker Desktop (`docker run -p 6379:6379 redis`)
or Memurai for Windows.

## Django / Python versions

Python 3.14.3 (already installed) + Django 6.0.7 — verified compatible
via a clean `pip install` with no dependency conflicts.

---

# Phase 2 (Public Navigation Shell — Homepage + cross-cutting pages)

## Scope decision: "Homepage" became the whole first-click navigation graph

The header/footer that appear on every page link to categories, search,
login, and four static pages. CLAUDE.md forbids `href="#"` and hardcoded
URLs, so Homepage couldn't ship without a working destination for every
one of those links. Phase 2 therefore also shipped: category/subcategory
listing, article detail, tag listing, search, About/Contact/Privacy/Terms,
and editorial login/logout — the minimum set that makes every header/
footer link real. Comments, bookmarks, the newsletter block, Archive,
full JSON-LD/sitemap/robots.txt, and the real advertisement system are
still out of scope (see plan file for the full list); the sidebar ad slot
is a reserved empty `div` sized to prevent layout shift, not a stub.

## `apps.core.utils.az_slugify` reused everywhere; new `az_timesince` filter

`Category`, `Tag`, `News`, `Page` all now auto-generate their slug in
`save()` via the Phase-1 `az_slugify` helper when one isn't supplied.
Relative timestamps ("3 saat əvvəl") needed the same treatment: Django's
built-in `timesince` filter renders English unit words because
`USE_I18N=False` (CLAUDE.md ch.3 — no i18n architecture is allowed, so
translation catalogs are off the table). `apps/core/templatetags/az_dates.py`
implements `az_timesince` as a plain string-formatting filter, not a
translation framework, so it doesn't need `USE_I18N`.

## Self-hosted font paths — CSS is two directories deeper than the fonts

`static/css/base/typography.css` was written with `url('../fonts/...')`,
which resolves to `static/css/fonts/` — one level short. The actual
files live at `static/fonts/`, two levels up from `css/base/`. Caught by
rendering the homepage with Playwright and reading `console --errors`
(12 silent 404s for every font weight) rather than by eyeballing the
CSS. Fixed to `../../fonts/...`. Worth remembering for any other CSS
file nested under `css/<subdir>/` that references top-level `static/`
assets — the relative path depth depends on where the *CSS file* sits,
not where `static/` sits.

## `News.category` still has no `subcategory` field — category pages compensate

Per the Phase-1 decision, `News.category` may point at a top-level
category or a subcategory. `NewsQuerySet.in_category()` (used by both
`HomeView`'s category sections and `CategoryDetailView`) shows a
top-level category page the union of its own articles and its
subcategories' articles, so nothing is lost by not having a redundant
field.

## Contact form email — Celery task, eager in development

`apps/pages/tasks.py:send_contact_email` is a real `@shared_task`,
dispatched with `.delay()` from `ContactView.form_valid()` (CLAUDE.md
ch.13 "Email sending" must not block the request). Since Redis isn't
available locally (Phase-1 known gap), `development.py` sets
`CELERY_TASK_ALWAYS_EAGER = True` — Celery's own documented pattern for
running tasks inline without a broker in dev. `production.py` leaves it
unset, so production dispatches through Redis for real. Verified
end-to-end: form POST → 302 → email text appears in the `runserver`
console (via `EMAIL_BACKEND = console` from Phase 1) with the Celery
"task succeeded" log line.

## View-count de-duplication uses the session, not a new table

`NewsDetailView.get_object()` increments `view_count` via `F('view_count') + 1`
only the first time a given session visits a given article (slug ids
kept in `request.session`, capped at 200 entries). This satisfies
CLAUDE.md ch.14's "prevent obvious duplicate counting" without a new
`ArticleView` audit model — bot filtering, if it's ever needed, is
still a clean addition later since nothing here assumes it won't exist.

## `Page` model — same interim pattern as `SiteSettings`

About/Privacy/Terms are `Page` rows (title, slug, content, SEO fields),
editable only through the dev-only Django Admin until the CMS "Pages"
screen exists — identical reasoning to why `SiteSettings` got a model in
Phase 1 before any settings form existed. `content` is a plain
`TextField` split into paragraphs by `apps.core.utils.split_paragraphs`
(shared with `News.content_paragraphs`), same interim state as article
body text pending the CKEditor phase.

## Login destination

`LOGIN_REDIRECT_URL = 'news:home'` for now — there is no `/cms/` yet.
Update this the moment the CMS dashboard phase lands; searching for
`LOGIN_REDIRECT_URL` in `config/settings/base.py` finds it.

---

# Phase 3 (CMS Dashboard)

## `LOGIN_REDIRECT_URL` now points at `/cms/`

Per the Phase-2 TODO above, `config/settings/base.py` now sets
`LOGIN_REDIRECT_URL = 'cms:dashboard'`. Editorial login lands in the CMS,
not the public homepage.

## Dashboard shows real, computable data only — not the mockup's numbers

`CMS Dashboard.dc.html` shows daily page-view analytics ("▲12% dünənə
görə") and a pending-comments count. Neither exists: we don't track
per-day view history (only a cumulative `News.view_count`), and Comments
are out of scope entirely (`Future Expansion`, ch.11). Rendering those
would mean fabricating numbers — a direct violation of "no placeholder
implementations" (ch.15). The stat-card row instead shows exactly the six
metrics TZ.md lists for the Dashboard (Total/Published/Draft/Scheduled
Articles, Categories, Users), and the "last 7 days" chart plots articles
*published* per day (real, from `News.published_at`) rather than page
views. Quick Actions is omitted outright — its only sensible action
("+ Yeni xəbər") has no destination until CMS News Management exists;
a button to nowhere is worse than no button.

## Sidebar: disabled `<span>`, not disabled `<a>`

Sections that don't exist yet (Xəbərlər, Kateqoriyalar, Media,
İstifadəçilər, Reklam, SEO, Tənzimləmələr) render as non-interactive
`<span aria-disabled="true">` — no `href`, not part of the tab order.
This preserves the full sidebar structure from the mockup (so the CMS's
eventual shape is visible) without a single dead link. "Şərhlər" was
dropped from the sidebar entirely rather than greyed out — unlike the
others it isn't a near-term phase, it's explicitly out of product scope.

## `apps.logs.ActivityLog` — minimal `Action` enum, grows with each producer

Only `login_success` / `login_failed` / `logout` exist as choices —
exactly what this phase logs (`apps/accounts/views.py` `LoginView`/
`LogoutView`). Article/category/settings actions (ch.5's fuller list)
get their own choices added in the phase that starts producing them,
not speculatively now. No `GenericForeignKey` to a target object yet —
`description` (plain text) is enough for auth events; add a real target
reference later without touching this schema if a future phase needs it.
Registered in the dev-only admin as fully read-only (no add/change/
delete permission) per ch.9 "Logs are read-only".

## Fixed a pre-existing bug: `News.Status` / `User.Role` labels were English

Both enums were written in Phase 1/2, before anything rendered
`get_status_display()`/`get_role_display()` in a template. Once the
Dashboard's recent-articles table and topbar role label actually
displayed them, the English choice labels ("Draft", "Published",
"Journalist") surfaced as a real bug on an Azerbaijani-only site
(ch.3). Fixed via `accounts.0002_alter_user_role` and
`news.0002_alter_news_status` — worth checking any *new* `TextChoices`
for the same mistake, since it's invisible until something actually
renders `get_FOO_display()`.

## Known gap: the seeded `admin` superuser has `role=Journalist`

`createsuperuser --noinput` (Phase 1) doesn't prompt for custom fields,
so it took the model default (`Role.JOURNALIST`). Cosmetically wrong in
the topbar ("admin — Jurnalist") but harmless — nothing in this phase
gates behavior on `role` yet. Fix directly in `/django-admin/` or
`manage.py shell` if it bothers you before a demo; a real fix (role
prompt or a management command flag) belongs to whichever future phase
introduces role-gated permissions.

---

# Phase 4 (CMS News Management)

## CKEditor 5, not django-ckeditor's bundled CKEditor 4

The plan called for "CKEditor" per CLAUDE.md ch.3, and `django-ckeditor`
is the obvious package — but installing it prints a Django system-check
warning that its bundled CKEditor 4 is EOL with **unfixed** security
issues (the maintainers' own words). CLAUDE.md ch.15 says "avoid
abandoned libraries" in plain terms, so mid-implementation this swapped
to `django-ckeditor-5` (actively maintained, wraps CKEditor 5). Settings
key is `CKEDITOR_5_CONFIGS` (not `CKEDITOR_CONFIGS`), field is
`django_ckeditor_5.fields.CKEditor5Field`, and — important gotcha — its
widget unconditionally calls `reverse('ck_editor_5_upload_file')` when
it renders, even though our toolbar has no upload button. Skipping
`path('ckeditor5/', include('django_ckeditor_5.urls'))` makes *every*
News editor page 500, not just the unused upload feature.

## Toolbar excludes Images and Videos, not just image upload

The original plan was "image insertion via URL only, no upload button."
In practice CKEditor 5's image plugin in this package is upload-oriented
enough that a clean URL-only mode wasn't there to configure, and
`mediaEmbed` (the URL-based "Videos" option) saves non-standard
`<oembed url="...">` markup that needs a server-side oEmbed resolver to
actually render on the public site — shipping that button would be a
toolbar entry that visibly does nothing. Both are dropped from
`CKEDITOR_5_CONFIGS['default']['toolbar']` until Media Library (images)
and a real embed-rendering pass (video) exist. `apps/news/utils.py`'s
bleach allow-list still permits `img` — harmless to allow now, saves a
config edit when the button returns.

## `apps.news.utils.sanitize_article_html` — bleach, applied in `save()`

CLAUDE.md ch.12: "CKEditor content must be filtered before rendering."
The allow-list is hand-mirrored to the toolbar config (tags the toolbar
can't produce shouldn't survive `save()` either) — the two are meant to
be edited together; a comment in each file points at the other.
`bleach`'s `styles=` kwarg was removed as of bleach 6 in favor of
`css_sanitizer=CSSSanitizer(...)`, which needs `tinycss2` — not pulled
in automatically, added as its own requirements line. Verified against
a real `<script>` + `onclick=` payload posted through the live form: the
script tag and the handler attribute are both gone from what's stored;
only inert text remains.

## `News.slug` gained `blank=True`

`NewsForm` sets `slug` `required=False` so the CMS form can submit it
empty and let `News.save()` auto-generate it (`az_slugify`, unchanged
from Phase 1) — matching TZ "Slugs: automatically generated, editable
by administrators." That alone isn't enough: Django's `ModelForm`
re-validates the constructed instance against the *model* field's own
`blank=False` inside `_post_clean()`, so an empty submission still
failed with "This field is required" until the model field itself
became `blank=True` too. `Category`/`Tag` have the same
auto-slug-if-blank `save()` logic without `blank=True` on their model
fields — harmless today only because nothing exposes them through a
`ModelForm` yet (Django Admin's `prepopulated_fields` fills the input
with JS before submit, so admin never hits this). Apply the same fix
there the moment either gets a CMS form.

## `News.is_deleted` — soft delete, `NewsQuerySet.visible()`

Per CLAUDE.md ch.10 ("Public content should generally use soft
deletion... Articles"). `visible()` filters `is_deleted=False`;
`published()` now builds on `visible()`, so every public view
(`HomeView`, `CategoryDetailView`, `NewsSearchView`,
`NewsQuerySet.in_category()`) got the exclusion for free — none of them
needed a direct edit. `NewsDeleteView`/`NewsRestoreView` just flip the
flag with `update_fields=['is_deleted']`; `NewsBulkActionView` does the
same via a single `.update()` call across selected rows (bypasses
`save()` — fine here since bulk actions only ever touch `status`/
`is_deleted`/`published_at`, never `content` or `slug`).

## Preview reuses the public article URL — no separate preview route

`NewsDetailView.get_queryset()` returns `.visible()` (any non-deleted
status) for authenticated requests and `.published()` for anonymous
ones. Since the only accounts that exist belong to CMS staff (Phase 2
decision), "logged in" and "allowed to preview drafts" are the same
condition — no role check needed. The editor's "Önizləmə" link is just
`article.get_absolute_url()` opened in a new tab; the detail template
shows a dismissible "not published yet" banner keyed off `article.status`.

## Discovered: Django 6 always wraps template loaders in `cached.Loader`

Cost real time mid-phase — edited `news_form.html` and `news_confirm_delete.html`
repeatedly with no visible effect until stumbling on this. In older
Django, `cached.Loader` was only used when `DEBUG=False`; in this
version (confirmed via `engines['django'].engine.template_loaders` in a
shell), it's unconditional — `Engine.__init__` always wraps loaders in
`cached.Loader` regardless of the `debug` flag, and that loader has no
mtime check at all (`django/template/loaders/cached.py`), so a cached
template stays cached for the life of the process. Normally
`runserver`'s autoreloader restarts the whole process on any watched
file change — including templates — which incidentally clears this
cache too. **The dev server in this project had been started with
`--noreload`** (to keep background-process bookkeeping simple), which
disabled that safety net along with Python autoreload. Fix: run
`manage.py runserver` **without** `--noreload` for any session that
touches templates. Static files (CSS/JS) aren't affected — those are
served straight from disk on every request, not through this cache —
only `.html` template edits need the process to actually restart or
autoreload to pick them up.

## Discovered mid-phase: Redis (Memurai) is now running locally

Phase 1 flagged Redis as unavailable, gating cache/Celery testing.
Sessions survived a full `runserver` process restart during this
phase's verification — proof the `django_redis` cache backend
(`SESSION_ENGINE = 'django.contrib.sessions.backends.cache'`) is live,
which is only possible with a working Redis. `Get-Service Memurai`
confirms it's installed and running (Redis-compatible, Windows-native).
The Phase-1 "known gap" is stale — caching and Celery's real async mode
(as opposed to the `CELERY_TASK_ALWAYS_EAGER` dev fallback from Phase 2)
can now actually be exercised and should no longer be assumed broken.

## `curl -F` gotcha hit repeatedly during verification (not a project bug)

Worth recording since it cost real debugging time and will recur:
`curl -F "field=<p>...</p>"` — a value starting with `<` — is
special-cased by curl to mean "read this field's value from the file
named after the `<`", not literal text. It fails with "Failed to
open/read local data" for any HTML-shaped payload (which is exactly
what article content looks like). Use `--form-string "field=value"` for
any text field whose value might start with `<`; reserve plain `-F` for
the actual file-upload field.

# Phase 5 (Media Library)

## Closes the gap Phase 4 deliberately left open

`MediaFile` existed as a metadata schema since Phase 1, but nothing ever
implemented CLAUDE.md ch.3's mandatory pipeline ("Original images should
never be served directly to users" — validate → crop → optimize → WebP
→ thumbnail). Phase 4 shipped a temporary direct-upload workaround
(`featured_image_file`, no crop) to keep the News editor usable. This
phase replaces it with the real pipeline and swaps the News editor's
cover picker over to it — `NewsForm` loses `featured_image_file`, gets
back the real `featured_image` FK it had all along on the model.

## Two-step stage/crop-confirm, not one upload request

Matches the design mockup's actual UX (dropzone → Cropper.js panel →
"Tətbiq et") rather than a single blocking upload+process call.
`stage_upload()` validates and parks the raw file under `media/temp/`
with no DB row yet (`temp_id` — the generated filename — is the only
handle needed). `process_crop()` opens it, applies the crop box
Cropper.js reports, resizes, converts to WebP, generates a thumbnail,
and only then creates the `MediaFile`. SVGs skip crop/resize/WebP
entirely (CLAUDE.md ch.3: "SVG files should not be converted") and are
stored verbatim — the JS widget detects `is_svg` in the stage response
and calls confirm immediately without ever opening the crop modal.

## `media/temp/` cleanup is a management command, not Celery Beat

Abandoned uploads (user picks a file, then never hits "Tətbiq et")
leave orphaned files under `media/temp/`. `clean_temp_uploads` deletes
anything older than 24h. No Celery Beat schedule exists yet in this
project, so this is a manual/cron-driven command for now (CLAUDE.md
ch.4 "Management Commands... Remove temporary files") — noted in the
command's own `help` text so it isn't mistaken for something that runs
itself.

## Crop UI is a modal, not the mockup's persistent 360px column

`CMS Media Manager.dc.html` shows the crop panel as a fixed right-hand
column, always part of the page layout. That only works for the
single-purpose Media Library page — the same crop UI is also needed
inside the News editor's two-column layout (main content + existing
360px sidebar already full of other fields), where a third column
doesn't fit. `templates/cms/partials/media_crop_modal.html` is instead
a shared overlay, included on both pages, driven entirely by
`static/js/cms/media-uploader.js`'s `MediaUploader` class — one crop
pipeline, two call sites (`media-library.js` for the library dropzone
and per-card "Əvəz et", `editor.js`'s `initCoverPicker()` for the News
cover field). Deviation from the mockup's literal placement, not from
its interaction design.

## Mockup's "İxrac formatı" (export format) selector was dropped

The mockup shows WebP/JPG/PNG as a user choice. CLAUDE.md ch.3 "Media
Formats" is unconditional: "Automatically convert: JPEG → WEBP, PNG →
WEBP" — no user override contemplated. `process_crop()` always writes
WebP for raster input; the modal has no format control. Alt text and
caption inputs took that space instead, since `MediaFile.alt_text`/
`caption` existed on the model since Phase 1 with no UI to set them.

## Replace folds into `MediaCropConfirmView`, no separate view/URL

The original plan sketched a distinct `MediaReplaceView` /
`media/<pk>/evez-et/`. Implemented instead as an optional `replace`
POST field on the same crop-confirm endpoint: `process_crop(...,
media_file=existing_instance)` updates that row in place rather than
creating a new one, so the pk — and every FK pointing at it
(`News.featured_image`, future `og_image`/`SiteSettings.logo`) —
survives unchanged. One pipeline, one endpoint, instead of two nearly-
identical code paths. Verified end-to-end: replacing the `MediaFile`
backing a published article's cover updates the public page's `<img>`
src without touching the article row.

## Hard delete, not soft delete, for `MediaFile`

CLAUDE.md ch.10's soft-delete list is "Articles / Pages / Advertisements
/ Categories" — editorial content with its own lifecycle. A `MediaFile`
is a storage-backed resource, not content with a workflow; every FK
that can reference one (`News.featured_image`, `og_image`) is already
`on_delete=SET_NULL`. `MediaDeleteView` hard-deletes the row and calls
`.delete(save=False)` on all three FileFields first (Django doesn't
remove files from storage on model delete). The confirm page surfaces
`MediaFile.usage_count` as a warning when non-zero, but doesn't block
the delete — consistent with "every FK survives as NULL" rather than
inventing a reference-counted guard nothing else in the project has.

## Discovered: `{{ x.some_filefield.url|default:... }}` is not a safe fallback

The plan called for templates to fall back from `thumbnail.url` to
`file.url` when a row predates this pipeline (Phase 4's rows have no
`thumbnail`). The obvious `{{ file.thumbnail.url|default:file.url }}`
crashed every page rendering it with `ValueError: The 'thumbnail'
attribute has no file associated with it` — a 500, not a graceful
fallback. Django's `Variable._resolve_lookup` only swallows lookup
failures silently when the raised exception carries
`silent_variable_failure = True` (true for `ObjectDoesNotExist`, false
for a bare `ValueError`, which is exactly what `FieldFile.url` raises
on an empty field) — so `default` never got a chance to run; the
exception propagated straight through the template render. Fixed by
testing the `FieldFile` itself for truthiness first (`{% if
file.thumbnail %}...{% else %}...{% endif %}`), which only calls
`FieldFile.__bool__` (a cheap `bool(self.name)` check, no `.url`
access, no exception) — applied in `media_grid.html`,
`components/news_card.html`, and the News editor's cover preview.
General lesson: never chain `.url` behind `|default` on a nullable
`FileField` — check the field's truthiness in an `{% if %}` first.

## `window.showToast` exposed from `toast.js`

`static/js/components/toast.js` previously only rendered toasts sourced
from server-rendered Django messages on `DOMContentLoaded`. AJAX
failures (upload/crop/replace errors) need to raise a toast from a
client-side event with no page reload — CLAUDE.md ch.8 bans
`alert()` outright ("Never use browser alert()"). Exposed the existing
`createToast` as `window.showToast(message, type)` rather than building
a second notification mechanism; `media-uploader.js`'s `onError`
callback and `media-library.js`/`editor.js`'s consumers of it both use
this instead of a new one-off.

# Phase 6 (CMS: Kateqoriyalar + Etiketlər)

## `Category` gains `is_deleted` — the same soft-delete shape as `News`

CLAUDE.md ch.10 names Categories explicitly in its soft-delete list.
Added `Category.is_deleted` + `CategoryQuerySet.visible()`, mirroring
`NewsQuerySet.visible()` exactly. Kept independent from the pre-existing
`is_active` (a "hide from public nav" toggle, unrelated to trash state)
— every public call site that filtered `.active()` now filters
`.active().visible()` (`apps/categories/views.py`,
`apps/core/context_processors.py`, `apps/news/views.py`,
`apps/news/forms.py`). The nav's `main_categories` context processor
also switched its `children` prefetch to a filtered `Prefetch(...,
queryset=Category.objects.active().visible())` — previously it
prefetched *all* children unconditionally, so an inactive/deleted
subcategory would have silently kept appearing in the header/footer
dropdowns even though this bug predates this phase.

## `Category.slug` / `Tag.slug` gained `blank=True`

Exactly the gap flagged in the Phase 4 note above ("`Category`/`Tag`
have the same auto-slug-if-blank `save()` logic without `blank=True`...
apply the same fix there the moment either gets a CMS form") — this is
that moment. Same fix as `News.slug`: `ModelForm._post_clean()`
re-validates against the model field's own `blank=False` regardless of
the form field's `required=False`, so both needed the model-level change
too.

## No CMS Tags mockup exists — screen designed from the Categories mockup

`CMS Categories.dc.html` is a real, closely-followed spec. `Tags.dc.html`
turned out to be the **public** tag archive page, not an admin screen —
confirmed by reading it in full before building anything. There is no
`CMS Tags.*` file anywhere in `design/`. `templates/cms/tag_list.html`
mirrors the Categories screen's shell/table/button/⋯-menu conventions
(same `cms-table`, `cms-list-toolbar`, `cms-row-menu` classes) minus the
hierarchy/drag-reorder parts, since tags are flat — the closest
consistent choice available, not a guess at an unseen design.

## Category `order` is drag-and-drop only, not a form field

Removed from `CategoryForm.Meta.fields` entirely — new categories get
`order = max(sibling.order) + 1` automatically
(`CategoryCreateView.form_valid`). The only way to change it is the
native HTML5 drag-and-drop in `static/js/cms/categories.js`, matching
CLAUDE.md's "Category ordering is managed manually" and the mockup's
`grip-vertical` handles on top-level rows (child rows are draggable too,
just without the visible handle — the mockup only had one example
subcategory to show, not a deliberate "children can't reorder" choice).
A vanilla `dragstart`/`dragover`/`drop` implementation, no library —
reordering is scoped to a sibling group (`data-parent` must match
between dragged and target rows) and, when a top-level row with children
is dragged, its child rows move as one block immediately after it so the
DOM's parent→children grouping survives the move. `CategoryReorderView`
re-validates group membership server-side from the posted pk list before
calling `bulk_update` — a client that fabricates a request naming pks
outside the claimed group gets a 400, not a silent cross-group reorder.

## Category delete is blocked outright, not soft-warned

Unlike `MediaFile.usage_count` (Phase 5's pattern — warn, don't block),
`CategoryDeleteView` refuses the delete entirely when the category still
has visible news or child categories attached, returning a
`messages.error` instead of flipping `is_deleted`. Reasoning: once
`.visible()` filtering rolled out to every public category query this
phase, a soft-deleted category with articles still pointing at it would
break their category link, breadcrumb, and category-page URL — Category
isn't a standalone resource like `MediaFile` (whose references are all
`on_delete=SET_NULL`), it's load-bearing for News's `on_delete=PROTECT`
FK. `Tag` has no such constraint (`News.tags` is a plain M2M), so
`TagDeleteView` keeps the Phase-5-style warn-not-block pattern.

## Tag merge — CLAUDE.md-mandated, no prior precedent in the codebase

CLAUDE.md ch.9: "Editors can: Create, Edit, **Merge**, Delete, Assign."
`TagMergeView` GET renders a target-tag `<select>` (all tags except the
source), POST reassigns every `News` row from source to target via the
M2M (`article.tags.add(target); article.tags.remove(source)` per row —
`NewsDuplicateView`'s `.tags.set(...)` was the only prior M2M-tag code
to draw from, but merge needed per-row add/remove instead of a blanket
`.set()`), then hard-deletes the source tag. Verified via Django's test
`Client` rather than Playwright for this one — the browser run's own
`Promise.all(waitForNavigation + click)` pattern raced against a
same-page form-error re-render (attempting to create a tag name that
collided with a leftover from an earlier verification pass) and produced
misleading console output, even though the underlying merge/delete logic
was correct both times. `Client(SERVER_NAME='127.0.0.1')` (matching
`ALLOWED_HOSTS`) gave a deterministic, DB-state-checked pass: source
deleted, target's `news_count` incremented, the reassigned article
carries the target tag.

## Sidebar gained a standalone "Etiketlər" item

CLAUDE.md ch.9's canonical sidebar order lists Tags as its own item
right after Categories; the actual sidebar built up incrementally across
Phases 3–5 never had one (only "Kateqoriyalar" existed, as a disabled
placeholder). Added `Etiketlər` → `cms:tag_list` immediately after the
now-live `Kateqoriyalar` link, matching that canonical order rather than
appending it wherever there was room.

## Media Library folders: rename + delete added post-launch

Phase 5's approved scope was explicitly "flat list, create-only — no
rename/move/nesting." Extended on request to add rename and delete
(nesting/move are still out of scope — untouched). Two implementation
notes:

- **Rename is a plain POST + redirect** (`FolderUpdateView`), not AJAX —
  deliberately mirrors `FolderCreateView`'s existing interaction pattern
  rather than introducing a second one for the same sidebar (CLAUDE.md
  ch.8: "AJAX should be used only when necessary"). The inline
  edit/cancel toggle is pure CSS/JS (`static/js/cms/media-library.js`'s
  `initFolderRename()`), but the actual save is a normal form submit.
- **Delete never touches files** — `MediaFile.folder` is already
  `on_delete=SET_NULL` (Phase 5), so a deleted folder's files simply
  fall back into "Bütün fayllar"; the confirm page states this rather
  than warning about data loss that can't actually happen. Also fixed a
  pre-existing gap while touching this file: `FolderCreateView` had
  never written an `ActivityLog` entry — now all three folder actions do
  (`FOLDER_CREATED/RENAMED/DELETED`).

# Phase 7 (CMS: İstifadəçilər + password reset)

## First role-gated view in the project

Every CMS view up to this phase used only `LoginRequiredMixin` — no view
anywhere checked `role`. CLAUDE.md ch.9 scopes user management to
Administrators, so `apps/core/mixins.py`'s new `AdministratorRequiredMixin`
is genuinely new architecture, not a reused pattern. It passes
`is_superuser` OR `role == Role.ADMINISTRATOR` — not just the role check —
because the seeded `admin` account is a `createsuperuser`-made account,
and `createsuperuser` never touches custom fields, so its `role` silently
defaulted to Journalist. Without the `is_superuser` escape hatch, `admin`
would have been locked out of the very screen meant to fix that. Fixed
the live `admin` row's `role` to `Administrator` as a one-time data
correction during verification (cosmetic — the mixin already covered it).

## `apps/users/` (empty scaffold app) stays unused

It's registered in `INSTALLED_APPS` but contains nothing beyond
`startapp` boilerplate — apparently reserved for this feature by an
earlier phase's `INSTALLED_APPS` entry, never built out. Went with
`apps/accounts/forms.py`'s `UserForm` + `apps/cms/views/user.py` instead,
mirroring the Category/Tag precedent exactly: the form lives with the
model it edits (`accounts.User`), CMS views live in `apps/cms/views/`.
Not reopened — no code currently imports anything from `apps/users/`.

## New-account passwords: real random password, not `set_unusable_password()`

The obvious design — create the account with no usable password, then
immediately email a setup link — silently fails. Checked Django's own
source (`django/contrib/auth/forms.py:423-442`): `PasswordResetForm.
get_users()` explicitly filters out any user where `has_usable_password()`
is `False`. So `UserCreateView.form_valid()` calls
`form.instance.set_password(get_random_string(32))` before saving —
a real, hashed, immediately-discarded password no one (including the
creating administrator) ever sees — which makes `get_users()` include the
account and the setup email actually go out. Verified end-to-end: create
→ email printed by the console backend → confirm link → set real
password → log in with it.

## Password reset is a full Django built-in flow, not just an admin action

User confirmed (asked directly, given the real scope this adds — 5 new
public templates plus 2 email templates) that CLAUDE.md's "Password
Reset" requirement should be built as the complete self-service flow
(`PasswordResetView` → `...Done` → `...Confirm` → `...Complete`), not
only the admin-triggered shortcut. Both paths converge on the same
`apps/accounts/services.py:send_password_setup_email()` helper, which is
just `PasswordResetForm.save()` with the project's own Azerbaijani email/
subject templates — the admin-triggered "Şifrəni sıfırla" skips the
"type your email" step (it already knows the target user) but otherwise
runs the identical token/email/confirm machinery. Never sends or displays
a password itself, only a link (CLAUDE.md ch.12).

## Discovered: `USE_I18N = False` means Django's *own* form labels leak English

Not something this phase introduced — hit while reviewing the rendered
password-reset-confirm page, which showed "New password" / "Your
password can't be too similar to your other personal information." in
plain English despite every other string on the site being Azerbaijani.
Root cause: `config/settings/base.py` sets `USE_I18N = False` (CLAUDE.md
ch.3: single-language site, no i18n architecture), so Django's
`gettext`-wrapped built-in strings (field labels, validator help text on
`AuthenticationForm`/`PasswordResetForm`/`SetPasswordForm`) never get
translated — they render as their literal English source with no
translation catalog to fall back on. This project's own hand-written
forms were never affected (every CMS form's labels are hardcoded
Azerbaijani strings directly in the template, e.g. `user_form.html`'s
`<label>Ad</label>`, never `{{ field.label }}`) — only forms that use
Django's *own* labels via a generic `{% for field in form %}...{{
field.label }}...{% endfor %}` loop were exposed: `LoginForm` (pre-dates
this phase — "Username"/"Password" were already rendering in English on
`login.html`, unnoticed until this review) and the two new password-reset
forms. Fixed by subclassing (`PasswordResetForm`, `SetPasswordForm` in
`apps/accounts/forms.py`, plus `LoginForm`'s existing class) and
overriding `.label`/`.help_text` in `__init__`, mirroring every other
form's hand-written-Azerbaijani-string convention instead of fighting
Django's i18n system for a site that deliberately has none.

## `templates/403.html` — first custom error page in the project

`AdministratorRequiredMixin` is also the first thing that can actually
produce a 403 in this project, surfacing a pre-existing gap CLAUDE.md
ch.6 requires (custom 404/403/500 pages) but no earlier phase needed.
Added only `403.html` (root-level, Django's zero-config convention for
`django.views.defaults.permission_denied` — no `handler403` wiring
needed) extending `cms/base.html` rather than the public site shell,
since the only way to reach it is already-authenticated-but-unauthorized
(`LoginRequiredMixin` redirects anonymous requests to login before
`test_func` ever runs) — full CMS chrome reads better than a bare public
error page. 404/500 remain unbuilt — out of scope, unrelated to this
feature, an older gap this phase didn't create.

# Phase 8 (CMS: Tənzimləmələr)

## Went beyond the mockup — user confirmed managing every existing model field, not just what's drawn

`CMS Settings.dc.html` only shows two fields (site name, contact email)
plus a decorative language selector and a category-reorder list that's an
exact duplicate of the Kateqoriyalar page (Phase 6) — dropped entirely,
not rebuilt here. Meanwhile `SiteSettings` already had `logo`, `favicon`,
`footer_text`, `contact_phone`, `contact_address`, and four social-link
URLs sitting in the schema since Phase 1 with no way to edit any of them
outside a shell. Asked the user directly rather than guessing; confirmed
scope is "every existing model field," not the mockup's literal two
inputs — the mockup under-specifies this screen, not a deliberate design
choice to leave most of the model unmanageable.

## First singleton `UpdateView` in the project

`SiteSettings.get_solo()` always resolves `pk=1` (`save()` hardcodes it,
`delete()` is a no-op) — `SettingsUpdateView` has no pk in its URL
(`tenzimlemeler/`, no `<int:pk>`) and overrides `get_object()` to return
`SiteSettings.get_solo()` directly. Every other CMS `UpdateView` up to
this phase took a pk from the URL; this is the first one that doesn't,
since there's exactly one row and it always exists.

## Two image pickers, one shared crop modal — new `static/js/cms/settings.js`

`static/js/cms/editor.js`'s `initCoverPicker()` (News cover image) is
hardcoded to a single picker's ids/selectors. Instantiating `MediaUploader`
twice on one page — once for logo, once for favicon — would double-bind
click handlers onto the same singleton `#media-crop-modal` DOM
(`templates/cms/partials/media_crop_modal.html` is shared, one instance
per page), so clicking "Tətbiq et" would fire both uploaders' confirm
handlers at once. Fixed by using **one** `MediaUploader` instance for the
whole page and reassigning `.onComplete`/`.defaultRatio` on it right
before each `uploadFile()` call, keyed off which picker's file input
changed — safe because `MediaUploader` (Phase 5) already reads
`this.onComplete`/`this.defaultRatio` at the moment it needs them, not
once at construction time (confirmed by re-reading `media-uploader.js`
before relying on it). Selectors generalized to `data-role="image-picker"`
+ an optional `data-aspect-ratio` attribute (favicon → `"1"` for a square
crop, logo → unset → free crop) instead of hardcoded per-field ids, so a
third picker could be added to some future page by copying the markup
pattern, not the JS. Deliberately did not refactor `editor.js` to share
this — the News cover picker already works and is tested; duplicating
~15 lines was judged lower-risk than touching it for this phase.

## Logo and social links now actually render on the public site

Both were "defined on the model but not yet rendered anywhere" before
this phase (confirmed by grepping every template) — saving them from the
new Settings screen would have been pointless if nothing ever displayed
them. `templates/components/header.html`'s brand link now shows
`site_settings.logo.file.url` when set (falls back to the `site_name`
text link otherwise) — uses `.file.url` directly, not `.thumbnail`, since
a logo doesn't go through the same small-card thumbnail pipeline as a
News cover image. `templates/components/footer.html` gained a row of
social icons in the brand column, one per non-empty `social_*` URL
(Bootstrap Icons `bi-facebook`/`bi-instagram`/`bi-twitter-x`/`bi-youtube`
— confirmed all four exist in the vendored icon font before using them).
`favicon` was already wired correctly in `templates/base.html` since an
earlier phase — untouched here.

## Access restricted to Administrators, same as User Management

CLAUDE.md's Settings chapter doesn't explicitly say "Administrators
only" the way the User Management chapter does, but site-wide branding/
contact/social configuration is at least as sensitive as user accounts —
reused `AdministratorRequiredMixin` (Phase 7) rather than leaving it at
plain `LoginRequiredMixin`. Sidebar's "Tənzimləmələr" item follows the
same conditional-link-vs-disabled-span pattern already used for
"İstifadəçilər".

# Phase 9 (CMS: Statik səhifələr)

## `Page.content` upgraded from plain TextField to CKEditor5Field

User confirmed upgrading it to match `News.content` — Haqqımızda/Privacy/
Terms benefit from real formatting (headings, lists), which a
paragraph-only plain-text field couldn't offer. This meant:

- **`sanitize_article_html` relocated to `apps/core/utils.py` as
  `sanitize_rich_text_html`.** It lived in `apps/news/utils.py`, but
  `apps/pages` importing from `apps.news` would violate CLAUDE.md ch.4
  ("Avoid importing unrelated applications directly") — News and Pages
  share no other relationship. Moved verbatim (same allow-list, same
  bleach config) to `apps/core/utils.py`, already home to `az_slugify`/
  `get_client_ip` — exactly the "Shared Services" pattern ch.4 describes.
  `apps/news/models.py` updated its import; `apps/news/utils.py` deleted
  (nothing else used it, confirmed by grep before removing). Verified the
  moved function behaves identically: `<strong>`/`<ul>`/`<li>` survive,
  `<script>` is stripped — same as News's existing behavior.
- **`split_paragraphs`/`Page.content_paragraphs` removed as dead code.**
  `News` had already stopped calling `split_paragraphs` when it moved to
  CKEditor (Phase 4) — `Page` was the only remaining caller, so once Page
  also moved to CKEditor, the helper had zero callers left.
  `templates/pages/page_detail.html` and `about.html` switched from
  looping `page.content_paragraphs` to `{{ page.content|safe }}`,
  mirroring `templates/news/detail.html`'s `article.content|safe` exactly
  — content is already bleach-sanitized in `save()`, same trust boundary
  as News.
- **`Page.slug` gained `blank=True`** — the same `ModelForm._post_clean()`
  fix applied to News/Category/Tag/Tag in earlier phases, needed the
  moment a model gets its first real CMS form.
- **Existing seeded pages needed a one-time data fix.** `_seed_pages()`
  now wraps paragraphs in `<p>` tags (mirroring `ARTICLES`' existing
  transformation in the same file) so *newly seeded* pages render
  correctly under `|safe` — but `get_or_create()` only sets defaults on
  first creation, so the three pages already in the dev DB from earlier
  phases still held old plain-text content with no HTML markup at all.
  Fixed with a one-time shell command wrapping their stored content in
  `<p>` tags to match; a fresh `seed_initial_data` run on a clean database
  doesn't need this step.

## No CMS Pages mockup — screen follows the Category/Tag/User shell

Same situation as Phase 6's Tags screen: `design/` has public-facing
`About.dc.html`/`Contact.dc.html` but no CMS admin screen for managing
`Page` rows. Built `page_list.html`/`page_form.html`/
`page_confirm_delete.html` directly from the already-established
`tag_list.html`/`tag_form.html`/`tag_confirm_delete.html` shell (search,
`cms-table`, row menu, `cms-simple-form`, `cms-confirm`) rather than
inventing new patterns. One addition: `.cms-simple-form--wide` (880px,
matching the News editor's `.editor__main`) — the existing 480px
`.cms-simple-form` was sized for Category/Tag/User's few short fields,
too narrow to give the new CKEditor instance reasonable room.

## Hard delete, redirect-to-edit after create — matches Page's actual shape

`Page` has no `is_deleted` field (unlike `News`/`Category`) — confirmed
in the model before building anything — so `PageDeleteView` hard-deletes,
same shape as `TagDeleteView`. `PageCreateView` redirects to
`page_edit` after saving (like `NewsCreateView`), not to the list (like
`CategoryCreateView`/`TagCreateView`) — with a CKEditor field involved,
staying on the edit screen to keep refining content matches how News
already works, more than the short-form Category/Tag pattern does.

## "Əlaqə" (Contact) is explicitly out of scope — confirmed before building anything

Contact is `ContactView` + `ContactForm` + a Celery email task, not a
`Page` row (confirmed by grepping `seed_initial_data.py`'s `PAGES` list
— "Əlaqə" never appears in it). The new Pages CMS section manages actual
`Page` table rows only; Contact's form/email flow is untouched.

## Sidebar gained a "Səhifələr" item with no prior placeholder

Unlike Reklam/SEO (which at least have `is-disabled` stub spans),
Pages had no sidebar slot at all before this phase — confirmed by reading
`templates/cms/base.html` in full before adding one. Placed right after
"Media", grouping it with the other content-management items
(Xəbərlər/Kateqoriyalar/Etiketlər/Media/Səhifələr) ahead of the more
sensitive İstifadəçilər/Tənzimləmələr items. Plain `LoginRequiredMixin`,
not `AdministratorRequiredMixin` — static pages are editorial content,
not site-wide sensitive configuration.

# Phase 10 (CMS: Reklam / Advertisements)

## First entirely-new domain model built this project — `AdPosition` + `Advertisement`

`apps/advertisements/` existed only as empty `startapp` scaffolding since
Phase 1 (same state `apps/users/` was in before Phase 7) — no prior model
to extend, unlike every other phase so far. Two models, not one:

- **`AdPosition`** is a separate model, not a hardcoded `TextChoices` field
  on `Advertisement` — user confirmed this explicitly. CLAUDE.md ch.9
  states "Advertisements should never require template modifications"
  and separately lists "Default advertisement positions" as seed data —
  both only make sense if positions are DB rows an admin (or a seed
  command) can add, not enum values requiring a code change. Templates
  reference a position by its `code` through `{% ad_slot "code" %}`
  (`apps/advertisements/templatetags/ads.py`) — adding a *new* campaign
  to an *existing* slot, or even adding a whole new `AdPosition` row,
  never touches a template again after this phase.
- **`Advertisement.status` is computed, not stored** — `is_active`
  (manual pause/resume, same shape as `News.is_featured`) combined with
  `start_date`/`end_date` yields `active`/`scheduled`/`paused`/`expired`
  via a property, exactly mirroring how `NewsQuerySet.published()`
  computes visibility from `status` + `published_at` at query time. No
  Celery Beat schedule exists anywhere in this project (confirmed before
  designing this — `config/celery.py` has no `beat_schedule`, no
  `django-celery-beat` installed) — News doesn't get automatic status
  transitions either, so building one just for Ads would be inventing
  infrastructure the rest of the project doesn't have.

## `AdPosition` gets Django admin only, not a CMS screen

The `CMS Ads.dc.html` mockup shows only a campaign list — no position
manager UI anywhere. Combined with CLAUDE.md treating positions as seed
data rather than a described CMS workflow, positions are managed via
Django admin (`apps/advertisements/admin.py`, dev-only per CLAUDE.md
ch.9) plus `seed_initial_data.py`'s new `_seed_ad_positions()` — which
seeds exactly the two positions the public templates' `data-position`
attributes already implied (`home-sidebar-1`, `category-sidebar-1`,
both 360×280 — the only pixel-exact ad placement in any mockup). The
full CMS section (list/create/edit/soft-delete/restore, matching
`CategoryListView`'s tabbed soft-delete shape since CLAUDE.md ch.10
lists Advertisements among soft-delete entities, unlike Page in Phase 9)
is for `Advertisement` campaigns only.

## `banner`/`position` are `on_delete=PROTECT`, not `SET_NULL` — and that required fixing `MediaDeleteView`

Every other `MediaFile`-referencing FK in the project (`News.featured_image/
og_image`, `SiteSettings.logo/favicon`) is `SET_NULL` — losing the image
just means nothing renders, never blocks a delete. An ad's banner is
different: a live campaign silently losing its creative (or its position)
is a real content-integrity problem, not a cosmetic one, so both FKs are
`PROTECT` here, the same reasoning as `News.category`. That surfaced a
real bug while implementing it: `MediaDeleteView.post()`
(`apps/cms/views/media.py`, Phase 5) called `media_file.delete()`
unconditionally — with a `PROTECT` reference now possible, that would
raise an unhandled `ProtectedError` → 500, not the graceful
usage-count warning the confirm page already shows. Fixed by wrapping the
delete in `try/except ProtectedError` with a friendly message, and — while
touching it — reordered the method to delete the DB row *before* deleting
the physical files (previously files were deleted first), so a blocked
delete can no longer leave a `MediaFile` row pointing at files that no
longer exist on disk. `MediaFile.usage_count` also gained a
`Advertisement.objects.filter(banner=self).count()` term so the warning
actually fires for banner references, not just News/Settings ones.

## Click tracking only — impressions explicitly deferred

CLAUDE.md itself lists "Click tracking (future)" under Advertisements,
and separately doesn't mention impressions at all — user confirmed
building just the click side. `Advertisement.click_count` is a plain
counter (`F('click_count') + 1`, avoiding a read-modify-write race, same
pattern as `News.view_count` would use) incremented by the public,
unauthenticated `AdClickView` at `/reklam-klik/<pk>/`, which then
redirects to `target_url`. No per-click log exists, so the CMS list's
"Bu ay klik sayı" stat is an approximation (sum of `click_count` across
campaigns that are live *right now*, not a true monthly tally) —
documented in the view's code comment, not hidden.

## `/reklam-klik/` — not `/reklam/` — to leave room for the "advertise with us" page

`Sitemap.dc.html` shows `/reklam/` as a public advertiser-info page, and
that's just a `Page` row (seeded this phase, `apps/pages` infrastructure
from Phase 9, zero new code) served by `apps.pages.urls`'s root-level
`<slug:slug>/` catch-all. Mounting `apps.advertisements.urls` at
`reklam/` instead of a distinct `reklam-klik/` prefix would have
permanently blocked that slug from ever working. Chose the non-colliding
prefix up front rather than discovering the conflict later.

## Public rendering never touches the two existing `ad-slot` divs directly

`templates/news/home.html` and `templates/categories/category_detail.html`
already had empty `<div class="ad-slot ad-slot--sidebar" data-position="...">`
placeholders stubbed in from an earlier phase. Replaced with
`{% ad_slot "home-sidebar-1" %}` / `{% ad_slot "category-sidebar-1" %}` —
the inclusion tag renders the *same* empty placeholder markup when no
campaign is live for that position (verified: an empty database produces
pixel-identical output to before this phase), and the real banner
`<img>` once one exists. One active campaign per position, no rotation/
carousel — nothing in any mockup suggested multiple banners sharing a
slot, and building rotation logic nobody asked for would be exactly the
kind of speculative feature CLAUDE.md's "avoid unnecessary abstraction"
warns against. A future phase can add it if it's ever actually needed.

# Phase 11 (CMS: SEO)

## Full scope confirmed — sitemap, robots.txt, remaining `SEOFieldsMixin` fields, JSON-LD

`apps/seo/` had existed since early phases as just an abstract
`SEOFieldsMixin` (9 fields, mixed into `News`/`Page`) with no sitemap, no
robots.txt, and only 2 of its 9 fields (`meta_title`/`meta_description`)
actually editable anywhere. User confirmed the full option rather than a
partial one: `django.contrib.sitemaps`-based sitemap.xml, dynamic
robots.txt, the remaining 7 fields exposed on the News/Page edit forms,
and JSON-LD (`NewsArticle`, `BreadcrumbList`, `WebSite`/`Organization`).
Analytics fields (GA/Meta Pixel) were explicitly out of scope.

## Sitemap and robots.txt use Django's own `django.contrib.sitemaps`, not a hand-rolled view

CLAUDE.md ch.15 prefers standard Django solutions over custom code where
one already exists. `apps/seo/sitemaps.py` defines one `Sitemap` subclass
per public entity (`News`, `Category`, `Tag`, `Page`, plus a `static`
sitemap for the homepage), each reusing an existing queryset method
(`News.objects.published()`, `Category.objects.active().visible()`) so
"only real content, never drafts/soft-deleted" is enforced in exactly one
place already trusted elsewhere in the codebase — not reimplemented.
`TagSitemap` deliberately filters to tags with at least one published
article; an empty tag page isn't worth a sitemap entry. Because
`django.contrib.sitemaps` queries the database fresh on every request
(no caching layer of its own), "sitemap updates automatically after
content changes" (CLAUDE.md ch.14) is true for free — no signal, no cache
invalidation to wire up. `robots_txt` (`apps/seo/views.py`) is a plain
view, not a static file, specifically so its `Sitemap:` line always
matches the live host via `request.build_absolute_uri()` rather than a
hardcoded domain.

## `static/js/cms/settings.js` renamed to `static/js/cms/image-pickers.js`

The file stopped being Settings-specific back in Phase 10 (Reklam's
banner picker already used it) — this phase makes it a third and fourth
consumer (News, Page), so it finally got a name that describes what it
does rather than where it was first written. Pure rename, no logic
change; `settings.html`/`ad_form.html`'s script tags were updated to
match.

## News' `featured_image` picker migrated off the old single-picker `editor.js` code, to make room for `og_image`

Before this phase, `news_form.html`'s cover image used a bespoke,
News-only implementation (`editor.js`'s `initCoverPicker()`) hardcoded to
one picker per page (`data-role="cover-picker"`, `#cover-file-input` as a
literal DOM id). Adding a second picker for `og_image` on the same page
would have hit the exact "two independent `MediaUploader` instances
double-bind the shared crop modal's click handlers" bug already solved
once in Phase 8 for Settings' logo+favicon pair. Rather than solve it
twice, `featured_image` was migrated onto the same generalized
`data-role="image-picker"`/`"picker-input"` pattern Settings/Reklam
already use — one shared `MediaUploader` instance per page, with
`onComplete`/`defaultRatio` reassigned per-picker immediately before each
`uploadFile()` call. `og_image` then became a second picker on
already-proven shared infrastructure instead of new one-off code.
`initCoverPicker()` was deleted from `editor.js` as dead code once no
template referenced `data-role="cover-picker"` anymore. `Page` gained an
`og_image` picker the same way — it never had any picker before this
phase.

**Bug found and fixed during verification**: the first draft of both
picker blocks placed the hidden `{{ form.featured_image }}`/
`{{ form.og_image }}` input *after* the closing `</div>` of the
`.media-picker` wrapper. `image-pickers.js` scopes its
`querySelector('[data-role="picker-input"]')` lookup to each picker's own
wrapper element, so the hidden input has to live *inside* that wrapper
(matching the working Settings/Reklam markup) — otherwise
`hiddenInput` resolves to `null` and the upload's `onComplete` callback
throws `Cannot set properties of null (setting 'value')`, silently
swallowed into a toast rather than a visible page error. Caught by an
end-to-end Playwright pass that actually uploaded a file into each
picker and read back the hidden field's value, not just by checking the
markup rendered.

## `<head>` gained blocks it never had: `robots`, `extra_meta`, `structured_data`

`templates/base.html` previously had no `<meta name="robots">` tag at
all, and no block a child template could use to inject arbitrary extra
`<meta>` tags or JSON-LD. Added `{% block robots %}index, follow{% endblock %}`
(default matches previous implicit behavior — everything was indexable
before), `{% block extra_meta %}{% endblock %}` (used by `meta_keywords`
on News/Page), and `{% block structured_data %}{% endblock %}` (used by
`NewsArticle` JSON-LD) right after the site-wide `Organization`/`WebSite`
JSON-LD block, which now renders unconditionally on every page. A single
`<meta name="twitter:card" content="summary_large_image">` was added —
title/description/image are already covered by the existing `og:*` tags,
so no separate `twitter:title`/`twitter:image` were added; X reads
Open Graph tags as a fallback in their absence.

## `News`/`Page` detail templates: `canonical_url`/`og_image`/`robots` now fall back correctly, not silently ignore the field

Before this phase `canonical_url` was rendered as `{{ request.build_absolute_uri }}`
unconditionally — the field existed in the database but had no effect.
Same for `og_image` (`og:image` always came from `featured_image`, never
checking whether an editor had set a distinct `og_image`) and
`robots_index`/`robots_follow` (no `<meta name="robots">` override
existed at all, so a `noindex` article would still say "index, follow").
Fixed with `{{ article.canonical_url|default:request.build_absolute_uri }}`,
an `og_image`-first-then-`featured_image` fallback, and a computed
`{% block robots %}` reading both boolean fields. `page_detail.html`'s
`{% block title %}` also started using `page.meta_title` (previously
ignored entirely, always falling back to `page.title`) — a pre-existing
gap being closed as part of exposing the full field set, not a new
feature.

## JSON-LD kept to three schema types, no duplicate CMS meta-tag editor

`NewsArticle` (per-article, `news/detail.html`), `BreadcrumbList` (added
directly to `components/breadcrumbs.html` so it renders "for free" on
every page that already includes that component — News, Category, Page,
Tag), and `WebSite`+`Organization` (site-wide, `base.html`, rendered once
per page as a single `@graph`). All string values embedded via Django's
`escapejs` filter rather than raw interpolation, since JSON-LD lives
inside a `<script>` tag and needs the same escaping discipline as any
other JS string literal. The `CMS SEO.dc.html` mockup includes a
per-article meta-tag editor alongside its 3 status cards — deliberately
not built as a second screen: those exact fields are now edited on the
article's/page's own form (this phase's other change), and a duplicate
editing surface for the same underlying fields would violate CLAUDE.md's
DRY principle for no benefit. `apps/cms/views/seo.py`'s
`SeoOverviewView` renders only the 3 status cards (sitemap active,
robots.txt configured, count of published-but-`robots_index=False`
News+Pages) plus a short note pointing editors to the article/page forms
instead.

# Phase 12 (CMS: inline images + YouTube video in CKEditor)

## Both blockers from the original CKEditor toolbar comment are now resolved

`CKEDITOR_5_CONFIGS['default']` had shipped since early phases with Images
and Videos deliberately left off the toolbar, with the reason spelled out
in a code comment: images needed the Media Library's upload→`MediaFile`
pipeline (didn't exist yet at that point), and `mediaEmbed` by default
saves a non-standard `<oembed>` tag with no resolver to render it on the
public site. Both are now false: the Media Library pipeline
(`apps/media_manager/services.py`) has existed since Phase 4/5 and is
reused directly, and `mediaEmbed.previewsInData: true` bakes the actual
`<iframe>` straight into the saved data, so no resolver is needed at all.

## No npm rebuild — the bundled package already ships every plugin used

`django_ckeditor_5`'s pinned bundle (`django_ckeditor_5/static/
django_ckeditor_5/src/ckeditor.js`) is a "kitchen sink" build that already
includes `Image`, `ImageCaption`, `ImageStyle`, `ImageToolbar`,
`ImageResize`, `SimpleUploadAdapter`, and `MediaEmbed` — confirmed by
reading the installed package's source before writing any code. Enabling
both features was therefore a matter of Django-side config (toolbar
array, a new upload view, a small custom JS file) rather than a
frontend build step.

## Inline images upload through the same pipeline as every other image, minus the crop step

New `CKEditorImageUploadView` (`apps/cms/views/media.py`) is the upload
target CKEditor5's `SimpleUploadAdapter` posts to — wired in via
`CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME` (`config/settings/base.py`), which
`django_ckeditor_5`'s widget reads instead of its own default view. The
view calls the exact same `stage_upload()` → `process_crop()` pair the
Media Library and every image picker use, just with `crop_box=None` —
confirmed by user: inline body images skip the interactive Cropper.js
step (unlike Featured/OG images), resized instead via CKEditor's own
drag handles (`ImageResize`, bundled). Every inline image still gets
WebP conversion, a thumbnail, and a real `MediaFile` row — not a raw
file dumped under `MEDIA_ROOT`, which is what the package's own default
upload view (`django_ckeditor_5/views.py`) does.

**SVG is not selectable through this button, and can't be** — confirmed
by testing, not assumed. `CKEDITOR_5_UPLOAD_FILE_TYPES` (a Django
setting) only controls part of the picker's behavior; the file input's
actual `accept` HTML attribute is built by CKEditor5's own Image plugin
from a hardcoded extension→MIME table that has no SVG entry, regardless
of what's listed in that Django setting. SVGs remain fully supported
everywhere else in the project (Media Library, Featured/OG image
pickers) — this is a CKEditor5 library limitation specific to inline
body-content images, not a gap in this project's pipeline.

## YouTube video uses a hand-written provider, not MediaEmbed's own default one

MediaEmbed ships a built-in YouTube provider, but with
`previewsInData: true` its saved output is `<div style="position:
absolute;...">` — inline styles throughout, which CLAUDE.md forbids
outright ("Never generate inline styles", ch.3/ch.6/ch.7). It would also
recognize every other bundled provider (Vimeo, Twitter, Instagram,
Spotify, …), when only YouTube was asked for. A one-function custom
provider (`static/js/cms/ckeditor-youtube-embed.js`, wired in via
`CKEDITOR_5_CONFIGS['default']['mediaEmbed']['providers']`) avoids both
problems: its output is a plain `<div class="media-embed"><iframe>`
styled by a real stylesheet (`static/css/components/rich-text.css`), and
no other provider is registered, so pasting a Vimeo/Twitter/etc. link
simply does nothing.

**Discovered mid-implementation**: `django_ckeditor_5`'s widget bootstrap
(`app.js`) resolves regex-shaped config strings to real `RegExp` objects
by calling `value.toString()` and checking the result against
`^/(.*?)/([gimy]*)$`. That works for a single regex string, but breaks
silently for an array of regex strings — `Array.prototype.toString()`
joins all elements with commas *before* the check runs, collapsing three
separate patterns into one garbled, unusable string (and then matching
the outer detection pattern *again* on the joined mess, mangling it
further). Caught by inspecting the live `editor.config.get('mediaEmbed')`
in a real browser, not by reading source alone — the config *looked*
correct in Python and in the rendered `<script type="application/json">`
tag; only the parsed runtime value was actually broken. Fixed by
combining the three YouTube URL shapes (`watch?v=`, `/shorts/`,
`youtu.be/`) into one regex with alternation instead of a list — sidesteps
the library bug entirely rather than working around it.

## Bleach allow-list changes are structural, not just "trust the toolbar"

`sanitize_rich_text_html` (`apps/core/utils.py`) is the actual security
boundary — applied in `save()`, not just the form, per its own existing
docstring. Two additions, both verified against the *exact* HTML
CKEditor produces (captured via `editor.getData()` in a real browser
session, not guessed):

- `figure`/`figcaption` (CKEditor5's block-image wrapper, also reused —
  with `class="media"` — as `previewsInData`'s outer wrapper around the
  custom YouTube provider's own markup) and `div`/`iframe`
  (the provider's inner wrapper).
- `iframe`'s `src` attribute is validated by a callable, not a plain
  list — `_validate_iframe_attribute` only allows `https://` URLs whose
  host is `youtube-nocookie.com` (or its `www.` form). The CKEditor UI
  only ever offers YouTube, but the UI isn't the boundary; a raw `<iframe
  src="https://evil.example/">` crafted any other way (a direct API call,
  a future SourceEditing slip) gets its `src` attribute stripped on
  save, same as any other write path. Verified with a Django-shell
  negative test before considering this done.
- `_CSS_SANITIZER`'s allowed CSS properties gained `width` (CKEditor5's
  `ImageResize` writes `style="width: NN%"` on the `<figure>`, not the
  `<img>`) and `aspect-ratio` (CKEditor5 stamps `style="aspect-ratio:
  W/H"` on every inserted `<img>` to prevent layout shift — discovered
  from real editor output, not anticipated in the original plan).

## Shared `rich-text-content` CSS class instead of per-page-type duplication

New `static/css/components/rich-text.css` styles `figure.image img`,
`figcaption`, and `.media-embed` once. Applied via a `rich-text-content`
class added to three existing prose wrapper divs — `.article__content`
(News), `.about-page__prose` (both `Page` detail and the dedicated About
page) — rather than writing the same rules three times (CLAUDE.md ch.7
"component-based architecture").

## Pagination audit — no changes made

Explored before starting this phase: every list-type page across the
public site and CMS already paginates (`paginate_by` + `components/
pagination.html`) except the CMS Categories list, which is unpaginated
*by design*, documented in the view's own docstring (`apps/cms/views/
category.py`) — the category tree is capped at two levels, so the list
is inherently short, and the `CMS Categories.dc.html` mockup doesn't show
a pager. Nothing was changed here this phase; it was audited and found
already correct.

# Phase 13 (CMS responsiveness)

## The CMS had zero media queries anywhere — a real, user-reported bug, not a gap discovered internally

User reported the admin panel wasn't responsive at all, pages overflowing
the screen. Verified before touching anything: `templates/cms/base.html`
never loads `static/css/responsive/mobile.css`, and that file has no
`.cms`-prefixed selectors regardless — the entire CMS section had no
responsive behavior whatsoever. `.cms-sidebar` was a hardcoded `width:
240px; flex: none` with no collapse mechanism, directly violating
CLAUDE.md ch.9's explicit spec: *"The sidebar is permanently visible on
desktop. On tablets and mobile devices it becomes collapsible."*

## Diagnosed by measurement, not by CSS inspection alone

Static CSS reading can't reliably predict real overflow — flex/grid
shrink behavior, cascade order, and `overflow-x: auto` containment all
interact in ways that are easy to get wrong on paper. Instead: started
the dev server, logged in via Playwright, and on all 12 CMS pages at 4
viewport widths (1440/1024/768/375) measured
`document.documentElement.scrollWidth` against `window.innerWidth`, then
walked the DOM for the actual overflowing element. The first version of
that DOM walk gave false positives — it flagged elements sitting *inside*
an already-correct `overflow-x: auto` wrapper (e.g. `.cms-table` inside
`.cms-table-wrapper`) as if they were the problem, when the wrapper was
already containing them exactly as designed. Rewritten to only count an
element as a true culprit if no ancestor's `overflow-x` was already
absorbing it — this is what actually found the real, independent bugs
below instead of chasing scroll containers that were working correctly.

## `.visually-hidden` needed `!important` — a genuine specificity bug, unmasked by the same diagnostic

The single biggest overflow contributor (up to +1072px of document width
at 1440px) wasn't a missing media query at all: `news_form.html`'s tag
`<select multiple>` (`static/js/cms/editor.js`'s `initTagPicker()` adds
`.visually-hidden` to it once the JS pill-picker widget takes over) also
carries `.form-input`. `forms.css` loads after `utilities.css` in
`base.html`'s `<head>`, so with equal specificity `.form-input`'s width
rule wins the cascade, leaving a full-width, absolutely-positioned
`<select>` (with every `<option>` at that same width) that still
contributes to the page's scrollable area despite being visually
invisible. Fixed with `!important` on every `.visually-hidden` property
(`static/css/base/utilities.css`) — the standard, expected shape for a
sr-only utility, which by definition must survive being combined with
any component class. This is the only `!important` introduced this
phase; CLAUDE.md ch.7 permits it for exactly this kind of case.

## Collapsible sidebar reuses the public site's existing off-canvas pattern, not a new one

`static/js/components/menu.js` already implements the toggle-button +
`is-open` class + close-on-outside-click shape for the public site's
mobile nav. `static/js/cms/sidebar.js` is the same shape (plus Escape-to-
close and a backdrop element, matching this project's existing Modal
Component spec — CLAUDE.md ch.11 "Overlay Click, Escape Key" — since the
CMS sidebar covers noticeably more of a narrow screen than the public
nav does). `static/css/cms/shell.css` gained the `@media (max-width:
992px)` block making `.cms-sidebar` a fixed, `translateX`-animated
drawer anchored left (the public nav's equivalent is right-anchored,
since that's where it normally sits) — same `z-index: 200` and
`--transition-base` token the public nav uses, for consistency. New
`.cms-topbar__menu-toggle` hamburger button, hidden above 992px, and a
new `#cms-sidebar` id / `.cms-sidebar-backdrop` div in
`templates/cms/base.html`.

## Cascade-order pitfall: a media-scoped override placed *before* the base rule it's overriding still loses

First draft of the `.editor` (News/Page editor two-column layout) mobile
stack put the new `@media (max-width: 1200px) { .editor__sidebar {
width: 100% } }` block directly under `.editor {}` at the top of
`editor.css`, while the original un-guarded `.editor__sidebar { width:
360px }` rule is defined later in the same file. Same selector
specificity, so CSS resolves the tie by source order — the *later*,
unconditional rule won regardless of viewport, silently no-opping the
override. Caught by re-running the same Playwright measurement after the
first round of fixes (still overflowing 392px vs 375px at mobile), not
assumed correct after writing the CSS. Fixed by moving the whole media
query to the end of the file, after every un-guarded rule it needs to
beat. `.cms-panel-grid` (Dashboard's chart+distribution two-column row)
had the same "not yet responsive" gap, found by the same re-run — it had
simply never been exercised at a narrow enough width before now — and
got the same treatment: a `@media (max-width: 576px)` collapsing it to a
single column, alongside `.cms-stat-grid`, `.cms-filter-bar`, and
`.media-dropzone` all gaining either responsive `grid-template-columns`
steps or `flex-wrap: wrap`.

## Verification

Re-ran the same measurement script after every fix, not just once at the
end — the two remaining bugs above (`.editor__sidebar` cascade order,
`.cms-panel-grid`) were only found because of that second pass. Final
state: all 12 CMS pages, all 4 viewport widths, zero horizontal overflow.
Separately verified: hamburger hidden above 992px (no visual regression
on desktop — screenshotted), visible and functional at 375px (toggle
opens/closes, backdrop click closes, Escape closes, `aria-expanded`
tracks state correctly). Zero console errors across every run.

# Phase 14 (public nav bug + CKEditor text-wrap for images)

## Public site: the mobile hamburger button was visible (and inert) on desktop — a pre-existing bug, same root cause pattern as Phase 13's `.visually-hidden` fix

User reported the hamburger button showing on large screens and doing
nothing when clicked. Root-caused with the same measurement approach as
Phase 13 (Playwright, real computed styles, not reading CSS on paper):
`components/header.html`'s toggle button carries both `.header-icon-btn`
(`components/buttons.css`, `display: inline-flex`) and `.header-menu-
toggle` (`layout/header.css`, `display: none`). `buttons.css` loads
*after* `header.css` in every `base.html`, so with equal selector
specificity the later rule wins regardless of viewport — the button
was never actually hidden on desktop, it just happened to show the
*correct* value below 992px by coincidence (both rules agree there).
Clicking it did toggle `#primary-navigation`'s `is-open` class
correctly (confirmed — the JS was never broken), but `.nav.is-open`'s
positioning/transform rules only exist inside `@media (max-width:
992px)`, so above that width the class toggle has nothing to visually
react to.

Fixed by bumping selector specificity (`button.header-menu-toggle`
instead of `.header-menu-toggle`, in both `layout/header.css` and its
`static/css/responsive/mobile.css` override) rather than reordering
global stylesheet `<link>` order — reordering risks unrelated cascade
assumptions elsewhere in two large, long-lived files; an element-type
selector addition is a one-line, fully localized fix with no other
surface area. Verified: hidden at 1440px, still visible and functional
at 768px, same as before.

## CKEditor images can now wrap article text — `imageStyle:alignLeft`/`alignRight`

Phase 12 deliberately left `imageStyle` alignment off the image toolbar
(`config/settings/base.py`), reasoning that the article body was a
single fixed-width reading column with no floated-image precedent in any
mockup. User explicitly asked for text-wrap-around-image after that,
which is a straightforward reversal: added `'imageStyle:alignLeft'`,
`'imageStyle:alignCenter'`, `'imageStyle:alignRight'` to `image.toolbar`.
These are CKEditor5's *inline*-image alignment styles (as opposed to
`alignBlockLeft`/`alignBlockRight`, which align without float) —
confirmed which class names they actually produce by capturing real
`editor.getData()` output in a browser rather than assuming from docs:
`image-style-align-left` / `image-style-align-right`. `apps/core/utils.py`'s
bleach sanitizer needed no change — `figure`'s `class` attribute was
already allowed with any value from Phase 12. New CSS in `static/css/
components/rich-text.css`: `float: left/right`, a margin on the far side
only (matching the spacing convention in the editor's own bundled CSS,
`django_ckeditor_5/dist/styles.css`, inspected directly for parity), and
`max-width: 50%` so a floated image always leaves room for text to
actually wrap next to it — `ImageResize` (already bundled, unchanged)
lets an editor shrink it further via drag handles if they want narrower.

## Video text-wrap is not possible without writing an actual CKEditor5 plugin — tried three approaches, verified each fails live before giving up

User also asked for the same text-wrap behavior around inserted YouTube
videos. Unlike Image, CKEditor5's `MediaEmbed` feature has no built-in
alignment/float mechanism — there's no `mediaStyle` equivalent to
`imageStyle`. Investigated whether the bundled, generic `Style` plugin
(`@ckeditor/ckeditor5-style`, confirmed present in `django_ckeditor_5`'s
webpack bundle) could fill the gap, since it's designed to let a config
apply an arbitrary class to a selected element via a toolbar dropdown:

- Configured `style.definitions` with `element: 'figure'` (the media
  widget's outer wrapper tag) — the dropdown button was enabled and the
  definitions worked correctly when an *image* figure was selected, but
  stayed disabled specifically when a media/video figure was selected
  (confirmed live: `.ck-disabled` class present on the button element
  in that state, via Playwright, not inferred from a screenshot).
- Tried `element: 'oembed'` instead (the media model's actual internal
  element name, visible in `editor.config.get('mediaEmbed').elementName`)
  in case the plugin matched by model name rather than tag — same
  result, still disabled.
- Concluded the Style command's enablement check only recognizes a
  fixed set of built-in-supported schemas (image, table, …) and
  MediaEmbed's widget isn't among them, regardless of which `element`
  value is configured — this is a hardcoded plugin limitation, not a
  config value to discover. Extending it for real would mean writing an
  actual CKEditor5 `Plugin` subclass with its own schema/converter
  registration in JavaScript, which in turn requires compiling a new
  editor bundle — `django_ckeditor_5` ships a pre-built bundle
  (`static/django_ckeditor_5/dist/bundle.js`) with no build pipeline in
  this project to extend it from source. That's a materially different,
  much larger scope than a config change, so it wasn't attempted without
  the user weighing in first.

Removed the non-functional `'style'` toolbar item and `style.definitions`
config entirely rather than leaving a permanently-disabled button in the
toolbar (CLAUDE.md ch.15 "no placeholder implementations, no unfinished
code") — video embeds stay full-width/block-only for now.

# Phase 15 (login hardening: hide the CMS entry point, brute-force lockout)

## Public header no longer links to the login page

`components/header.html` showed a person-icon link to `accounts:login`
for every anonymous visitor. Removed outright — logged-in staff still
see a logout icon (unchanged, `{% if request.user.is_authenticated %}`),
but there's no `{% else %}` branch anymore for anonymous visitors. This
is UI hygiene, not a security control by itself: `/accounts/login/`
still resolves and is reachable by anyone who knows or guesses it — told
the user this explicitly rather than let "the button's gone" be mistaken
for "the attack surface is gone." The actual control is the lockout
below.

## Brute-force lockout — custom, cache-backed, not django-axes

User chose the custom option after being asked (recommended, since Redis
is already the project's configured cache backend, CLAUDE.md ch.13 — no
new dependency needed, versus `django-axes`, which is a fine package but
adds one anyway plus its own DB tables for a project this size).

New `apps/accounts/services.py` functions — `is_login_locked_out`,
`register_login_failure`, `clear_login_failures` — key the counter on
`(IP, username)`, not IP alone or username alone: locks out one attacker
grinding through passwords for one account from one machine, without
that letting an attacker deny service to a real user logging in from a
*different* IP, or to every account behind a shared office IP (both real
failure modes of a naive single-key design). `LOGIN_ATTEMPT_LIMIT = 5`,
`LOGIN_LOCKOUT_SECONDS = 15 * 60` — a fixed window from the first
failure (not slid forward per attempt), the simpler of the two standard
rate-limit shapes and enough for CLAUDE.md ch.12's "Temporary lockout".

`apps/accounts/views.py`'s `LoginView.post()` checks the lockout
*before* calling into Django's own auth backend at all — a locked-out
pair never reaches password verification, not even to fail it again.
`form_valid()` calls `clear_login_failures()` so a legitimate user who
mistyped their password a few times isn't left throttled after finally
getting it right. Every blocked attempt is also logged
(`ActivityLog.Action.LOGIN_BLOCKED`, new choice — migration
`apps/logs/migrations/0007_alter_activitylog_action.py`), alongside the
existing `LOGIN_FAILED`/`LOGIN_SUCCESS` entries from Phase 7, so the
Activity Log screen shows the whole picture without any new UI.

Verified live (Playwright): 5 wrong-password submissions, 6th submission
using the *correct* password still rejected with the lockout message
(proves the check runs before auth, not after another failed attempt);
a successful login clears the counter — logged back out and failed
twice more, then logged in immediately after, no lockout. `ActivityLog`
rows confirmed for both `LOGIN_FAILED` and `LOGIN_BLOCKED`.

## Found while testing, fixed in the same pass: Django's default `invalid_login` error was still literal English

Phase 7 localized `LoginForm`'s field *labels* but not
`AuthenticationForm.error_messages['invalid_login']`/`'inactive'` —
those still rendered Django's stock English text (same `USE_I18N =
False` root cause as every other instance of this bug fixed so far).
Caught because this phase's own Playwright pass exercises repeated
failed logins and reads the error text on every one. Overridden in
`LoginForm.error_messages` — deliberately *not* using Django's own
`%(username)s` placeholder in the message, since that gets filled from
the User model field's `verbose_name` ("username"), not this form's
Azerbaijani label override, so it would've rendered literal English
either way; hardcoded "istifadəçi adı" directly into the string instead.

# Phase 16 (social links: fixed fields → flexible CRUD list)

## Why this replaced, rather than extended, the Phase 8 fields

`SiteSettings.social_facebook/instagram/twitter/youtube` (4 fixed
`URLField`s, Phase 8) already displayed on the public site and were
already editable in CMS Settings — functionally "done" by CLAUDE.md
ch.9's letter. User asked specifically for add/edit/delete as three
distinct actions on an open-ended set of platforms (Telegram, WhatsApp,
etc.), confirmed via `AskUserQuestion` against the alternative of just
adding 1-2 more fixed fields — a fixed set, however large, still needs a
code change and a migration every time a newsroom wants a platform that
isn't already listed, which is exactly the constraint being removed.

## New `SocialLink` model, same shape as `Tag`

`apps/settings_app/models.py`'s new `SocialLink(BaseModel)` follows
`Tag`'s (`apps/tags/models.py`) precedent closely: flat list, no
hierarchy, **hard delete** (not in CLAUDE.md ch.10's soft-delete list —
a link is trivial to re-add, recovery machinery would be pure overhead).
`platform` is a fixed `TextChoices`, not free text — deliberately, so
the CMS never requires an editor to know or type a CSS icon class name
(CLAUDE.md ch.9 "must never be designed for technical users only"). The
11 choices (10 named platforms + `OTHER`) and their icon-class mapping
were checked against the actually-bundled `static/vendors/bootstrap-
icons/bootstrap-icons.css`, not assumed from the library's public docs —
confirmed present: facebook, instagram, twitter-x, youtube, telegram,
whatsapp, linkedin, tiktok, pinterest, threads, plus `link-45deg` as
`OTHER`'s fallback so an unlisted platform still gets a sane icon
instead of a broken one. `order` is a plain integer field editable in
the form, not drag-and-drop — the list is short (a handful of rows in
practice), so `Category`'s full DnD reorder machinery
(`CategoryReorderView`) would be solving a problem this list doesn't
have (CLAUDE.md ch.15 "avoid unnecessary abstraction").

## Three-migration split for a clean field→model data move

Doing "add `SocialLink`" and "remove the 4 old fields" as one migration
would drop any existing URLs with no path to recover them. Split into
three, in dependency order:
1. `0003_add_social_link` — create the table (generated first, with the
   4 old fields still in the model, then temporarily restored after a
   premature edit removed them too early — worth noting only because it's
   *why* the migration numbers aren't contiguous with a naive single-shot
   generation).
2. `0004_migrate_social_link_data` — hand-written `RunPython`, one
   `SocialLink` row per non-blank old field, both forward and backward
   (`migrate_social_links_backward` collapses back into the 4 fields, so
   `migrate settings_app 0003` remains a real, working rollback target).
3. `0005_remove_social_fields` — drops the 4 old columns, generated
   last so it only runs after data has somewhere to land.

Verified against the actual dev database (all 4 fields were empty at
migration time, confirmed via shell before writing the data migration)
— the logic itself doesn't depend on that emptiness and handles
populated fields the same way; it just means this particular run had
nothing to move.

## CMS screen reachable from Settings, not a new sidebar item

`apps/cms/views/social_link.py` — List/Create/Update/Delete, modeled on
`apps/cms/views/tag.py` minus search/pagination (short list) and minus
`Tag`'s usage-count delete warning (a `SocialLink` has no dependent rows
anywhere in the schema, unlike a `Tag` with articles attached).
`AdministratorRequiredMixin` — same access tier as `SettingsUpdateView`,
since this is the same category of site-wide, sensitive configuration.

CLAUDE.md ch.9's sidebar order is fairly fixed and doesn't list a social-
links item — rather than add a new top-level entry for a small, rarely-
touched feature, `templates/cms/settings.html`'s old 4-field "Sosial
şəbəkələr" section became a link card pointing at `cms:social_link_list`
(new `.cms-settings-card--link` modifier, `static/css/cms/settings.css`)
— one click from the screen an admin would already be on for this kind
of setting, no sidebar clutter.

## Public rendering: one context-processor addition, not per-view plumbing

`apps/core/context_processors.py`'s `site()` already injects
`site_settings`/`main_categories` into every public page's context —
added `social_links` (`SocialLink.objects.all()`, already ordered via
`Meta.ordering`) there too, so `templates/components/footer.html`
needed no view changes anywhere, just its own template logic: the old 4
hardcoded `{% if site_settings.social_x %}` blocks collapsed into one
`{% for link in social_links %}` loop rendering `link.icon_class`/
`link.get_platform_display`.

## Verification

Playwright, logged in as Administrator: confirmed the old fields are
gone from the Settings form and the new link card is present; created 3
links (Facebook, Telegram, and one `OTHER` pointing at a made-up domain,
specifically to exercise the fallback icon path) via the new CMS screen;
edited one, deleted one; confirmed `ActivityLog` rows for all three
action types. Public homepage footer inspected directly (Django test
client, not just Playwright) — all three links rendered in `order`, with
the correct icon classes, `OTHER` correctly falling back to
`bi-link-45deg`. `manage.py check` and `makemigrations --check` clean
throughout. Test rows and their activity-log entries removed afterward.

# Phase 17 (contact form English leak, CKEditor image distortion, empty categories in nav, upload size hints)

## Contact form: same `USE_I18N=False` English leak, fourth time found

`apps/pages/forms.py`'s `ContactForm` had Azerbaijani field *labels* but
no `error_messages` overrides, so Django's built-in validation text
("This field is required.", "Enter a valid email address.") rendered as
literal English — the same root cause as `LoginForm`/`PasswordResetForm`/
`SetPasswordForm` (Phase 7) and `AuthenticationForm.error_messages`
(Phase 15). Every field now gets an explicit override; a `_REQUIRED_
MESSAGE`/`_MAX_LENGTH_MESSAGE` dict pair avoids repeating the same two
strings across all four fields. At this point four separate forms have
hit this exact bug independently — worth checking any *future* form
against it up front rather than waiting for another report.

## CKEditor inline images rendered squashed on the public site — root cause found by comparing editor vs. public rendering, not by reading CSS

User reported a 1024×1024 upload displaying as roughly 257×1024 on an
article page. Reproduced with a real synthetic 1024×1024 PNG (not
assumed from the report) and checked the *same* image's rendered
`getBoundingClientRect()` at three points: in the editor immediately
after upload (593×593 — correct), in the editor after a save+reload
(593×593 — still correct), and on the actual public article page
(**780×1024 — wrong**). Only the public render was broken, which
immediately ruled out the upload pipeline, CKEditor itself, and the
saved HTML (all three already correct) and pointed at `static/css/
components/rich-text.css` specifically.

Root cause: `.rich-text-content figure.image img { width: 100%; }` had
no `height` rule, relying on the `style="aspect-ratio: W/H"` CKEditor
stamps on every inserted `<img>` to auto-compute height from the
definite `width: 100%`. But that same `<img>` also carries literal
`width="1024" height="1024"` *HTML attributes*, and browsers map an
element's `height` attribute to a low-specificity implicit height
style — since nothing in the stylesheet ever set `height` to override
that mapped attribute, the computed height stayed a *second, separate*
definite value (1024 real pixels) instead of `auto`. With both width
and height already definite from two unrelated sources, `aspect-ratio`
has nothing left to resolve and is silently ignored — the image renders
at the container's width and the original's raw pixel height,
independent of each other. Fixed with one line, `height: auto;`, which
makes the computed height genuinely `auto` again so `aspect-ratio` can
do its job. Verified with both a square (1024×1024 → renders 1.000
ratio) and a 16:9 image (1600×900 → renders 1.778 ratio) side by side in
the same article.

## Categories with zero published articles no longer appear in the public nav

`apps/core/context_processors.py`'s `site()` already builds
`main_categories` for every public page's header — added an `Exists`
subquery filter (not per-category `.exists()` calls, which would be a
real N+1 across however many top-level categories exist) so a category
only appears if it — or, for a top-level category, any of its
subcategories — has at least one published article
(`News.objects.published()`, the same queryset method `NewsQuerySet.
in_category()` already uses for category pages, reused here rather than
reimplemented). Applied at both levels: an empty top-level category is
dropped entirely, and within a category that *does* qualify, its own
empty subcategories are separately filtered out of the dropdown — a
parent with one populated and one empty child shows only the populated
one. Verified with two throwaway test categories (one empty top-level,
one empty child under a real populated parent) confirming both cases,
then removed.

## Every image-upload field in the CMS now states its recommended size

None of the six `media-picker` locations across the CMS (News cover
image, News/Page OG image, Settings logo/favicon, Ad banner) told an
editor what size to upload before this — some had a hint with no
dimensions, most had no hint at all. Added a concrete recommendation to
each, sized to how the image actually gets used rather than a generic
number:
- News cover image: 1200×675 (matches the picker's own configured
  `data-aspect-ratio="1.7777777778"`, i.e. 16:9).
- News/Page OG image: 1200×630, the standard Open Graph preview size.
- Settings favicon: 512×512 (matches its `data-aspect-ratio="1"`).
- Settings logo: no fixed ratio (none was ever enforced here), so a
  qualitative recommendation instead — transparent PNG/SVG, ≥120px tall.
- Ad banner: rather than hardcode a pixel size, the hint points at the
  `position` field's own selection — `AdPosition.__str__` already
  renders each dropdown option as `"Name (W×H)"`
  (`apps/advertisements/models.py`), so the real number is always
  correct even if new positions with different dimensions get added
  later, instead of a hint that could silently go stale.
- CKEditor inline body images (both News and Page): 1200px width,
  next to the content field itself, since this upload path has no
  single fixed aspect ratio to point at.

# Phase 18 (CMS sidebar and Media Library folders now stay in view while scrolling)

## Both were plain flex children with no scroll-independent positioning

User reported two symptoms that turned out to share one root cause:
the Media Library's folder panel scrolling out of view on a long file
grid, and the "Tənzimləmələr" sidebar link ending up further down the
page the longer that page got. `.cms-sidebar` (`static/css/cms/
shell.css`) had no `position: sticky`/`fixed` at desktop widths — it's
a plain flex sibling of `.cms-main` inside `.cms-shell`, so it stretches
to match `.cms-main`'s height on any page taller than the viewport. Its
bottom-pinned item (`.cms-sidebar__item--bottom`, `margin-top: auto`)
is positioned relative to that *stretched* box, not the viewport — on
a tall page the box itself extends far down, dragging the bottom-pinned
link down with it. Same underlying issue, one level down, for
`.media-folders` (`static/css/cms/media.css`): `align-self: stretch`
matches it to `.media-main`'s height, but nothing kept its *visible*
position anchored to the viewport while the page scrolled.

## Fix: `position: sticky` on both, not a scroll-container restructure

Added `position: sticky; top: 0; height: 100vh; overflow-y: auto;` to
`.cms-sidebar` and the same shape (`max-height` instead of `height`,
since its content is usually much shorter) to `.media-folders`. Kept
the mobile off-canvas override (`position: fixed`, Phase 13) — a
media-query rule with a matching condition still overrides an earlier
unconditional `sticky` rule by ordinary cascade order, confirmed by
re-testing the mobile drawer afterward, not assumed safe from reading
the rule order.

Verified by scripted scrolling (not just resizing the viewport and
looking): logged in, scrolled a media-heavy page and a separately a
plain News list 1500-2000px down, and confirmed via
`getBoundingClientRect()` that the sidebar, the folders panel, and the
"Tənzimləmələr" link all stayed within the viewport bounds after the
scroll — the exact measurement that would have caught this bug before
shipping it. Mobile off-canvas drawer re-checked afterward, unaffected.

# Phase 19 (permanently deleting a news article now cleans up its media; one-time project data wipe)

## Media attached to an article only gets deleted at permanent-delete time, never at soft-delete time

News delete was already soft-delete-only (`is_deleted` + `NewsRestoreView`,
CLAUDE.md ch.10 "Deleted records should remain recoverable") with no hard-delete
path at all. The user wanted an article's attached media (cover image, OG
image, and any image inserted inline into the CKEditor body) removed along
with it — but doing that at soft-delete time would leave a later restore
showing an article with broken images, since a soft-deleted row is meant to
stay fully recoverable. Resolved by adding a genuine hard-delete action,
reachable only from the "Silinənlər" (trash) tab, and hanging the media
cleanup off that instead: `NewsPermanentDeleteView`
(`apps/cms/views/news.py`) — `get_object_or_404(News, pk=pk, is_deleted=True)`
so it can only ever fire on a row already in the trash.

`apps/media_manager/services.py` gained three functions supporting this:
- `collect_news_media_ids(article)` — called *before* the article is
  deleted, returns every `MediaFile` id potentially exclusively owned by
  it: `featured_image_id`, `og_image_id`, plus every inline `<img src="…">`
  found in `article.content` via regex, matched back to `MediaFile` rows by
  stripping `settings.MEDIA_URL` from the path (inline body images have no
  FK — CKEditor just writes a `<img src>` URL into the stored HTML — so this
  is the only way to find them).
- `delete_unused_media(media_ids)` — after the article row is actually
  gone, deletes every collected id whose `MediaFile.usage_count` (already
  existing, checks News/Advertisement/SiteSettings references) is now zero.
  A cover image shared by a second article, an ad banner, or the site logo
  survives; only a truly orphaned file is removed.
- `delete_media_file(media_file)` — extracted from the existing
  `MediaDeleteView` (which now calls it too, instead of duplicating the
  same delete-row-then-delete-files logic) so both the manual media-library
  delete and this automatic cleanup path stay in sync.

Logged as a new `ActivityLog.Action.ARTICLE_PURGED`, with the deleted media
count appended to the description (e.g. `"Title (+ 2 media fayl)"`) when
anything was actually removed.

New UI: `templates/cms/news_confirm_permanent_delete.html` (a
`.cms-confirm` page, same shape as every other confirm screen) reachable
from a "Həmişəlik sil" button that now sits next to "Bərpa et" on each
trash-tab row (`.cms-table__actions-group`, `static/css/cms/editor.css`).
Needed a new `.btn--danger` (`static/css/components/buttons.css`) — the
existing `.btn--secondary` is an outline style already used for "Bərpa et"
here, and `--color-danger` happens to equal `--color-primary` in value, so
a solid-fill variant was the only way to visually separate the "safe"
action from the "destructive" one on the same row.

Verified end-to-end with a real two-article scenario, not just by
reasoning about the code: two articles sharing one cover image — purging
the first left the image intact (second article still referenced it);
purging the second then correctly deleted the now-unused `MediaFile` row
*and* its on-disk file. Repeated separately for an inline body image
(uploaded through the CKEditor toolbar, not the cover-image picker) to
confirm the regex-based path also works, since that path has no FK to
fall back on.

## One-time project data wipe: all News, Folders and MediaFiles removed; four static pages left untouched

Separate from the feature above — a one-time cleanup, not new
functionality, so no management command was added for it (a permanent
"wipe all content" command sitting in the codebase would be a standing
footgun for a single use). Run directly via `manage.py shell`:
`Advertisement.objects.all().delete()` (the only model with `on_delete=
models.PROTECT` toward `MediaFile`, via `Advertisement.banner` — had to go
first or every `MediaFile` delete below would raise `ProtectedError`;
confirmed with the user this test ad should go too), then
`News.objects.all().delete()` (a real hard delete — `News` has no custom
manager overriding `.delete()`, `is_deleted` is only ever toggled from CMS
views, so the plain queryset method deletes rows for real, trash included),
then `Folder.objects.all().delete()`, then every `MediaFile` individually
through `delete_media_file()` (not a bulk `.delete()`, which would drop the
DB rows but leave the on-disk files behind).

Checked before running, not assumed: every FK that can point at a
`MediaFile` (`SEOFieldsMixin.og_image`, `SiteSettings.logo`/`favicon`,
`News.featured_image`, `Advertisement.banner`) — all `SET_NULL` except the
`Advertisement` one already handled above. Confirmed the four pages the
user asked to preserve (Haqqımızda, Əlaqə/Contacts, İstifadə şərtləri,
Məxfilik siyasəti) have zero exposure either way: three are plain `Page`
rows with `og_image=None` and no inline content images, and Contacts isn't
a `Page` row at all — `ContactView` is a bare `FormView` that only sends an
email, no stored content to lose.

Also removed a handful of files under `media/uploads/` and `media/temp/`
that had no corresponding `MediaFile` row at all (leftover from
staged-but-never-finalized uploads, predating this cleanup) — the bulk
delete above only walks rows that exist in the database, so these needed a
direct filesystem check to catch.

Verified after: `Page`/`Category`/`Tag` counts unchanged; all four
protected pages return 200 with correct content; `media/` contains nothing
but the tracked `.gitkeep`; CMS News list and Media Library both render
their empty states rather than erroring. One gap surfaced by testing
against a fully empty database, out of scope for this cleanup and left
as-is: the public homepage (`templates/news/home.html`) has no "no
articles" empty state — `{% if hero %}` and `{% for section in
category_sections %}` simply render nothing, leaving blank space instead
of a message, which existing CLAUDE.md guidance calls for but which the
homepage template was never actually built to do at zero-content.

# Phase 20 (breaking-news ticker becomes a real marquee; active nav state; mobile social links; view counter surfaced)

## View counter was tracked but never displayed

`News.view_count` was already incremented correctly (session-deduped) and
used to rank "Ən çox oxunan," but no template ever rendered the number —
CLAUDE.md ch.11's "Standard News Card" spec requires it. Added to
`components/news_card.html` (icon + count next to the timestamp) and
`news/detail.html` (appended to the existing date/reading-time line).

## Breaking ticker: single crossfading headline → true horizontal marquee

The first version of the ticker (this phase started from) rotated one
headline at a time via a JS `setInterval` swapping an `is-active` class.
User asked for a continuous horizontal scroll instead, with a lightning
icon per headline and no more static "TƏCİLİ"/"Canlı" badge text.

Rebuilt as a CSS-only marquee: `templates/components/breaking_ticker.html`
renders every breaking article **twice**, back to back, inside
`.breaking-ticker__track`; `@keyframes breaking-ticker-scroll` animates
`transform: translateX(0 → -50%)` on an infinite loop — since the two
copies are identical, translating by exactly half the track's total
width means the loop restarts with the visible content unchanged, no
visible jump. Pausing on hover is plain CSS
(`.breaking-ticker:hover .breaking-ticker__track { animation-play-state:
paused; }`) — no JS needed for that part at all. `static/js/components/
breaking-ticker.js` only sets `animation-duration` from a
server-computed value (`apps/news/views.py`'s `HomeView` — `max(18,
len(breaking_articles) * 6)` seconds), so scroll *speed* stays constant
regardless of how many headlines are queued instead of a fixed duration
making 2 headlines crawl and 8 whip past unreadably fast.

Each headline gets a `bi-lightning-charge-fill` icon before the title.
The duplicate second copy is `aria-hidden="true"` with `tabindex="-1"`
links, so screen readers and keyboard navigation only ever see one real
copy.

One bug found and fixed mid-build: once every `.breaking-ticker__item`
became `position: absolute` (for the crossfade version) or moved into a
flex row (for the marquee), the wrapping elements had no normal-flow
content left to size themselves against and collapsed to zero height —
invisible to Playwright's actionability checks (and to real mouse
hover, since a zero-height box can't be hovered) despite the text still
painting. Fixed with an explicit `height: 100%` chain down from the
ticker's own fixed `36px`.

## Active navigation state

Only "Ana səhifə" ever got an `is-active` class before this phase —
category links, subcategory dropdown links, and the "Daha" static-page
group never indicated the current section, leaving readers without any
sense of where they were on the site.

`apps/categories/views.py`'s `CategoryDetailView` and `apps/news/views.py`'s
`NewsDetailView` now also set `context['nav_active_category']` (the
category being browsed, or the current article's category).
`templates/components/header.html` compares this against each nav
category/subcategory (`nav_active_category.pk == category.pk` — or
`.parent_id == category.pk`, so a subcategory page also highlights its
parent). The four static pages ("Daha" dropdown) use a simpler check —
`request.resolver_match.namespace == 'pages'` for the parent toggle, an
exact `url_name`/`kwargs.slug` match for the specific link — since they're
a small, fixed, known set already routed through one Django app
namespace. `.nav__dropdown-link.is-active` is a new CSS rule
(`static/css/components/dropdown.css`); `.nav__link.is-active` already
existed and just needed to actually get applied.

## Social icons no longer disappear on mobile

`static/css/responsive/mobile.css` hid `.site-header__social` outright
below 768px with no replacement — a direct violation of CLAUDE.md ch.6
("Never hide critical functionality on smaller screens"), caught when
asked to look at it, not something the user had to find. Fixed by
duplicating the same links into the off-canvas mobile nav drawer
(`.nav__social`, new markup in `components/header.html`), hidden by
default (`static/css/layout/navigation.css`) and revealed only inside
the same `max-width: 768px` block that hides the topbar copy — so
exactly one copy is ever visible at any width.

## Verification

Playwright throughout: ticker duplication/scroll/pause/resume/click-
through, nav `is-active` on category/subcategory/article/static pages,
mobile menu open/closed social-link visibility toggling correctly
against the same breakpoint the topbar hides at. All confirmed via
scripted `getComputedStyle`/`getBoundingClientRect` checks, not visual
inspection alone — the zero-height bug above would not have been obvious
from a screenshot at a moment the animation happened to be mid-frame.

# Phase 21 (a real automated test suite; prepared for GitHub → Hostinger VPS deployment)

## Context

Every one of the 19 prior phases was verified by hand — one-off
Playwright scripts written to a scratch directory, run once, discarded.
Every app's `tests.py` was still the untouched three-line Django stub.
The project also wasn't a git repository at all. None of that is
compatible with actually running this on a VPS: nobody re-verifies 19
phases by hand before every deploy, and there's nothing to push to
GitHub in the first place. This phase built a real, repeatable test
suite across three layers and the full path from `git push` to a
running production site.

## Backend — pytest (107 tests, ~84% coverage of `apps/`)

`requirements/development.txt` gained `pytest`, `pytest-django`,
`pytest-cov`, `factory-boy`, `locust` (dev-only, never in
`requirements/production.txt`). New `config/settings/test.py` (inherits
`development.py`; fast password hasher; `MEDIA_ROOT` redirected to
`test_media/` so upload-pipeline tests never write into the real
`media/` folder this project already had to clean by hand once).
`pytest.ini` at the repo root; root `conftest.py` holds the shared
fixtures (`administrator`, `journalist`, `admin_client`,
`category`/`subcategory`, `published_news`/`draft_news`,
`sample_image_bytes`/`sample_image_file`, `media_file`).

Per-app tests cover: CMS permission boundaries (every list/overview
screen, parametrized — anonymous redirected, non-admin gets 403 on the
Administrator-only screens, admin gets 200 everywhere); the News
lifecycle and its permanent-delete media cleanup (the exact
shared-vs-exclusive-media scenario manually verified in Phase 19, now
locked in by a test instead of memory); category hierarchy and the
empty-category nav-hiding logic; the upload pipeline's validation
(size/type/corrupted-file rejection); `MediaFile.usage_count` across
News/Advertisement/SiteSettings; one CRUD smoke test per CMS-managed
model with an `ActivityLog` assertion; the public views (home, article,
category pagination, search, sitemap, robots.txt); `ContactForm`'s
Azerbaijani error messages.

**Three real bugs found while writing these tests, all fixed**:

1. **Slug generation could produce an empty or colliding slug.**
   `News`/`Page`/`Category`/`Tag` all did `if not self.slug: self.slug =
   az_slugify(...)` with no uniqueness check and no fallback for text
   `az_slugify` can't transliterate (non-Azerbaijani/non-ASCII input
   slugifies to `''`). Two articles with the same title crashed with an
   unhandled `IntegrityError` at `INSERT` time — *after* `ModelForm`
   validation had already passed, since the form validates the
   still-blank slug field, not the value `save()` fills in afterward.
   Fixed with one shared helper, `apps/core/utils.py`'s
   `generate_unique_slug()` — appends `-2`, `-3`, ... on collision, falls
   back to a random 8-char hex when slugify itself yields nothing — used
   by all four models instead of the raw `az_slugify()` call each had.

2. **A corrupted/fake image file crashed upload validation.**
   `apps/media_manager/services.py`'s `_validate_upload()` called
   `Image.open(uploaded_file)` with no exception handling around it — a
   file with an image extension/content-type but bytes that aren't
   actually a valid image raised an unhandled `PIL.UnidentifiedImageError`
   (a real 500 to the user, violating CLAUDE.md ch.5/12 directly). Now
   caught and re-raised as the same friendly `ValidationError` already
   used for outright-disallowed formats.

3. **`pytest.ini`'s own `python_files = test_*.py` silently excluded
   every `tests.py`** (Django's own convention, used by six of this
   project's apps) **from collection** — only the newer `test_*.py`
   files inside `apps/news/tests/` and `apps/cms/tests/` ever ran.
   40 of the first 107 tests written were never actually executing.
   Fixed by adding `tests.py` to the pattern
   (`python_files = test_*.py tests.py`) — caught by comparing the
   suite's own reported test count against a manual tally, not assumed
   correct because "pytest didn't error."

## Frontend — Playwright (e2e/), a committed suite instead of scratch scripts

New `e2e/` directory: `package.json` (`@playwright/test`, dev-only, never
shipped), `playwright.config.js`, six spec files (`home`, `article`,
`cms-auth`, `cms-news`, `contact-form`, `mobile-nav`).

Runs against a **dedicated `config/settings/e2e.py`** — its own database
(`news_db_e2e`, distinct name enforced by a safety check in the
bootstrap command) and its own Redis logical DB (index 3, separate from
development's index 1), never the developer's real `news_db`, which by
this point holds genuine editorial content. `apps/core/management/
commands/bootstrap_e2e_db.py` creates the database if missing (via a
direct `psycopg` connection to Postgres' `postgres` maintenance
database — `CREATE DATABASE` can't run inside Django's ORM/transactions),
migrates, flushes, and reseeds one administrator
(`e2e_admin`/`E2E-test-password-123`), one category, one social link.
`e2e/global-setup.js` runs this once per `playwright test` invocation,
so every run starts from the same known state. `playwright.config.js`'s
`webServer` starts `manage.py runserver` under these settings
automatically — `npx playwright test` is self-contained.
`workers: 1` — every spec shares one server/database, so parallel
workers would race each other's writes.

**A genuine production bug found by the `cms-news.spec.js` restore test,
unrelated to the test infrastructure itself**: `templates/cms/
news_list.html`'s trash-tab "Bərpa et" (restore) button and the
"Dublikat et" (duplicate) button were each wrapped in their own
`<form>` — nested inside the *outer* `<form id="bulk-form">` that wraps
the whole table for bulk-select actions. HTML forms cannot nest; browsers
silently drop the inner `<form>` start tag per the HTML5 parsing
algorithm, and the button ends up submitting the *outer* bulk-action
form instead. The button appeared to work (page reloaded, no error) but
never actually restored or duplicated anything — confirmed by querying
the database directly after a "successful" test run and finding
`is_deleted` still `True` and no `ARTICLE_RESTORED` entry in
`ActivityLog` at all. This had been sitting unnoticed since Phase
19/whenever bulk actions were added, because manual verification only
ever checked that the button was *visible*, never that clicking it
produced the expected end state. Fixed using the HTML5 `form="..."`
attribute — each button now references a standalone `<form id="restore-
form-{{ pk }}">`/`<form id="duplicate-form-{{ pk }}">` rendered *after*
the bulk-form closes, associating the button with the right form
regardless of DOM nesting. Checked every other CMS list template
(`category_list.html`, `ad_list.html`, `user_list.html`, ...) for the
same pattern — none of the others wrap their table in an outer form at
all (only the news list has bulk actions), so this was an isolated bug,
not a systemic one.

Two smaller Playwright fixes along the way: `force: true` needed on
hover/click actions targeting the continuously-animating ticker (its
"element is stable" actionability check never passes on a moving
target, same as a real mouse doesn't need that guarantee); a
`waitForURL('**/xeberler/**')` glob matched the *current* URL before a
redirect even happened (every relevant URL in that flow contains
`/xeberler/`), so it resolved immediately instead of waiting — replaced
with `Promise.all([waitForURL(precise-predicate), click()])` pairing
everywhere a click triggers a redirect this suite depends on.

## Load — Locust (stress_tests/locustfile.py)

`ReaderUser` (weight 8 — the realistic majority of real traffic) never
hardcodes a slug: each task loads the homepage and regex-extracts a
real `/category/.../` or `/news/.../` link from what actually rendered,
so the same file works against any host with any content instead of
breaking the moment seed data changes. `CmsStaffUser` (weight 1) only
performs a real login when `LOCUST_CMS_USERNAME`/`LOCUST_CMS_PASSWORD`
are set in the environment — otherwise it just repeats the anonymous
`/cms/` redirect, since a real login needs credentials for whatever
specific host/account this is pointed at. Smoke-tested locally (5 users,
12s) against a real dev server with real content: 0 failures, category/
article links correctly discovered and hit.

## Deployment — classic venv + systemd + Nginx (user's explicit choice over Docker)

New `deploy/` directory: `gunicorn.service` (unix socket, not a TCP
port — only Nginx ever talks to it), `celery-worker.service`,
`nginx.conf` (static/media served directly by Nginx, `/media/temp/`
explicitly denied per CLAUDE.md ch.12, HTTPS added afterward by
`certbot --nginx` rather than hand-maintained here), `deploy.sh` (pull →
install → migrate → collectstatic → restart both services → curl the
homepage and fail loudly if it isn't 200). No `celery-beat.service` —
confirmed via grep that nothing in the project defines
`CELERY_BEAT_SCHEDULE` anywhere; scheduled publishing is a query-time
filter (`News.objects.published()`), not a periodic task, so a Beat
service would be infrastructure with nothing to run.

`.github/workflows/ci.yml` runs pytest and the full Playwright suite
(Postgres + Redis service containers) on every push/PR. Deployment
itself stays manual — the user's explicit choice over auto-deploying via
SSH from CI — so this workflow never touches the VPS and needs no
deploy secrets.

`docs/DEPLOYMENT.md` (VPS provisioning + update runbook), `docs/
TESTING.md` (how to run all three test layers), root `README.md`
(quickstart) are new. The project was `git init`'d for the first time
this phase and pushed to `https://github.com/emineliyev/spress.git`.

## Verification

`pytest --cov=apps` — 107 passed, ~84% coverage. `npx playwright test`
(e2e/) — 15 passed. Locust — 5 simulated users, 12s, 0 failures against
a real dev server. `python manage.py check` and `makemigrations --check
--dry-run` clean throughout (the slug-generation fix touched only
Python logic, no schema change).

# Phase 22 (ad slot conflicts blocked; permanent delete for Category/Advertisement; pick-from-library image picker)

## Context

Three gaps the user found using the CMS directly, after Phase 21's test suite and deploy prep: two silent-failure-shaped bugs and one workflow gap.

## Ad slots: a second active campaign in the same position used to win silently

`{% ad_slot %}` (`apps/advertisements/templatetags/ads.py`) has always just
picked `Advertisement.objects.active().filter(position__code=...).order_by
('-created_at').first()` — nothing anywhere validated that only one
campaign should be simultaneously active per position. Create a second
active campaign in the same slot without realizing the first was still
running, and the first one silently stops rendering — no error, no
warning, just a banner that quietly changed. User chose blocking over
auto-deactivation (a plain "we handled it for you" felt riskier than
making the conflict visible).

`AdvertisementForm.clean()` (`apps/advertisements/forms.py`) now checks,
whenever `position` + `is_active` + `start_date` are all set, every
*other* `visible()` campaign in the same position for a date-range
overlap (`_ranges_overlap()`, a small helper treating a `None` end date
as "no upper bound" rather than needing a sentinel "infinity" value) —
on a hit, `self.add_error('position', ...)` names the conflicting
campaign by title so the editor knows exactly what to deactivate first.
Scoped to `is_active=True` campaigns only (a draft/paused campaign
sharing a position is fine) and excludes `self.instance.pk` (editing a
campaign doesn't conflict with its own unchanged record).

## Permanent delete extended to Category and Advertisement

News already had this (Phase 19) — Category and Advertisement's trash
tabs showed "Bərpa et" with no way to actually clear an item out.
`CategoryPermanentDeleteView`/`AdPermanentDeleteView`
(`apps/cms/views/category.py`, `apps/cms/views/advertisement.py`) copy
`NewsPermanentDeleteView`'s GET-confirm/POST-delete shape exactly, at
`.../hemise-sil/` (`cms:category_permanent_delete`,
`cms:ad_permanent_delete`), with a `Həmişəlik sil` button added next to
`Bərpa et` in both trash-tab templates (neither `category_list.html`
nor `ad_list.html` wraps its table in a bulk-action `<form>` the way
`news_list.html` did — confirmed before adding a plain link button here,
not assumed safe from Phase 21's nested-form bug).

Category needed more care than News did: `News.category` is
`on_delete=PROTECT` and `Category.parent` is `on_delete=CASCADE` — a
naive `category.delete()` would either raise an unhandled
`ProtectedError` (a linked article, even a soft-deleted one, still holds
the FK) or silently cascade-delete child categories. Both are checked
explicitly against *every* row first (not just `.visible()` ones — a
soft-deleted News or Category can still hold the reference), blocking
with a clear count-based message rather than either failing loudly or
deleting more than the admin asked for. Advertisement is simpler (only
its own `banner` to worry about) and mirrors News's media-cleanup
pattern directly: capture `banner_id` before `ad.delete()`, then
`delete_unused_media({banner_id})` (`apps/media_manager/services.py`,
already built in Phase 19) removes it only if nothing else still
references it.

New `ActivityLog.Action.CATEGORY_PURGED`/`AD_PURGED` (+ migration).

## Media picker: choosing an existing image, not just uploading a new one every time

Every "Şəkil seçin" button (News cover/OG, Page OG, Settings logo/
favicon, Ad banner — all sharing `static/js/cms/image-pickers.js`) used
to go straight to the OS file dialog. Reusing an already-uploaded image
meant downloading it and re-uploading it, or wasn't really possible at
all — and every fresh upload duplicated storage for an image already in
the library.

New shared modal, `templates/cms/partials/media_picker_modal.html`
(one singleton per page, included next to the existing
`media_crop_modal.html` on every page with a picker — `news_form.html`,
`page_form.html`, `ad_form.html`, `settings.html`), two tabs:

- **"Kitabxanadan seç"** (default) — `apps/cms/views/media.py`'s new
  `MediaPickerListView(MediaLibraryListView)` reuses the existing
  view's filtering/pagination untouched, just a lighter
  `template_name` (`cms/partials/media_picker_grid.html` — adapted from
  the existing `media_grid.html`, whose own comment had already
  anticipated this reuse since Phase 10: *"a future picker-from-library
  view can reuse it without duplicating card markup"*). Cards are
  `<button data-action="pick-media">` instead of management-menu `<div>`s
  — clicking one sets the picker's hidden input and preview directly,
  no crop step, since a library image is already processed. Search and
  the format filter re-`fetch()` the grid in place; pagination links
  inside the fetched HTML are intercepted the same way (read the raw
  `href` query-string, refetch against the *picker's own* URL) rather
  than left to navigate normally — a plain anchor's `.href` resolves
  against the page's own address, not the fetched fragment's original
  one, so navigating it directly would silently target the wrong page
  once injected into e.g. `/cms/xeberler/yeni/`.
- **"Yeni yüklə"** — the exact same stage→crop→confirm pipeline as
  before, just triggered from inside the modal: the picker modal hides
  itself before the crop modal opens (confirmed via Playwright, not
  assumed — no double-modal stacking), and `MediaUploader`'s existing
  "singleton, rebind `onComplete`/`defaultRatio` before each use"
  pattern (already established for reusing one uploader instance across
  multiple pickers on a page) now also carries the *currently open*
  picker's identity through the modal correctly.

`image-pickers.js` was rewritten around a single `currentPicker` module
variable, set when any picker's "Şəkil seçin" is clicked and read by
both tabs — verified with Playwright that two pickers on the same page
(News has featured_image *and* og_image) never cross-contaminate each
other's hidden input, since both tabs ultimately read/write through
whichever picker was opened last.

## Verification

`pytest`: 6 new `AdvertisementForm` tests (blocked/allowed/inactive-
doesn't-conflict/editing-self-doesn't-conflict) and 7 new permanent-
delete tests (`apps/cms/tests/test_permanent_delete.py`, including the
Category-blocked-by-referencing-News case that would otherwise raise
`ProtectedError`) — 120 passed total, `manage.py check` and
`makemigrations --check --dry-run` clean.

Playwright (manual scripts, not yet folded into `e2e/`): picker modal
opens showing all 9 real library files; nonsense search → empty state,
clearing it restores the grid; clicking a card closes the modal and
sets the correct hidden input/preview; switching to "Yeni yüklə",
uploading, and applying a crop closes both modals and updates the
picker with the newly created media, with the featured-image picker's
16:9 aspect ratio correctly pre-selected in the crop panel; two pickers
on one page (featured_image/og_image) confirmed to track independently.
Test article/media created during verification cleaned up afterward
(no state left in the dev database, which by this phase holds genuine
editorial content, not just test rows).

# Phase 23 (SEO field hints; two real bugs behind the reported YouTube "Error 153")

## SEO panel fields now explain themselves

User asked for plain-language explanations of "OG başlıq / Canonical URL /
OG təsvir / OG şəkli" — jargon a non-technical editor has no reason to
already know (CLAUDE.md ch.9 "must never be designed for technical users
only"). Added an `.editor__hint` under every SEO field in both
`news_form.html` and `page_form.html` (identical field set via
`SEOFieldsMixin`) plus one summary sentence at the top of the section,
each explaining what the field actually controls rather than just its
name — e.g. "OG başlıq" → *""OG" = Open Graph. Sosial şəbəkədə
paylaşılanda linkin üzərində görünəcək başlıq."*

## Reported bug: inserted YouTube videos show "Xəta 153 / Video pleyer konfiqurasiya xətası"

Investigated by reproducing it directly rather than guessing — created a
real article through the CMS with an embedded YouTube video and viewed
it publicly. Two unrelated real bugs turned up, not one.

**Bug 1 — `.article__body` collapses to zero width for text-light
content.** `static/css/pages/article.css`'s `.article__layout` is a flex
row (share-icon column + main content); `.article__body` had `max-width:
780px` but no `flex-grow`/`flex-basis`, so its actual width fell out of
its own content's intrinsic sizing. For ordinary paragraph text this
happens to converge on something reasonable (text has real min/max-
content width to shrink from), which is why this had never surfaced
before — but a body whose only content is an `aspect-ratio`-sized video
embed has no intrinsic width to compute from at all, and the whole
element, and everything inside it (`.rich-text-content`, `.media-embed`,
the iframe itself), collapsed to `0×0` — confirmed by walking the
ancestor chain with `getBoundingClientRect()` at every level, not
assumed from reading the CSS. Fixed with `flex: 1; min-width: 0;` —
the standard, deterministic way to make a "fill the remaining row
space" column, instead of relying on content happening to produce a
reasonable shrink-to-fit size.

**Bug 2 — the real "Error 153" cause: no `referrerpolicy` on the
iframe.** Once the video had real dimensions to actually render into,
the reported error reproduced exactly. Ruled out two plausible causes
empirically before finding the real one: swapping `youtube-nocookie.com`
for plain `youtube.com` didn't help; testing via `localhost` instead of
the raw `127.0.0.1` IP didn't help either. The actual cause: this
project's `SecurityMiddleware` sends `Referrer-Policy: same-origin`
site-wide (CLAUDE.md ch.12) — correct for the site itself, but it means
the browser sends *no* referrer at all on any cross-origin request,
including to YouTube's embedded player, which can't validate the embed
without one and fails with a generic configuration error instead of
actually loading. Confirmed by adding `referrerpolicy="strict-origin-
when-cross-origin"` directly to the iframe (overriding the page-level
policy for just that element) — the error changed from the generic
"Error 153" to YouTube's real response for that specific video,
proving the player initializes correctly once it has an origin to
validate against. `strict-origin-when-cross-origin` still only reveals
this site's origin (scheme+host) to YouTube, not the specific article
URL being read, keeping the same referrer-privacy intent
`Referrer-Policy: same-origin` was set for in the first place.

Two files: `static/js/cms/ckeditor-youtube-embed.js` (the custom
MediaEmbed provider that generates the saved iframe markup — Phase ~9)
now emits the attribute; `apps/core/utils.py`'s `_validate_iframe_attribute`
allow-list (the bleach sanitizer applied in `News.save()`/`Page.save()`)
had to be extended to keep it, or every save would have silently
stripped it back out.

## Verification

`pytest`: 2 new sanitizer tests (`apps/core/tests.py`) — `referrerpolicy`
survives sanitization on a real YouTube iframe, a non-YouTube iframe
host is still rejected. 122 passed total.

Playwright: reproduced the original error on a fresh CMS-created,
published article; confirmed the layout fix via `getBoundingClientRect()`
at every level of the ancestor chain before and after; confirmed the
referrer-policy fix by observing the error message itself change from
generic-config-error to a real YouTube response; re-screenshotted an
existing real article (text + featured image, no video) to confirm the
flex change caused no regression there. Test articles/media removed
afterward.

# Phase 24 (optional per-video cover image for embedded YouTube videos, click-to-load facade)

## What was asked

An editor may want a custom thumbnail for an embedded YouTube video
instead of YouTube's own preview frame — explicitly *not* a general
native-video-upload feature, confirmed with the user before starting:
just an optional cover image keyed to the existing YouTube-embed
feature from Phase ~9/23. No cover set → behaves exactly as before
(direct iframe).

## Why a separate model, not an HTML attribute on the embed

`CKEDITOR_5_CONFIGS` has no `htmlSupport`/General HTML Support plugin
enabled (checked directly in `config/settings/base.py`, not assumed),
so a custom attribute hand-added to the saved markup has no guarantee
of surviving CKEditor5 regenerating its editing view from its internal
model on the next edit. Rather than risk silent data loss on re-edit,
the video_id → cover mapping lives in its own table,
`apps.news.models.NewsVideoCover` (`news` FK + `video_id` +
`cover_image` FK, unique on `(news, video_id)`) — the article's
`content` field is never touched by this feature at all. This is the
first model in the project with a plain "one News, many X" FK (no
precedent existed before — checked).

## A real discovery made while building this: what `News.content` actually contains

Building the CMS-side "which videos are in this article right now"
detection required understanding what CKEditor5's MediaEmbed plugin
actually round-trips through `editor.getData()`/`setData()`, not just
what's visible in the rendered iframe. Verified directly (Playwright,
loading a real existing video article — pk 29 — back into the CMS
editor and dumping `editor.getData()`): the *actual* stored
`News.content` is not merely the bare `<div class="media-embed
media-embed--youtube"><iframe>` produced by the custom provider's
`html:` callback (Phase 9/23) — it's that div wrapped in
`<figure class="media"><div data-oembed-url="...original pasted
URL...">`, which the bleach sanitizer must therefore also allow through
(only iframe-level attributes are restricted by
`_validate_iframe_attribute`). That `data-oembed-url` marker is what
lets CKEditor5's own upcast converter recognize the content as a media
widget again on the next edit and reconstruct the correct editing-view
figure — proven empirically when a first attempt at feeding
`editor.setData()` a bare `media-embed` div (no figure/oembed wrapper)
during Playwright verification silently dropped the video entirely.
Because of this, `static/js/cms/video-covers.js`'s video-ID detection
only ever looks for `<iframe src=".../embed/(id)">` inside the current
data — it doesn't care about or depend on the wrapper shape at all,
so it's unaffected either way.

## CMS: "Video örtükləri" sidebar

`static/js/cms/video-covers.js` — registers with django_ckeditor_5's
own `window.ckeditorRegisterCallback('id_content', ...)` hook to get
the live CKEditor5 instance, rather than polling/observing the editing-
view DOM: the editor element is created asynchronously (`ClassicEditor
.create().then(...)`, well after `DOMContentLoaded`), so scraping the
DOM at load time is inherently racy, while the registered callback only
fires once the instance genuinely exists. On every `change:data`
(debounced 500ms) it re-scans `editor.getData()` for YouTube iframe
src's, diffs against the currently-rendered picker rows, and adds/
removes rows in the "Video örtükləri" sidebar section accordingly. Each
row is built with the exact same `[data-role="image-picker"]` markup as
the featured/OG image pickers and registered into the *same* shared
media-picker modal via a new export from Phase 22's
`static/js/cms/image-pickers.js` — `window.registerImagePicker(el)` —
so no picker/modal logic is duplicated for this feature. Existing
covers (when editing an already-saved article) are seeded from hidden
`data-role="existing-video-cover"` spans the template renders from
`form.instance.video_covers.all`. On submit, the current video→cover
state is serialized into a hidden `video_covers_json` field, read by
`apps/news/services.py`'s new `sync_video_covers(article, payload_json)`
— a full replace-all (not a diff) called from `NewsCreateView`/
`NewsUpdateView.form_valid()` right after `super().form_valid(form)`,
matching how `ActivityLog.objects.create()` already relies on
`self.object.pk` being available at that point in both views.
Malformed/invalid entries (bad JSON, missing video_id, a
`cover_media_id` that isn't a real `MediaFile`) are silently skipped —
`content` remains the source of truth for which videos exist; a cover
mapping is only ever an optional enhancement on top of it, never
something a save should fail over.

`apps/media_manager/services.py`'s `collect_news_media_ids()` (Phase 19)
now also includes every `article.video_covers.cover_image_id` — so
`NewsPermanentDeleteView`'s existing exclusive-media cleanup correctly
accounts for cover images too, same shared-vs-exclusive logic already
covering featured/OG/inline images.

## Public site: click-to-load facade

`NewsDetailView.get_context_data()` adds `video_covers` — a plain
`{video_id: cover_image_url}` dict — surfaced to the template via
Django's `json_script` filter (`templates/news/detail.html`), no new
server-rendering logic needed. `static/js/pages/article.js` (previously
just the print button) reads it on load and, only for videos that have
a matching cover, replaces the `<iframe>` inside `.media-embed--youtube`
with a `<button class="media-embed__facade">` showing the cover image
and a play icon; the iframe's `src`/`allow`/`referrerpolicy`/`loading`
are preserved on the button as closure state, not re-derived. Clicking
it lazily builds a fresh real `<iframe>` with those exact attributes and
swaps it back in — the video never starts loading until the reader
actually asks for it. A video with no matching cover is left completely
untouched, so Phase 23's `referrerpolicy` fix keeps applying unchanged.

## Verification

`pytest`: new `apps/news/tests/test_video_covers.py` — `sync_video_covers()`
create/replace/malformed-entry behavior; `collect_news_media_ids()`
includes video-cover images; a video-cover image survives permanent-
delete of its article if still referenced elsewhere (mirrors Phase 19's
shared-media test), and is cleaned up via the real HTTP permanent-delete
view when it isn't; `NewsCreateView` persists a submitted
`video_covers_json` payload end-to-end. 130 passed total.

Playwright: created a real article via the CMS, inserted a YouTube
embed directly into the live CKEditor instance (in the correct
`<figure data-oembed-url>` shape — see the discovery above), confirmed
the "Video örtükləri" row appeared, picked a cover via the existing
Phase 22 media-picker modal, saved and published; confirmed the public
page rendered a `.media-embed__facade` with that exact cover image and
zero direct iframes, then confirmed clicking it produced a real iframe
with the correct `src`/`referrerpolicy`. Separately re-verified the
pre-existing real article (pk 29, no cover set) still renders a direct
iframe with Phase 23's `referrerpolicy` intact — no regression. Test
article and its `NewsVideoCover` rows removed from the dev database
afterward.

# Phase 25 (responsive ad banner; a placeholder CTA for empty ad slots; a real CMS Contact Message inbox)

## Ad banner cropping on resize

Reported as "the ad banner isn't responsive" and, after a first fix,
"still gets cropped when the screen shrinks." Root cause (confirmed with
Playwright at five viewport widths, not guessed): `.ad-slot--sidebar`
(`static/css/layout/sidebar.css`) had `width: 100%` but a fixed
`height: 280px` — correct only at the desktop sidebar's exact 360px
width (`AdPosition` "home-sidebar-1"/"category-sidebar-1" is registered
as 360×280). Once the sidebar stacks to near full page width on tablet
(768–992px, `static/css/responsive/mobile.css`), the box stayed pinned
at 280px tall while ~700–950px wide, and `object-fit: cover` cropped
the banner into an unreadable sliver (confirmed visually — the
campaign's own logo and CTA button were cut off).

Landed on the same fluid-width/fixed-ratio pattern `.news-card__image`
already uses everywhere else on the site (`static/css/components/
cards.css`): `aspect-ratio: 360 / 280` directly on `.ad-slot--sidebar`,
`object-fit: cover` on `.ad-slot__image`. Verified at 1440/992/768/480/
360px — the banner now keeps the same proportions and shows in full at
every width, matching the rest of the site's card imagery instead of a
one-off implementation.

## Empty ad slot becomes a house-ad CTA

A slot with no active campaign used to render a bare empty `<div>`. Now
`templates/components/advertisement.html`'s empty branch is a real link
to `pages:contact` ("Burada sizin reklamınız ola bilər. Əlaqə üçün
əlaqə səhifəsinə keçin.") reusing the exact same `.ad-slot--sidebar`
box (same aspect-ratio, same footprint) via a new `.ad-slot--placeholder`
modifier — centered text, hover feedback, no layout shift once a real
campaign goes live in that slot.

## Contact Message CMS inbox

The Contact form (`apps.pages.forms.ContactForm`/`ContactView`) only
ever emailed a submission and forgot it — an editor whose mailbox
filtered or dropped that email had no other record it existed. New
`apps.pages.models.ContactMessage` (status: `Status.NEW`/`Status.READ`
— CLAUDE.md ch.10 "Avoid boolean fields for workflows... use status
values", not an `is_read` boolean) is created in `ContactView.form_valid()`
alongside the existing `send_contact_email.delay()` call — the CMS row
is the durable record, the email is a notification on top of it, not
the source of truth.

New CMS module, `apps/cms/views/contact_message.py` — kept as its own
file rather than folded into `apps/pages/views.py` (public) or another
CMS view module, matching the project's one-file-per-screen convention:

- `ContactMessageListView` — the standard CMS list shape (status filter,
  name search, pagination), mirroring `TagListView`/`PageListView`.
- `ContactMessageDetailView` — opening a message *is* what marks it
  read (`get_object()` flips `NEW` → `READ` before rendering), the same
  implicit-read convention every email inbox uses, so reading a message
  costs zero extra clicks.
- `ContactMessageToggleStatusView` — a manual override for flipping a
  message back to `NEW` (e.g. "I'll come back to this one"), reachable
  from both the list row and the detail page.

New sidebar entry ("Müraciətlər", `templates/cms/base.html`) shows a
live unread-count badge. Backed by a new, narrowly-scoped context
processor — `apps.core.context_processors.cms_notifications` — kept
separate from the existing `site()` processor (which every public page
also pays for) specifically because this one only makes sense, and only
runs its query, for authenticated `/cms/` requests; `site()` has no such
guard and would run this query on every public page view for no reason.

## Verification

`pytest`: `apps/cms/tests/test_contact_messages.py` — submitting the
public form creates a CMS-visible `ContactMessage`; the list requires
login, shows messages, and filters by status; opening a message marks
it read; the toggle view flips read back to new; the sidebar unread
count reflects only `NEW` messages. 137 passed total.

Playwright: submitted the real public contact form, confirmed the CMS
sidebar badge showed "1", opened the message from the list (status
flipped `Yeni` → `Oxunub` immediately, list re-confirmed it), toggled it
back to `Yeni` from the list row. Ad banner re-screenshotted at all five
widths after the aspect-ratio fix — full banner visible and proportional
at every one, matching `.news-card__image`'s behavior. Test message
removed from the dev database afterward.

## Addendum — a visible template comment, and an optional phone number

Two follow-ups reported right after Phase 25 shipped:

**A raw template comment was showing up on the message detail page.**
Django's `{# ... #}` comment tag is documented as single-line only — the
three-line version in `contact_message_detail.html` wasn't parsed as a
comment at all, so its literal text rendered on the page. Fixed by
switching to `{% comment %}...{% endcomment %}`, which does support
multiple lines. Checked the rest of the templates for the same mistake
(none found).

**Email shouldn't be mandatory if a phone number is given instead.**
`ContactMessage`/`ContactForm` gained a `phone` field (`CharField(max_length=30,
blank=True)`, matching `SiteSettings.contact_phone`'s existing shape);
`email` became `required=False`. A new `ContactForm.clean()` requires at
least one of the two — a reply channel is still mandatory, just not a
specific one. `send_contact_email` and the CMS detail page adjust
accordingly (a phone-only message shows a "Zəng et" call link instead of
a broken `mailto:` with nothing after the colon).

Verified with Playwright: submitted phone-only (succeeds), submitted
with neither email nor phone (shows the Azerbaijani cross-field error),
confirmed the fixed detail page no longer leaks the comment text and
shows the phone number with a working `tel:` link. 139 tests passing.

# Phase 26 (move a Media Library file between folders)

## What was asked

`MediaFile.folder` (a nullable FK to `Folder`, CLAUDE.md ch.9 "Media
Library — Folder organization") could only ever be set once, at upload
time (`process_crop(..., folder_id=...)`) — there was no way to move an
already-uploaded file into a different folder afterward, or back out of
one. Requested as a "if it's not too hard" nice-to-have, so implemented
as the simplest thing that solves it — no drag-and-drop, matching
`FolderCreateView`/`FolderUpdateView`'s existing plain-POST-and-redirect
pattern (CLAUDE.md ch.8 "AJAX should be used only when necessary")
rather than introducing a new interaction paradigm for one feature.

## Implementation

A plain `<select onchange="this.form.submit()">` added to each card's
existing row-menu (`templates/cms/partials/media_grid.html`), listing
every `Folder` plus a "Qovluqdan çıxar" (remove from folder) option —
posts to a new `apps.cms.views.media.MediaMoveView`, which just
reassigns `MediaFile.folder` and logs `ActivityLog.Action.MEDIA_MOVED`.
`"Qovluqdan çıxar"` uses the sentinel value `__unfiled__` rather than an
empty string — the placeholder option ("Qovluğa köçür...") is itself
`value=""` and `disabled`, so a second option sharing that value would
have been ambiguous HTML even though it's never actually submittable in
practice.

Redirects back to the exact filtered/paginated grid the move was made
from (folder/format/search/page) — reconstructed server-side from a
small whitelist of hidden `return_*` fields via `reverse()` +
`urlencode()`, deliberately not a raw "next" URL parameter, so this
can't become an open redirect (CLAUDE.md ch.12). Moving a file *out of*
the folder currently being viewed correctly returns to that same
(now one-file-shorter) filtered view rather than following the file to
its new location — consistent with how every other per-row action on
this page already behaves (stays where you were working).

Media Picker's grid (`cms/partials/media_picker_grid.html`, Phase 22)
deliberately has no row-menu at all — this feature only touches the
main Library grid, not the picker.

## Verification

`pytest`: `apps/cms/tests/test_media_move.py` — requires login; assigns
a folder; moves between two different folders; "Qovluqdan çıxar" clears
it; the redirect preserves the filtered grid's folder/format/search/page
via the `return_*` fields. 144 passed total.

Playwright: moved a real Media Library file unfiled → "Reklam" →
"Loqo" → unfiled again, confirmed via the filtered grid endpoint
(`?folder=<id>`) at each step that the file appeared/disappeared
correctly; confirmed moving it out of the currently-viewed folder
redirected back to that folder's view, not the file's new one. File
ended the run back in its original (unfiled) state — no cleanup needed.

## Addendum — the panel closed itself the instant the select was clicked

Reported immediately after shipping: opening the row-menu and clicking
the new select closed the whole panel before a folder could be chosen.
`static/js/cms/news.js`'s `initRowMenus()` (shared by both the News and
Media list pages) closes every open row-menu panel on any `document`
click, so the menu can dismiss itself on an outside click — but a click
on a still-closed `<select>` to open it also dispatches a real, bubbling
`click` event on the select itself, which is indistinguishable from an
"outside" click to that listener. Confirmed the actual mechanism (not
guessed) with Playwright: a raw `.click()` on the select, not the
higher-level `selectOption()` helper my first verification pass used
(which sets the value programmatically and never exercises this path at
all — why the bug wasn't caught the first time). Fixed by skipping
`closeAllPanels()` when the click originated inside
`.cms-row-menu__move-form`; every other row action (`Əvəz et`, `Sil`,
the toggle button) is unaffected since they either navigate away or
already stop their own propagation.

# Phase 27 (real per-role permissions — the other four CMS roles stop being just a label)

## What was asked

User noticed the role picker on the "add user" screen and asked what
each role actually did. The honest answer, checked against the code
rather than assumed from CLAUDE.md's aspirational ch.9 description: only
two tiers existed — `AdministratorRequiredMixin` gated Users/Settings/
Social Links, and every other role (Baş redaktor, Redaktor, Jurnalist,
Kontent meneceri) had *identical* access to everything else. The picker
worked, but four of its five options were purely cosmetic. Confirmed
with the user which concrete rules to build for each role before writing
any code, rather than inventing a scheme unilaterally.

## The permission model

Four boolean-ish properties on `apps.accounts.models.User`, each backed
by a `set` of `Role` members plus an `is_administrator` escape hatch
(superusers and Administrators pass every check):

- `can_write_news` — Administrator, Baş redaktor, Redaktor, Jurnalist.
  Kontent meneceri is the one role that never touches News at all.
- `can_manage_structure` — Administrator, Baş redaktor, Kontent meneceri.
  Categories and Advertisements are structural/monetization decisions,
  not day-to-day editorial work — Redaktor and Jurnalist don't reach
  either screen.
- `can_manage_content` — everyone except Jurnalist. Tags, Pages, and the
  SEO overview are content-adjacent but not News itself.
- `is_senior_editor` — Administrator, Baş redaktor, Redaktor. The line a
  Jurnalist doesn't cross: editing/publishing/deleting *any* article,
  not just their own.

Three new `LoginRequiredMixin` subclasses in `apps/core/mixins.py`
(`StructureManagerRequiredMixin`, `ContentManagerRequiredMixin`,
`NewsAccessRequiredMixin`) each just delegate `test_func()` to one of
these properties, mirroring the existing `AdministratorRequiredMixin`.
Applied to the relevant CMS views: Category/Advertisement views got
`StructureManagerRequiredMixin`; Tag/Page/SEO overview got
`ContentManagerRequiredMixin`; every News view got
`NewsAccessRequiredMixin`. Media Library, Dashboard, Activity Log and
the Contact Message inbox stay open to every logged-in role — nothing
in the confirmed rules restricted them.

## Jurnalist: own articles only, no direct publishing

Two more restrictions apply *within* the News screens, since
`can_write_news` alone only answers "can this role reach the screen,"
not "what can they see/do on it":

**Ownership scoping.** A new `apps/cms/views/news.py` helper,
`_scope_to_author(queryset, user)`, filters to `author=user` for
anyone who isn't `is_senior_editor` — applied to every News queryset
and `get_object_or_404` lookup (list, create's success redirect target,
update, delete, permanent-delete, restore, duplicate, and the bulk-
action queryset). A Jurnalist opening someone else's article by URL
gets a 404, not a 403 — consistent with the rest of the project's
existing "don't reveal whether the object exists" pattern rather than a
new one invented for this feature.

**No direct publish.** `apps.news.forms.NewsForm.__init__` now takes a
required `user` kwarg (`NewsCreateView`/`NewsUpdateView` supply it via
`get_form_kwargs()`) and narrows `status`'s choices to Draft/Pending
Review when `not user.is_senior_editor` — the dropdown itself never
offers Published/Scheduled/Archived, and a crafted POST with one of
those values is rejected by Django's own "not one of the available
choices" ChoiceField validation, no separate `clean()` check needed.
`NewsBulkActionView` gets the equivalent check for the bulk publish/
archive actions (bulk delete stays available, scoped to the Jurnalist's
own articles same as everything else).

## Template visibility

`templates/cms/base.html`'s sidebar now renders a disabled `<span>`
instead of a link for every section a role can't reach (matching the
existing Users/Settings pattern from before this phase, just driven by
the new properties instead of a hardcoded Administrator check).
`dashboard.html`'s "Yeni xəbər" quick action and `news_list.html`'s bulk
publish/archive buttons are similarly hidden rather than left as dead
links that would 403/reject on click.

## Verification

`pytest`: rewrote `apps/cms/tests/test_permissions.py` as a full
5-role × 13-screen access matrix (`ALL_ROLES` × `LIST_VIEWS`, with the
allowed-role set spelled out per screen) — the old test only ever
checked Administrator vs. "logged in" for a fixed six of those screens.
New `apps/cms/tests/test_news_role_scoping.py`: a Jurnalist's news list
only shows their own articles, editing someone else's 404s, editing
their own works, direct-publish is rejected while Draft/Pending Review
succeeds, an Editor *can* edit and publish someone else's article
(confirming the restriction is Jurnalist-specific, not News-wide), a
Kontent meneceri can't reach News at all, and both bulk-publish
(rejected) and bulk-delete (allowed, own articles) for a Jurnalist. New
`editor_in_chief`/`editor`/`content_manager` fixtures added to
`conftest.py` alongside the existing `administrator`/`journalist` pair.
195 passed total.

Playwright: created one real test account per new role, hit all 9
gated CMS screens with each, and confirmed every response code against
the exact matrix above (all matched — Baş redaktor: everything but
Users/Settings; Redaktor: no Categories/Ads; Jurnalist: only News+Media;
Kontent meneceri: no News). Screenshotted a Jurnalist's dashboard
sidebar to confirm the disabled items render as inert `<span>` elements,
not dead links. Confirmed the News editor's status dropdown for a
Jurnalist offers only "Qaralama"/"Nəzərdən keçirilir". Test accounts
removed from the dev database afterward.

## Addendum — phone number on the user form, and role privileges spelled out

Two follow-ups once the role system above existed to actually describe:
`User.phone` (added alongside the role work) is now surfaced in
`UserForm`/`user_form.html`. And since Phase 27 gave the five roles real,
different privileges, the "Rol" field on that same form now spells out
each one's actual access in plain Azerbaijani directly under the
dropdown, so an Administrator creating an account doesn't have to guess
or go check the code — kept in sync by hand with the permission
properties on `User`, the same way `AdvertisementForm`'s CMS hints
already explain jargon fields elsewhere.

Also clarified for the user: new accounts intentionally never get a
password typed in by the creating Administrator — they always get one
via an emailed setup link (`apps.accounts.services.send_password_setup_email`),
per CLAUDE.md ch.12 "Never display passwords. Never email passwords."
This was already noted on the form (`"Yeni istifadəçiyə şifrə təyin
etmək üçün e-poçtuna keçid göndəriləcək."`) but had gone unnoticed —
no behavior change, just confirmed the existing design was intentional.

Verified with Playwright: the phone field renders and round-trips
through a real user creation; screenshotted the role hint block.
195 tests still passing (no new tests needed — `phone` is a plain
optional field with no validation logic of its own to cover). Test
account removed from the dev database afterward.

# Phase 28 (primary nav overflow — too many categories used to just spill off the screen)

## What was asked

User asked, hypothetically, what happens if there are enough categories
that they don't fit in the nav bar. Checked the code rather than
guessing: nothing handled it. `.nav__list` (`static/css/layout/
navigation.css`) is a plain `flex` row with no `flex-wrap` and no
`overflow-x`, and `main_categories` (`apps.core.context_processors.site`)
had no cap — every active top-level category with at least one
published article got rendered, unconditionally. Past a certain count,
items would silently overflow the container's right edge (no clipping,
since nothing up the ancestor chain sets `overflow: hidden` either) —
broken-looking, not a graceful degradation.

## How many actually fit — measured, not guessed

Seeded 8 extra temporary categories (16 total) and measured each nav
item's rendered right edge against the container's right edge with
Playwright at both 1440px and the narrowest standard desktop width,
1280px (`--container-max-width`). Roughly 12 items fit at 1280px before
the first overflow — but that measurement didn't yet account for the
overflow-trigger button itself needing room, which would eat further
into that budget. Landed on a fixed count of 8
(`NAV_VISIBLE_CATEGORY_COUNT`, `apps/core/context_processors.py`)
rather than a JS-measured dynamic threshold — deterministic and simple
(CLAUDE.md ch.8 "JavaScript is responsible for interactivity only"),
and it happens to match the site's real current category count exactly,
so nothing changes visually today; the overflow menu only appears once
a 9th category is added.

## Implementation

`site()`'s `main_categories` is now materialized to a `list` and split
into `nav_categories` (first 8) and `nav_overflow_categories` (the
rest) — `main_categories` itself stays the full, uncapped list, since
`footer.html` uses it as a complete sitemap-style listing with no
overflow concern of its own. `header.html` loops over `nav_categories`
for the direct nav items, then — only if `nav_overflow_categories` is
non-empty — adds one more `<li class="nav__item--has-dropdown">`
("Digər kateqoriyalar") holding the rest, built from the exact same
markup pattern the existing "Daha" static-pages dropdown already uses.
No JS or CSS changes needed: `static/js/components/dropdown.js` already
generically wires up every `.nav__item--has-dropdown` (mobile tap-to-
open; desktop already uses CSS `:hover`/`:focus-within`), and the
dropdown styling is shared, not duplicated.

## Verification

`pytest`: `apps/core/tests.py` — with more than 8 published-and-active
top-level categories, `nav_categories` caps at 8, `nav_overflow_categories`
holds the remainder, and `nav_categories + nav_overflow_categories ==
main_categories` (nothing lost, just split); with few categories,
`nav_overflow_categories` is empty. 197 passed total.

Playwright: reproduced the real overflow scenario (16 categories) —
confirmed all 16 nav items combined (8 direct + "Digər kateqoriyalar" +
"Daha") fit within the container with zero overflow, confirmed hovering
"Digər kateqoriyalar" reveals exactly the 8 overflow categories, and
separately confirmed `footer.html` still lists all 16. Temporary
categories and their articles removed from the dev database afterward.

# Phase 28 (footer category overflow — a real "Bütün bölmələr" index page)

## What was asked

Follow-up to Phase 26's nav overflow fix, discussed and agreed with the
user before implementing: `footer.html`'s "Bölmələr" column stacks one
`<a>` per category vertically with no cap — unlike the nav row (bound
by width), the footer column is bound by *height*, so past a handful of
categories it just grows taller and taller, visually lopsided against
the much shorter "Şirkət"/"Hüquqi" columns next to it. Two options were
discussed (cap-with-link-out vs. reflowing into pills/multi-column);
went with the more durable one — a real dedicated category index page,
matching how larger news sites handle this, with the added benefit of
a proper crawlable/linkable category listing (CLAUDE.md ch.14 internal
linking) that didn't exist before at all.

## Deduplicating the "does this category lead anywhere" query

Before adding a third caller of the same nav-visibility logic (nav,
footer, and now the index page), the query itself moved out of
`apps.core.context_processors.site()` and into a new
`Category.objects.navigable()` queryset method — top-level categories
with at least one published article (own or via a subcategory), each
with its visible+published subcategories prefetched. `site()` now just
calls `list(Category.objects.navigable())` once; the index page's
`CategoryIndexView.get_queryset()` calls the exact same method (CLAUDE.md
ch.15 "Never duplicate business logic" — this rule now lives in exactly
one place instead of being copy-pasted a third time).

## Footer cap + index page

A second constant, `FOOTER_VISIBLE_CATEGORY_COUNT` (also 8, same
reasoning as the nav's — matches today's real count, so nothing visibly
changes until a 9th category exists), caps `footer_categories` the same
way `NAV_VISIBLE_CATEGORY_COUNT` already caps `nav_categories` — both
sliced from the same uncapped `main_categories` list, no extra queries.
A new `footer_has_more_categories` flag shows a "Bütün bölmələr →" link
(bold, matches the column's other links otherwise) only when there's
actually overflow.

New `apps.categories.views.CategoryIndexView` at `/category/` (the
categories app's own URL root, alongside its existing `/category/<slug>/`
detail route) — a plain `ListView` with no pagination (a bounded,
editor-curated list, not user-generated content), rendering every
navigable category as a card with its subcategories linked underneath.
New `templates/categories/category_index.html` +
`static/css/pages/category-index.css` (a responsive 3/2/1-column grid),
following the same breadcrumbs/container/empty-state conventions as
`category_detail.html`.

## An unrelated environment hiccup surfaced along the way

While running the full suite to verify this change, `pytest` started
failing across dozens of unrelated tests with `redis.exceptions.ConnectionError`
— the local Memurai (Redis-compatible) Windows service had stopped at
some point during the session, unrelated to this feature (`apps.accounts.services`'s
login-lockout counter, and Django's own cache-backed sessions, both
need it). Restarted the service (`Start-Service Memurai`) and confirmed
a clean run afterward — not a regression from this change, just an
environment hiccup that happened to surface while testing it.

## Verification

`pytest`: `Category.objects.navigable()` covered indirectly through the
existing nav tests (unchanged assertions, same method now used
underneath) plus new ones — footer caps at `FOOTER_VISIBLE_CATEGORY_COUNT`
and flags overflow correctly, is empty-flagged when everything fits;
`CategoryIndexView` lists a populated category, excludes an empty one,
and shows subcategory links. 202 passed total.

Playwright: created 4 extra categories (12 total), confirmed the footer
showed exactly 8 plus the "Bütün bölmələr" link, clicked it and
confirmed `/category/` listed all 12 in the grid. Temporary categories
and their articles removed from the dev database afterward.

# Phase 29 (sticky category nav; contact info in the footer + structured data)

## Sticky nav — a real CSS containing-block gotcha, not just "add position: sticky"

Reported: scrolling down a long page leaves the category row behind,
so switching categories means scrolling back to the top first. Discussed
scope with the user first — only the category row should stick, not the
logo/social/search topbar or the breaking-news ticker above it, so it
keeps a fixed screen-space cost instead of the full header permanently
eating the top of the viewport.

The first attempt — just adding `position: sticky; top: 0;` to
`.site-header__navbar` — measurably failed: Playwright showed the
navbar's `boundingBox().y` at -1084 after scrolling 1200px, i.e. it had
scrolled away entirely, not stuck. Root cause, confirmed by walking the
computed-style ancestor chain rather than guessing: a sticky element
can only remain stuck for as long as its *containing block* (in the
simple case, its parent) is intersecting the viewport. `.site-header__navbar`
was nested inside `<header class="site-header">` alongside the topbar —
and that `<header>` was only exactly as tall as topbar+navbar combined
(134px), with nothing else inside it. Once the user scrolled past the
topbar's own height (~80px), the header itself had fully exited
upward, leaving the sticky navbar with no more containing block to
anchor against — so it started scrolling away again immediately after
a brief ~80px stick.

Fixed by restructuring `templates/components/header.html`: `</header>`
now closes right after the topbar, and `.site-header__navbar` (plus the
search form) become siblings of `<header>` instead of children —
`<body>` is now their containing block, which spans the entire page, so
the sticky row has room to stay stuck for the whole scroll. Confirmed
no CSS selector or JS depended on the navbar being nested inside
`.site-header` (checked directly, not assumed) before making the
change — `<nav>` is still a proper semantic landmark either way, just
no longer inside the same top-level `<header>` as the topbar, which
HTML5 doesn't require.

New `z-index: 40` on the sticky row (existing scale: dropdown 50,
mobile off-canvas drawer 200, toast 1000 — sits below both, above plain
page content). Degrades to a no-op on mobile: `.nav` becomes a
`position: fixed` off-canvas drawer there (Phase before this one), so
`.site-header__navbar` has no in-flow content left to stick once that
kicks in.

## Contact info: footer + structured data

Discussed where else `SiteSettings.contact_phone`/`contact_email`
(previously shown only on the Contact page) should appear; picked the
two highest-value, lowest-risk spots over a header/topbar addition
(rejected — no room, and CLAUDE.md ch.7 minimalism):

- **Footer** — a new `.site-footer__contact` list in the brand column
  (phone + email, icon + link, `mailto:`/`tel:`), shown only when set.
- **Structured data** (invisible to readers, SEO-only) — `base.html`'s
  site-wide `Organization` JSON-LD gained a `contactPoint` block
  (`contactType: "customer service"` + phone/email), each field only
  emitted when the corresponding `SiteSettings` field is filled in —
  can help Google's Knowledge Panel / rich results (CLAUDE.md ch.14).

## Verification

`pytest`: 202 passed, unaffected by any of this (no new Python logic —
template/CSS changes only).

Playwright: scrolled 1200px and confirmed the navbar's bounding box
sits at `y: 0` (genuinely stuck, not just "hasn't scrolled past yet"),
confirmed a category link stays clickable without scrolling back up,
confirmed the "Digər kateqoriyalar" dropdown still opens correctly
while the nav is stuck, and separately confirmed the mobile off-canvas
hamburger menu (a completely different code path) still opens
correctly after the restructuring. Confirmed the footer shows the real
`contact_email`/`contact_phone` from `SiteSettings` with working
`mailto:`/`tel:` links, and confirmed the page's `Organization` JSON-LD
now includes a matching `contactPoint`.

# Phase 30 (pre-deployment audit — one deploy-blocking bug, one real functional gap)

## What was asked

User is deploying to the VPS today and asked for a thorough audit of
the whole project for anything missing or broken before going live —
not a specific feature request. Checked systematically rather than
just re-reading docs: `manage.py check --deploy`, `makemigrations
--check`, `collectstatic --dry-run`, every `{% static %}` reference in
every template cross-checked against a real file on disk, every env
var actually read by `config/settings/*.py` cross-checked against
`.env.example`, every third-party import in `apps/`+`config/` cross-
checked against `requirements/base.txt`, a search for leftover
`console.log`/`TODO`/`FIXME`/stray `print()`, the full `pytest` suite,
and the full `e2e/` Playwright suite (not just ad-hoc scripts written
during the session) — plus reading `docs/DEPLOYMENT.md` and `deploy/*`
side by side with what the code actually does, rather than trusting
the doc's own claims about itself.

## Found and fixed: `SECURE_PROXY_SSL_HEADER` was never set — this would have broken HTTPS entirely

The most serious finding. `deploy/nginx.conf` correctly forwards
`X-Forwarded-Proto` to Gunicorn, but `config/settings/production.py`
never told Django to trust that header. Without it, Django has no way
to know a request arrived over HTTPS — Gunicorn only ever sees plain
HTTP from Nginx — which breaks three things simultaneously the moment
HTTPS is enabled:

1. **An infinite redirect loop.** `SECURE_SSL_REDIRECT` (on by default)
   checks `request.is_secure()`, which would always be `False` without
   the proxy header — Django redirects every request to HTTPS, Nginx
   terminates it and forwards to Gunicorn as HTTP again, Django
   redirects again, forever. This alone would have made the entire
   site completely unreachable the moment `certbot` finished.
2. **CSRF validation** compares the request's detected scheme against
   the `Referer` header's scheme — mismatched (again because Django
   always thinks it's HTTP) means every form submission on the live
   site would have been rejected.
3. **`request.scheme` in templates** — used directly in canonical URLs,
   Open Graph tags, the sitemap, and every page's structured data —
   would render `http://` instead of `https://` sitewide, undermining
   the SEO work from earlier phases.

Fixed with one line: `SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')`
in `production.py`. Confirmed `manage.py check --deploy` still reports
zero issues with a realistic env afterward.

## Found and fixed: Scheduled articles never actually get published

`News.objects.published()` (`apps/news/models.py`) only ever matches
`status=News.Status.PUBLISHED` — confirmed nothing anywhere in the
project (no signal, no Celery task, no management command) ever
transitions a `SCHEDULED` article to `PUBLISHED` once its
`published_at` arrives. `docs/DEPLOYMENT.md` had actually documented
the opposite — a comment claiming "scheduled publishing is a query-
time filter" — which doesn't match the code at all and would have left
a real editor confused the first time they scheduled an article and it
never went live.

New `apps.news.management.commands.publish_scheduled` — the same
"plain cron, no Celery Beat" pattern `clean_temp_uploads` already
established (Phase ~10): finds every `Scheduled`, non-deleted article
whose `published_at` has passed, bulk-updates their status to
`Published`, and logs one `ActivityLog` entry per article (`actor=None`
— a system action, not a human one) so the CMS activity feed shows
*why* an article's status changed without an editor touching it.

Also discovered and fixed a second, smaller gap while here:
`clean_temp_uploads` itself has run this whole project with **no cron
entry ever actually documented** in `DEPLOYMENT.md`, despite its own
`help` text saying it needs one — the one-time VPS setup steps never
mentioned crontab at all. Added a new step 11 with both commands'
crontab lines together.

## Everything else checked came back clean

- `makemigrations --check --dry-run`: no missing migrations.
- `collectstatic --dry-run`: 281 files, no errors.
- Every `{% static %}` reference in every template (55 unique paths):
  all resolve to a real file.
- Every third-party import across `apps/`+`config/`: all present in
  `requirements/base.txt` (Django, psycopg, django-environ, django-redis,
  redis, celery, Pillow, django-ckeditor-5, bleach — nothing missing,
  nothing unused-but-still-installed).
- No stray `console.log`, `TODO`, `FIXME`, or debug `print()` anywhere
  in `apps/` or `static/js/`.
- Django's `LOGGING` config already separates application/security/
  error/task logs into rotating files per CLAUDE.md ch.5 — no gap.
- `.env` (the real local file, not `.env.example`) confirmed still
  correctly gitignored — never at risk of being committed.
- The one real documentation gap found in `.env.example`:
  `DJANGO_SECURE_HSTS_SECONDS` is read (with a safe 1-year default) but
  was never listed — added, with a note about starting with a short
  value for the first few days after enabling HTTPS.

## Verification

`pytest`: new `apps/news/tests/test_publish_scheduled.py` — publishes a
due Scheduled article and logs it, leaves a not-yet-due one alone,
ignores a soft-deleted one, confirms the newly-published article
actually appears in `News.objects.published()` afterward, and confirms
running with nothing due creates no log noise. 207 passed total.

Also ran the full `e2e/` Playwright suite (not just this session's ad-
hoc verification scripts) for the first time in a while — all 15
passed, including the mobile-nav test, which exercises Phase 29's
header restructuring end-to-end.

Manually verified `publish_scheduled` against the real dev database:
created an article with `status=SCHEDULED` and a `published_at` two
minutes in the past, ran `manage.py publish_scheduled`, confirmed its
status flipped to `PUBLISHED` and it immediately appeared in
`News.objects.published()`. Test article and its log entry removed
afterward.

# Phase 31 (custom 404 / 500 / CSRF-403 error pages — none existed until now)

## What was asked

User noticed, right after finishing the live VPS deploy, that the
project had no custom error pages at all — a direct gap against
CLAUDE.md ch.6 ("Create custom templates for: 403, 404, 500 ... Do not
display technical details") and ch.14's 404 requirements (search,
popular articles, categories, homepage link).

## Found

`templates/errors/` existed but was completely empty, and
`config/urls.py` set no `handler404`/`handler500`. Only
`templates/403.html` existed at the template root — not a global
handler, just Django's own convention of auto-discovering a template
literally named `403.html` for any unhandled `PermissionDenied`
(confirmed no explicit view ever renders it by name). It extends
`cms/base.html` and is only ever reachable from `apps/core/mixins.py`'s
CMS-only permission mixins (`AdministratorRequiredMixin` etc.) — no
public view raises `PermissionDenied`, confirmed by grep. That left one
real public-facing 403 uncovered: a CSRF failure (e.g. the contact form
submitted from a tab left open past the session/cookie lifetime), which
Django routes through the separate `CSRF_FAILURE_VIEW` setting, not
`handler403` — unset, it would have shown Django's unstyled built-in
`csrf_403.html`.

## Fixed

- `apps/core/views.py` — three new views: `handler404` (queries
  `News.objects.published()` for 3 popular articles; categories are
  already free via the `site()` context processor), `handler500`, and
  `csrf_failure` (branches on `request.path.startswith('/cms/')` — CMS
  gets the existing `templates/403.html`, public gets the new
  `templates/errors/403.html`).
- `config/urls.py` — `handler404`/`handler500` wired as module-level
  string paths (Django's documented convention; both are inert in
  `DEBUG=True`, so local dev behavior is unchanged).
- `config/settings/production.py` — `CSRF_FAILURE_VIEW`, set only here
  (not `base.py`) so `DEBUG=True` locally still gets Django's own more
  helpful CSRF debug explanation instead of the styled production page.
- `templates/errors/404.html`, `templates/errors/403.html` — extend
  `base.html` normally (reusing `.empty-state` from `alerts.css`,
  `news_card.html`, and the `site()` context processor's
  `main_categories` — no new components needed for either).
- `templates/errors/500.html` — deliberately **not** `{% extends
  "base.html" %}`. A 500 can itself mean the database is unreachable,
  and `base.html`'s header/footer depend on `site()` querying it.
  `handler500` renders via `render_to_string()` with no `request=`
  argument — `django.shortcuts.render()` always forwards the request
  into a `RequestContext`, which runs every context processor
  (including that DB query) regardless of whether the template ends up
  using the result, so omitting `request` entirely was the only way to
  actually keep this page DB-independent. Matches Django's own
  `server_error` view, which follows the same rule for the same reason.
- `static/css/pages/errors.css` — new, shared by all three templates.

## Verification

`pytest`: `apps/core/tests.py` — `handler404` returns 3 popular
*published* articles only (a draft with a higher view count is
confirmed absent from the response); `handler500` asserted via
`django_assert_num_queries(0)` to actually prove the no-DB claim, not
just assume it; `csrf_failure` returns the CMS-styled page for `/cms/`
paths and the public-styled page otherwise. 211 passed total.

Also confirmed the `handler404 = 'apps.core.views.handler404'` string
wired in `config/urls.py` resolves correctly through a real request
cycle, not just a direct function call: `Client().get()` under
`override_settings(DEBUG=False, ALLOWED_HOSTS=['testserver'])` against
a nonexistent URL returned a full 404 page (20,689 bytes — header,
footer and popular articles all present), confirming the URLconf
wiring itself works, not just the view function in isolation.

No visual browser check this time — this environment has no
screenshot/browser tool available. Recommend a quick real-browser check
of `https://spress.az/bu-səhifə-yoxdur/` after this deploys.

# Phase 32 (a real N+1 query, hiding in every subcategory article link)

## What was asked

User asked to check whether the site has any N+1 query problems, and
whether django-debug-toolbar was worth installing to find out.
Recommended checking directly with `CaptureQueriesContext` instead — no
new dependency (CLAUDE.md ch.3), no risk of it ever being left enabled
in production, and it becomes a permanent regression test instead of a
one-time interactive look.

## Found: `Category.get_absolute_url()` needs `.parent.slug` for a subcategory — nothing selected it

Built a throwaway diagnostic (data with articles deliberately filed
under a *subcategory*, not just any category) and ran it against six
public pages, capturing every real query and flagging any exact SQL
repeated more than once. Every page that renders `news_card.html` (or a
category breadcrumb) for a subcategory article showed the same pattern:
one extra `SELECT ... FROM categories_category` per article, scaling
linearly with article count. Root cause: `Category.get_absolute_url()`
needs `self.parent.slug` for a subcategory (`categories:subcategory_detail`
takes both slugs), but every affected queryset only had
`select_related('category', ...)` — one join short of the one that
actually mattered.

Confirmed on: `HomeView.category_sections` (a top-level section shows
its subcategories' articles too), `NewsDetailView` (the article's own
breadcrumb, and `related_articles`' fallback-by-category query),
`NewsSearchView`, `CategoryDetailView` (both the page's own breadcrumb
and its article list), `TagDetailView`, and this session's own
`apps.core.views.handler404`. Two spots that looked like candidates but
weren't: `HomeView`'s hero/`popular_news` and `breaking_articles` — grep
confirmed neither of their templates ever calls `category.get_absolute_url`,
so no fix needed there.

## Fixed

Changed `select_related('category', ...)` to `select_related('category__parent', ...)`
in all six spots above (`apps/news/views.py` ×4, `apps/core/views.py`,
`apps/tags/views.py`) — `category__parent` implies `category` in the
same JOIN, no need to list both. `CategoryDetailView._resolve_category()`
(`apps/categories/views.py`) also got `.select_related('parent')` on the
category lookup itself, fixing the one-time (not N+1, but still free to
fix) query for the page's own breadcrumb.

Measured before/after with the throwaway diagnostic: HOME 20→17 queries,
ARTICLE DETAIL 20→15, CATEGORY TOP-LEVEL 20→14, CATEGORY SUBCATEGORY
21→14, SEARCH 17→11, 404 15→12 — and zero exact-duplicate queries left
on any of them, for a dataset with several articles filed under a
subcategory (the specific shape needed to surface this at all; a single
test article per category, as most existing tests use, never would
have shown it).

## Verification

`pytest`: six new regression tests (one per affected view/app —
`apps/news/tests/test_public_views.py` ×3, `apps/categories/tests.py`,
`apps/tags/tests.py`, `apps/core/tests.py`), each comparing real query
counts for 1 vs 3+ subcategory articles and asserting they're equal —
proving no N+1 directly, not asserting a magic fixed number unrelated to
the bug. Two false failures along the way, both test-design artifacts
rather than real regressions, worth recording since they'd trip up the
same approach again: `SiteSettings.get_solo()` (`apps.core.context_processors.site`)
lazily creates its one row on first access, so the *first* of two
captures in the same test always paid a one-time SELECT+INSERT the
second didn't — fixed by calling `SiteSettings.get_solo()` once before
either capture. Separately, the article-detail test reused the same
`client` (and therefore the same session) for both captures, so the
view-count-once-per-session logic (`NewsDetailView.get_object()`)
shaved one UPDATE off the second capture — fixed with an extra warm-up
request before either capture. 217 passed total (211 + 6).

# Phase 33 (crop preview 403 in production; create-success redirect; homepage section count in Settings)

## What was asked

User reported three things after using the CMS on the live VPS deploy,
plus a question about homepage logic:

1. Cropping an image in the CMS worked locally but the cropped preview
   didn't show after the real deploy, with a browser console error:
   `https://spress.az/media/temp/<uuid>.jpg 403 (Forbidden)`.
2. Publishing a News article seemed to make it "featured" automatically.
3. After successfully creating a News article, redirect to the news list
   instead of the article's own edit page.
4. What decides which categories appear on the homepage — user has 8
   populated categories but only 2 show as sections.

## 1. Fixed: crop preview 403 — nginx correctly denies /media/temp/, but the browser still needs to load it

Root cause, found by tracing the full stage→crop→confirm flow end to
end (JS ↔ view ↔ service, comparing every JSON field name against every
JS access site — no mismatch found there): `deploy/nginx.conf` has
`location /media/temp/ { deny all; }`, added deliberately in an earlier
phase per CLAUDE.md ch.12 ("temporary files... never served even by
accident"). Locally this is invisible because `DEBUG=True` serves
`MEDIA_URL` through Django's own `static()` helper (`config/urls.py`),
never touching nginx at all — in production, Cropper.js's preview
legitimately needs the browser to load that exact not-yet-confirmed
file, and nginx was blocking it outright.

Rejected fix: loosening the nginx rule — that would undo a deliberate
security decision for the sake of one feature. Instead:

- New `apps.cms.views.media.MediaTempPreviewView` — login-gated (same
  `LoginRequiredMixin` as every other media view), validates `temp_id`
  against `TEMP_ID_PATTERN` (exactly what `stage_upload()` generates:
  32 lowercase hex chars + `.` + a known extension) before it ever
  touches the filesystem, 404s otherwise, then serves the file via
  `FileResponse`. `/media/temp/` in nginx stays fully denied — nothing
  about that changes.
- `MediaUploadStageView.post()` now overwrites `stage_upload()`'s raw
  `/media/temp/...` URL with `reverse('cms:media_temp_preview', ...)`
  before returning the JSON. No JS changes needed at all —
  `media-uploader.js` just uses whatever `url` the response contains.
- Found and fixed one adjacent, real (if unrelated-to-the-report) bug
  while in this code: `templates/cms/partials/media_picker_grid.html`'s
  `data-thumbnail-url` attribute read `media_file.thumbnail.url|default:media_file.file.url`
  unguarded — for an SVG (`thumbnail` is always `None` for those,
  `apps/media_manager/services.py`), `FieldFile.url` raises `ValueError`
  *before* `|default` ever runs, potentially breaking the "Kitabxanadan
  seç" AJAX grid whenever an SVG is in the library. Matched the `<img>`
  tag two lines below, which already used `{% if %}`/`{% else %}`
  correctly.

## 2. Not a bug — clarified, no change made

Traced every mutation of `is_featured` in the codebase (model, form,
both `NewsCreateView`/`NewsUpdateView.form_valid`, the bulk-publish
action, `NewsDuplicateView`) — nothing ever sets it besides the admin's
own "Seçilmiş xəbər" checkbox. User confirmed after asking: the
checkbox itself was never getting checked — what looked like
auto-featuring was `HomeView`'s hero fallback (`apps/news/views.py`):
`published.filter(is_featured=True).first() or published.first()`,
which shows the latest article as the hero display whenever nothing is
actually marked featured, without writing anything to the database.
User chose to keep this fallback as-is (the alternative — no hero at
all when nothing's featured — was offered and declined).

## 3. Fixed: redirect after creating a News article

`NewsCreateView.get_success_url()` (`apps/cms/views/news.py`) changed
from `reverse('cms:news_edit', kwargs={'pk': self.object.pk})` to
`reverse('cms:news_list')`. `NewsUpdateView`'s equivalent (staying on
the edit page after an *edit*) was deliberately left alone — only asked
about the create flow.

## 4. Turned into a real setting: `SiteSettings.home_category_sections_count`

`HomeView.category_sections` used to cap at a hardcoded
`HOME_CATEGORY_SECTIONS = 2` constant (`apps/news/views.py`) — how many
top-level categories become a homepage section. User has 8 populated
categories and wanted to control this without a code change every time.
Added `SiteSettings.home_category_sections_count` (default 2, matching
prior behavior exactly — `MinValueValidator(1)`/`MaxValueValidator(8)`,
the upper bound matching the user's own current category count so "show
everything" is reachable), exposed in `templates/cms/settings.html`'s
"Ümumi" section, `HomeView` now reads `SiteSettings.get_solo().home_category_sections_count`
instead of the constant. New migration
`0006_sitesettings_home_category_sections_count`. Also added
`MIN_VALUE_MESSAGE`/`MAX_VALUE_MESSAGE` to `apps/core/forms.py` (USE_I18N=False
means every validated field needs an explicit Azerbaijani override,
same reasoning as the existing `MAX_LENGTH_MESSAGE`) — the first numeric
range-validated field in the project, so these didn't exist yet.

## Verification

`pytest`: `apps/cms/tests/test_media_upload.py` (new, 10 tests) —
stage/preview both require login, the staged response's `url` points at
`media_temp_preview` not a raw `/media/temp/` path, a freshly staged
file round-trips byte-for-byte through the preview view with the right
`Content-Type`, and four flavors of malformed/nonexistent `temp_id`
(wrong case, wrong length, wrong extension, a literal path-traversal
attempt that doesn't even match the URL pattern) all 404 rather than
touching the filesystem. `apps/cms/tests/test_settings.py` (new, 5
tests) — the homepage actually renders exactly N sections for a
configured N (both lower and higher than the old hardcoded default),
and the settings form rejects 0 and 9 while accepting 8. One test-design
mistake caught and fixed along the way: the "higher count" test
originally gave each category only one article, and since `HomeView`
excludes whichever article becomes the hero from also appearing in its
own category's section, that category's section came out empty (and
therefore dropped) by chance — fixed by giving each test category two
articles, unrelated to the setting being tested. 232 passed total
(217 + 10 + 5).

# Phase 34 ("show all categories" toggle for the homepage)

## What was asked

Follow-up to Phase 33's `home_category_sections_count` setting (capped
at 1–8): user has more than a couple of populated top-level categories
and wants a way to show all of them on the homepage, not just up to the
cap.

## Added: `SiteSettings.home_show_all_categories`

Considered a "0 means unlimited" sentinel on the existing count field
instead — rejected as a magic number an editor would have to already
know about, when the settings screen can just state the choice
directly. Added a separate `BooleanField` (default `False`, matching
prior behavior exactly):

- `apps/settings_app/models.py` — new field + migration
  `0007_sitesettings_home_show_all_categories`.
- `apps/settings_app/forms.py` — added to `SiteSettingsForm`, a plain
  `CheckboxInput` with a `data-role` for the JS below to target.
- `templates/cms/settings.html` — checkbox above the existing count
  field, reusing the `.cms-checkbox` label pattern already used for
  `is_featured`/`is_breaking` on the News form.
- `apps/news/views.py`'s `HomeView` — when the toggle is on, the
  top-level-categories queryset is left unsliced entirely; the count
  field is only applied (`[:count]`) when it's off.
- New `static/js/cms/settings.js` — toggles the count field between
  interactive and visually inert as the checkbox changes. Deliberately
  sets `readOnly`, not `disabled`: a `disabled` input is excluded from
  form submission outright, which would leave this required field
  empty and fail validation the moment "show all" is checked — `readOnly`
  keeps submitting its last value, which `HomeView` ignores anyway once
  the toggle is on. New `.form-field--disabled` style in
  `static/css/cms/settings.css` for the visual half of this (opacity,
  muted label) since `readOnly` alone doesn't grey anything out the way
  `disabled` natively would.

## Verification

`pytest`: `apps/cms/tests/test_settings.py` — homepage shows all 10 of
10 populated top-level categories when the toggle is on even though
`home_category_sections_count` is simultaneously set to 1 (proving the
count is genuinely ignored, not coincidentally satisfied); the toggle
itself saves correctly both on and back off (an unchecked HTML checkbox
sends nothing at all, which must reset the field to `False`, not leave
the previous value in place — confirmed explicitly rather than assumed).
234 passed total (232 + 2).

# Phase 35 (homepage caching — home_show_all_categories made its render cost uncapped)

## What was asked

Direct follow-up to Phase 34: user pointed out that with 15+ populated
top-level categories and "show all" enabled, the homepage would build
15 × 3 = 45+ article cards in one request — more DB queries (one per
category section, in `HomeView`'s loop) and a much heavier page than
before the toggle existed. Discussed three options (Redis-cache the
homepage, cap the total article count, reduce per-category count); user
chose caching only.

## Added: `HOME_CACHE_KEY` — the homepage's context cached in Redis, invalidated explicitly rather than left to expire

Redis was already configured (`config/settings/base.py`'s `CACHES`,
already used for sessions and `apps.accounts.services`' login-lockout
counters) — nothing new to provision, just the first view to actually
use it for content.

- `apps/news/views.py`'s `HomeView.get_context_data` — the expensive
  part (hero, category sections, popular news, breaking ticker) moved
  into `_build_home_context()`, cached under `HOME_CACHE_KEY` for
  `HOME_CACHE_TIMEOUT` (300s, a backstop — not the primary invalidation
  mechanism, see below). All querysets fully evaluated to lists before
  caching (`popular_news` needed an explicit `list()` it didn't have
  before; everything else already was) — a cached lazy queryset would
  just re-query on first access later, defeating the point.
- New `apps/news/signals.py` — `post_save`/`post_delete` on `News`
  invalidate the cache unconditionally. Wired via `apps/news/apps.py`'s
  new `ready()`. Deliberately does **not** cover the view-count
  increment in `NewsDetailView.get_object()` — that's a bulk
  `News.objects.filter(pk=...).update(...)`, which Django never routes
  through signals at all, and that turns out to be exactly right here:
  busting the homepage cache on every single article view (by far the
  highest-frequency write to this model) would defeat caching entirely.
- Two *other* bulk-`.update()` call sites do need to affect the
  homepage and don't fire signals either — grepped for every
  `News.objects...update(` in the codebase to find them both:
  `NewsBulkActionView`'s delete/publish/archive actions
  (`apps/cms/views/news.py`) and `publish_scheduled`
  (`apps/news/management/commands/publish_scheduled.py`, the cron job
  that flips a due Scheduled article to Published — see Phase 30). Both
  now call `cache.delete(HOME_CACHE_KEY)` directly right after their
  `.update()`. This last one matters most for staleness: the entire
  point of that command is an article going live with nobody touching
  the CMS, so it needs to appear immediately, not after the 300s
  backstop.

## Found and fixed while implementing: cache state was leaking across the entire test suite

`config/settings/development.py`/`test.py` never override `CACHES` —
every test hits the same real Redis instance dev/production use.
`apps/accounts/tests.py` already had its own module-scoped
`autouse=True` `cache.clear()` fixture for exactly this reason (login-
lockout counters), but scoped only to that one file — the new homepage
cache would have leaked between *any* two tests that both touch
`news:home`, in either direction, anywhere in the suite. Promoted that
fixture to the root `conftest.py` (global `autouse=True`, applies to
every test now) and removed the now-redundant duplicate from
`apps/accounts/tests.py`.

## Verification

`pytest`: new `apps/news/tests/test_home_cache.py` (6 tests) — a second
request doesn't call `_build_home_context` again (`unittest.mock.patch`,
not a fragile query-count comparison); creating a published article
invalidates the cache and the very next request reflects it without
anything manually clearing it; `NewsPermanentDeleteView`,
`NewsBulkActionView`'s publish action, and `publish_scheduled` each
invalidate correctly despite two of those three going through a bulk
`.update()` that no signal ever sees. 240 passed total (234 + 6).

# Phase 36 (site-wide nav/settings context cached in Redis)

## What was asked

Direct follow-up to Phase 35: user asked whether the other public pages
needed caching the same way. Recommended against it for category/tag/
article pages — already bounded by pagination (`LIMIT`/`OFFSET`, cost
doesn't grow with total row count) and confirmed as much together by
walking through exactly how Django's `ListView` pagination executes SQL.
Pointed at a better target instead:
`apps.core.context_processors.site()` — 3 queries (top-level categories,
`SiteSettings`, `SocialLink`) that run on literally every single page on
the site, for data that only changes when an editor touches the CMS.
User agreed to cache that.

## Added: `SITE_CONTEXT_CACHE_KEY`

Same pattern as Phase 35's `HOME_CACHE_KEY`, generalized:

- `apps/core/context_processors.py`'s `site()` — the query-building part
  moved into `_build_site_context()`, cached under `SITE_CONTEXT_CACHE_KEY`
  (300s backstop, same reasoning as the homepage — invalidation is the
  real mechanism). `social_links` needed an explicit `list()` it didn't
  have before (same lesson as `HomeView`'s `popular_news` in Phase 35 —
  a cached lazy queryset just re-queries on first access later).
- `apps/settings_app/models.py`'s `SiteSettings.get_solo()` — added
  `select_related('logo', 'favicon')`. Without it, the *cached* instance
  would still fire a fresh query for `site_settings.logo.file.url` on
  every cache hit in `base.html` — caching the row itself doesn't cache
  its foreign keys unless they're actually joined in.
- New `apps/core/signals.py` — `post_save`/`post_delete` on `Category`
  and `SocialLink`, `post_save` only on `SiteSettings` (its `delete()` is
  overridden to a no-op, so `post_delete` would never fire for it
  anyway). Wired via `apps/core/apps.py`'s new `ready()`.
- `CategoryReorderView` (`apps/cms/views/category.py`) uses
  `Category.objects.bulk_update(categories, ['order'])` for its drag-
  and-drop reorder — grepped for it specifically, since Phase 35 already
  established that Django never routes `bulk_update()`/`update()` through
  signals. Added an explicit `cache.delete(SITE_CONTEXT_CACHE_KEY)` right
  after it — nav order is exactly what that view changes.

## Found and fixed while implementing: 5 existing N+1 regression tests broke

Phase 32's `category__parent` regression tests (`apps/news`,
`apps/categories`, `apps/tags`, `apps/core`) each warmed up
`SiteSettings.get_solo()` directly to spend its one-time lazy-row-
creation cost before comparing two query captures. That warm-up never
went through an actual request, so it never touched
`apps.core.context_processors.site()` at all — meaning the *new* site-
context cache's own one-time populate cost (3 queries) now fell
entirely on whichever of the two captures ran first in each of those 5
tests, the exact same category of false mismatch Phase 32 had already
solved once for `SiteSettings.get_solo()` alone. Fixed by replacing each
manual `SiteSettings.get_solo()` call with a real warm-up HTTP request
(or a direct `handler404()` call, for the one test that doesn't use a
client) — any full render through `site()` populates both the
lazily-created row and the new cache in one pass. One test
(`test_article_detail_related_articles_query_count_does_not_scale`) was
already safe by coincidence — it already had its own warm-up request for
an unrelated reason (the view-count-once-per-session check) that happened
to cover this too.

## Verification

`pytest`: `apps/core/tests.py` (5 new tests) — a second request doesn't
call `_build_site_context` again; creating a `Category`, updating
`SiteSettings`, and creating/deleting a `SocialLink` each invalidate the
cache; `CategoryReorderView`'s bulk reorder invalidates it despite the
`bulk_update()` gap. 245 passed total (240 + 5).

# Phase 37 (real production slowness — nginx had neither gzip nor HTTP/2)

## What was asked

User reported the live site feels slow in real use and asked how to
actually check why, rather than guess.

## Diagnosed

`curl -w` timing breakdown against the live site, run from the VPS
itself against its own public IP (`--resolve spress.az:443:127.0.0.1`,
same technique used earlier to test HTTPS before DNS had propagated):
TTFB was 56ms, total 56.5ms. That ruled out Django/Gunicorn/Postgres —
the backend itself responds fast — and pointed at either network
distance or asset delivery. `sudo cat /etc/nginx/sites-available/spress.az`
(the live, certbot-edited file — different from `deploy/nginx.conf`'s
un-edited template, since certbot only ever edits the copy on the
server, never the repo) confirmed two real gaps at once:

1. **No gzip anywhere.** `deploy/nginx.conf` never had a `gzip` directive
   — a genuine, direct miss against CLAUDE.md ch.13 "Compression: Enable
   server compression... Gzip". `base.html` alone loads ~15 CSS files
   and ~6 JS files (CLAUDE.md ch.7/ch.8's one-file-per-concern rule) —
   every one of those transferred at full uncompressed size.
2. **No HTTP/2.** `listen 443 ssl;` — certbot added the SSL directives
   but not the `http2` keyword this time. Without it, that same pile of
   small CSS/JS files competes over HTTP/1.1's much smaller effective
   parallelism instead of one multiplexed HTTP/2 connection — exactly
   the shape of problem that reads as "the page feels slow" while the
   TTFB measurement says the opposite.

## Fixed

- `deploy/nginx.conf` — added a `gzip on` block (`text/plain, text/css,
  text/xml, application/json, application/javascript, application/xml+rss,
  image/svg+xml`; `text/html` needs no explicit entry — nginx always
  gzips it once `gzip on` regardless of `gzip_types`; images/fonts left
  out deliberately since WebP/WOFF2 are already compressed formats,
  regzipping them just burns CPU for no size win).
- `docs/DEPLOYMENT.md` step 10 — added 10b: confirm certbot's
  `listen 443 ssl;` line actually got `http2` added, with the exact
  manual fix if it didn't (this VPS's certbot run didn't).
- Live server: both applied by hand directly to
  `/etc/nginx/sites-available/spress.az` (not `deploy.sh` — this file
  lives outside the Django code deploy.sh manages entirely) — `listen 443
  ssl http2;`, plus the same gzip block — then `nginx -t && systemctl
  reload nginx`.

## Verification

Manual only — this is nginx config, not Django/pytest territory.
Re-ran the same `curl -w` timing command after reloading, plus
`curl -sI -H "Accept-Encoding: gzip" ... | grep -i content-encoding` to
confirm `Content-Encoding: gzip` is actually present on the response.

# Phase 38 (a CMS-wide toast on any form validation error)

## What was asked

Chasing what looked at first like a create-article redirect bug turned
out to be a real save succeeding exactly as designed — the actual report
underneath it was: submitting the News form without a Category shows its
inline red error correctly, but nothing else on the page signals that
anything went wrong, and that inline message is easy to miss on a long
form. Asked for a toast/popup in addition. Confirmed with the user this
should apply CMS-wide, not just News.

## Added: `FormErrorToastMixin`

`apps/core/mixins.py` — a small mixin overriding `form_invalid()` to add
`messages.error(...)` before calling `super().form_invalid(form)`, so the
existing toast pipeline (`components/toast.html`, already included in
`cms/base.html`) picks it up alongside the untouched inline field errors
— this only adds a signal, never replaces the field-level one.

Applied to all 13 CMS `CreateView`/`UpdateView` classes across the
project (grepped for every one, not just News, per the user's "all
forms" choice): `AdCreateView`/`AdUpdateView`, `CategoryCreateView`/
`CategoryUpdateView`, `NewsCreateView`/`NewsUpdateView`,
`PageCreateView`/`PageUpdateView`, `SettingsUpdateView`,
`SocialLinkCreateView`/`SocialLinkUpdateView`, `TagCreateView`/
`TagUpdateView`, `UserCreateView`/`UserUpdateView`. Placed first in each
MRO (`class NewsCreateView(FormErrorToastMixin, NewsAccessRequiredMixin, CreateView)`)
so its `form_invalid()` runs before Django's own re-render.
`FolderCreateView`/`FolderUpdateView` (`apps/cms/views/media.py`)
deliberately excluded — plain `View` subclasses that already call
`messages.error()` directly in their own `post()`, not
`ModelFormMixin.form_invalid()`, so the mixin wouldn't apply to them
architecturally.

## Verification

`pytest`: `apps/core/tests.py` (2 new tests) — an invalid News
submission (missing Category) returns 200 (not a redirect), the inline
`form.errors['category']` is still present, and the toast message is in
`response.context['messages']`; a second test repeats the same shape
against `CategoryCreateView` to confirm this isn't special-cased to
News. 247 passed total (245 + 2).

# Phase 39 (a pasted CKEditor link was invisible in article body text)

## What was asked

Screenshot showed a link pasted into an article's CKEditor content
rendering as plain black text, indistinguishable from surrounding
paragraph text, plus a request to not show the raw `https://` prefix.

## Found

`static/css/base/reset.css`'s global `a { color: inherit; text-decoration: none; }`
(intentional — lets UI chrome like nav/buttons/cards style links per
component) also silently applied to editor-pasted links inside article
body text, which `static/css/components/rich-text.css` (shared by
`.article__content` and static-page prose) never overrode.

## Fixed

`.rich-text-content a` — `color: var(--color-info)` (blue, the
conventional "this is a link" signal, distinct from the site's brand
red already used for CTAs/buttons elsewhere) plus underline and a hover
color shift to `--color-primary`. Scoped to rich text only — the
UI-wide reset everywhere else is untouched.

The `https://` prefix wasn't changed in code — explained to the user
instead why: the link's visible text and its actual `href` were
identical here (CKEditor autolinked the pasted raw URL), so removing
the prefix from the displayed text would make it diverge from the
underlying URL, which is a real accessibility/SEO regression, not a
cosmetic win — the correct fix is editorial, not technical: reselect
the link text in CKEditor and replace it with something meaningful
("rəsmi sayt", "ətraflı bura") while keeping the same href.

## Verification

Visual/CSS only — no Python behavior changed, nothing for `pytest` to
cover here.

# Phase 40 (static files had no cache-busting — deployed CSS/JS fixes could take up to 30 days to actually reach a browser)

## What was asked

Nothing directly — surfaced while confirming Phase 39's link-color fix:
user reported the color still wasn't showing after deploying and hard-
refreshing wasn't mentioned as tried yet, which raised the question of
whether the browser could even be seeing the new file at all.

## Found

`deploy/nginx.conf`'s `location /static/ { expires 30d; }` tells every
browser to cache static assets for 30 days with no revalidation. Neither
`config/settings/base.py` nor `production.py` set `STORAGES`/
`STATICFILES_STORAGE` — Django's default `StaticFilesStorage` keeps a
CSS/JS file's filename identical across every deploy. Combined, editing
`rich-text.css` and redeploying doesn't change its URL at all — a
browser that already cached it has no signal to re-fetch, and would
keep serving the pre-fix version for up to 30 days regardless of how
many times the fix is redeployed. A direct, confirmed miss against
CLAUDE.md ch.13 "Static Assets": "Use cache versioning for updates."

## Fixed

`config/settings/production.py` — added `STORAGES` with
`'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'}`,
which appends a content hash to every static filename during
`collectstatic` (already run every deploy, `deploy.sh`) and rewrites
every `{% static %}` reference to match — an unchanged file keeps its
URL (still cached, no wasted re-downloads), a changed one gets a new URL
the old 30-day cache entry is irrelevant to. `nginx.conf` needed no
change at all — it just serves whatever filenames exist on disk.

Caught and fixed one mistake before it shipped: `STORAGES` is a full
replacement of Django's own default, not a merge — an initial version
that set only the `'staticfiles'` key would have silently dropped the
`'default'` key entirely, breaking every `MediaFile` upload (not just
static files) the moment this deployed. Restated `'default':
{'BACKEND': 'django.core.files.storage.FileSystemStorage'}` explicitly
alongside it.

Scoped to `production.py` only, not `base.py`/`development.py` — dev
never runs `collectstatic` in the workflow this project uses (`runserver`
serves static files directly via `STATICFILES_FINDERS`), so hashed
filenames would add friction there for no benefit.

## Verification

No `pytest` coverage — this only matters under `DEBUG=False` with a
real `collectstatic` run, which the test suite's settings
(`config.settings.test` → `development.py`) never exercises. Verified
by hand instead: ran `collectstatic` locally against
`config.settings.production` (`DJANGO_SECRET_KEY`/`DJANGO_ALLOWED_HOSTS`
set inline, `STATIC_ROOT` monkey-patched to a scratch temp directory so
nothing in the real project tree was touched) — "283 static files
copied, 283 post-processed", zero errors, confirming every `url(...)`
reference inside every CSS file (self-hosted Noto Sans/Serif `@font-face`
rules, Bootstrap Icons' own already-hashed font URLs) resolves to a real
file on disk; a manifest-storage failure here throws loudly rather than
silently 404ing later. Then confirmed `{% static %}` itself resolves
through the manifest correctly: `static('css/components/rich-text.css')`
→ `/static/css/components/rich-text.d13c9d89757a.css`. Full `pytest`
suite re-run after the settings change anyway, to confirm nothing
elsewhere assumed the old storage backend: 247 passed, unchanged (test
settings never touch `production.py`, so this was expected, not a
meaningful signal either way).

# Phase 41 (real outage — deploy.sh's manage.py calls were silently running under development settings all along)

## What happened

Deploying Phase 40's `ManifestStaticFilesStorage` change took the live
site down: `deploy.sh`'s health check failed with HTTP 500, and the raw
response was Django's absolute last-resort fallback ("Internal Server
Error", not even this project's own `errors/500.html`) — meaning
`errors/500.html`'s *own* `{% static %}` references failed too, while
handling the first failure.

## Root cause

`manage.py`'s own fallback is `os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')`.
`deploy.sh`'s `manage.py migrate`/`collectstatic` calls never set this
explicitly — only `deploy/gunicorn.service`'s `EnvironmentFile=/opt/spress/.env`
correctly puts Gunicorn itself on `production`. This gap has existed
since `deploy.sh` was first written and stayed invisible for every prior
deploy: `development.py` and `production.py` both read the same
`DATABASE_URL`/`REDIS_URL` from `.env` via `django-environ`, so
`migrate` and plain `collectstatic` "worked" under either module with
no visible difference. `STORAGES` (Phase 40) was the first
production-only setting an actual `manage.py` subcommand's *behavior*
depended on — `collectstatic`, run under `development.py`, used the
default `StaticFilesStorage` and never built `staticfiles.json` at all.
Every `{% static %}` lookup at request time then raised
`ValueError: Missing staticfiles manifest entry for '...'` — including
inside `errors/500.html` itself, which is why even the custom error
page couldn't render and Django fell all the way back to its bare
built-in fallback.

Confirmed directly, not guessed: `manage.py collectstatic --noinput`
run by hand printed `283 static files copied` with **no** "post-
processed" count and no manifest file on disk; the exact same command
with `DJANGO_SETTINGS_MODULE=config.settings.production` forced in
front of it printed `283 static files copied, 283 post-processed` and
created `staticfiles.json` immediately.

## Fixed

- **Immediate recovery** (VPS, by hand): `rm -rf staticfiles`, re-ran
  `collectstatic` with `DJANGO_SETTINGS_MODULE=config.settings.production`
  forced explicitly, restarted Gunicorn. Confirmed `200` again within
  minutes of the outage starting.
- **Permanent fix**: `deploy/deploy.sh` now does
  `export DJANGO_SETTINGS_MODULE=config.settings.production` immediately
  after `cd "$PROJECT_ROOT"`, before any `manage.py` call — every
  command deploy.sh runs is now guaranteed to match what Gunicorn
  actually serves, closing this entire class of "which settings module
  is this actually running under" gap for good, not just the one
  symptom that happened to surface it.

## Verification

Manual, on the live server — this is deploy-script/ops territory, not
something `pytest` (which never invokes `deploy.sh` or shells out to
`manage.py` as a subprocess) could have caught. Re-confirmed `200` via
the same `curl --resolve` health-check command `deploy.sh` itself uses,
both immediately after the manual recovery and is expected to self-
verify on every future run now that the fix is in `deploy.sh` itself.

# Phase 42 (permanent user delete; self-service password change)

## What was asked

Two additions, discussed before implementing: Administrators should be
able to permanently delete a user, and any CMS user should be able to
change their own password without an admin's involvement.

## Context found before designing either

User had no hard-delete or `is_deleted` field at all — "removing" a
user has only ever meant deactivation (`is_active=False`,
`UserDeactivateView`/`UserActivateView`, fully reversible). The one FK
that matters for a real delete: `News.author` is `on_delete=PROTECT`
(every other reference — `ActivityLog.actor`, every `BaseModel.created_by`/
`updated_by` across categories/tags/pages/ads/media/social links/
settings — is `SET_NULL`). Separately, no self-service password change
existed anywhere: the only two password flows were both admin/email-
driven (`UserResetPasswordView` and the public "forgot password" flow),
and `docs/EMAIL_SETUP.md` already documents that both 500 without SMTP
configured, which isn't live on this deployment yet.

Discussed both before building: whether "delete" should mean an actual
hard delete or just clearer deactivation UI (chose real permanent
delete), and whether password change should be old+new password
in-CMS or wait for SMTP (chose old+new password — works today,
independent of email).

## Added: `UserDeleteView`

Mirrors the News/Category/Advertisement soft-delete-then-purge pattern
even though User has no `is_deleted` field of its own —
`is_active=False` is that checkpoint here instead:
`user_list.html`'s row menu only shows "Həmişəlik sil" once "Deaktiv
et" already has been (`UserDeleteView.get`/`post` both look up
`is_active=False`, 404 otherwise — same convention as
`CategoryPermanentDeleteView`). Blocks with a clear message (not a raw
`ProtectedError`) when `target.articles.exists()`; refuses self-deletion,
same reasoning as `UserDeactivateView`'s existing self-deactivation
refusal. New `ActivityLog.Action.USER_DELETED` +
`templates/cms/user_confirm_delete.html` (the `btn--danger` variant of
`user_confirm_deactivate.html`, matching `news_confirm_permanent_delete.html`'s
wording pattern).

## Added: `ChangePasswordView` — self-service, no email

`apps/cms/views/profile.py` (new file — a deliberately separate
concern from `user.py`, which is entirely "an Administrator manages
someone else's account"; this view only ever acts on `request.user`) —
subclasses Django's own `PasswordChangeView`, `LoginRequiredMixin` only
(none of `apps/core/mixins.py`'s role-scoped mixins fit, since every
authenticated CMS user needs this regardless of role). New
`ChangePasswordForm` (`apps/accounts/forms.py`, Azerbaijani labels,
same `USE_I18N=False` reasoning as the neighboring `SetPasswordForm`/
`PasswordResetForm`). Reachable from a new `bi-key` icon in the CMS
topbar (`templates/cms/base.html`), next to logout. New
`ActivityLog.Action.USER_PASSWORD_CHANGED`, distinct from the existing
admin-triggered `USER_PASSWORD_RESET`.

## Verification

`pytest`: new `apps/cms/tests/test_user_delete_and_password.py` (8
tests) — delete requires the target already deactivated (404
otherwise); a clean deactivated user is actually removed from the DB;
blocked (and kept in the DB) when the target authored an article;
self-delete refused; a non-Administrator gets 403; change-password
requires login; any role (tested with a Journalist, the least-
privileged role) can change their own password and the new password
actually works afterward (`user.check_password(...)`); a wrong current
password is rejected and the password stays unchanged. 255 passed
total (247 + 8).

# Phase 44 (CKEditor lists were invisible — same root cause as Phase 39's invisible links)

## What was asked

User reported CKEditor's list buttons "don't work" — clicking bulleted/
numbered list did nothing visible. Separately asked about adding text/
background color to the editor toolbar; declined after discussing the
trade-off (CLAUDE.md ch.9's deliberately minimal toolbar exists so
articles share consistent typography instead of per-editor color
choices) — no code change for that part.

## Diagnosed

Confirmed it wasn't a missing plugin first (grepped django_ckeditor_5's
bundled `bundle.js` for `bulletedList`/`numberedList`/`ListEditing`/
`ListUI` — all present) before looking anywhere else. Then asked the
user to check the toolbar button's own active/pressed state when
clicked, not just the text — it *did* highlight, meaning CKEditor's
`bulletedList`/`numberedList` command was executing successfully and
producing real `<ul>`/`<li>` elements; they just weren't rendering as a
list. Exact same root cause as Phase 39's invisible links:
`base/reset.css`'s `ul, ol { list-style: none; padding: 0; margin: 0; }`
resets every list on the site for UI chrome (nav menus, card lists) —
and, same as the `<a>` reset before it, silently strips every bullet/
number and its indent from CKEditor-produced lists too, both in the
final published article *and inside the CKEditor editing area itself*
(the editor's own live preview uses the same site-wide CSS).

## Fixed

`static/css/components/rich-text.css` — extended the `<a>` rule from
Phase 39 and added new `ul`/`ol`/`li` rules, this time targeting two
selectors together: `.rich-text-content` (published output) **and**
`.ck-content` (CKEditor5's own editing-view root class, confirmed
present in `bundle.js`) — so an editor sees the actual final look while
typing instead of a WYSIWYG mismatch, not just a fix that only shows up
after publishing. `templates/cms/news_form.html` and `page_form.html`
(the only two CKEditor5 fields in the project — `News.content` and
`Page.content`) now load `rich-text.css`, which neither previously did.

## Verification

Visual/CSS only, same as Phase 39 — no Python behavior changed. Full
`pytest` suite re-run anyway (255 passed, unchanged) and `collectstatic`
re-verified clean under `config.settings.production`
(`ManifestStaticFilesStorage`, Phase 40) against a scratch `STATIC_ROOT`
before pushing, given Phase 41's incident was triggered by exactly this
kind of static-file change.

# Phase 45 (About page 404 — a hardcoded slug expectation; hardcoded stats made CMS-managed)

## What was asked

User created a "Haqqımızda" page in the CMS, but the public `/about/`
link still 404'd. Separately, once that was fixed, pointed out that
the About page's three "number + label" cards (2018/40+/7) can't be
edited or removed from the CMS at all.

## Diagnosed: `AboutView` looks up a hardcoded slug the CMS never told the editor to use

`apps/pages/views.py`'s `AboutView.get_context_data()` does
`get_object_or_404(Page, slug=ABOUT_SLUG, is_published=True)`, where
`ABOUT_SLUG` used to be `az_slugify('Haqqımızda')` → `'haqqimizda'` —
a value derived from the display title, never shown to the editor
anywhere in the CMS `Page` form (which has a perfectly normal, editable
"URL slug" field). Asked the user what slug their page actually had:
`about`. Two different strings, so the lookup never matched even
though the page existed and was published — the generic
`PageDetailView` catch-all route would have served it fine at its own
URL, just not at `/about/` specifically, which is what `header.html`/
`footer.html` both hardcode a link to.

## Fixed: `ABOUT_SLUG` is now the literal the user actually wants, not a derived one

`ABOUT_SLUG = 'about'` — a plain literal instead of `az_slugify(...)`,
since there's no actual requirement that the slug match the display
title's transliteration; `'about'` is a perfectly normal choice.
Updated `apps/core/management/commands/seed_initial_data.py`'s seed
Page entry to set `'slug': 'about'` explicitly too (it previously had
no explicit slug at all, relying on the now-wrong auto-generation), and
fixed `apps/pages/tests.py`'s `test_about_page_renders_when_published`,
which had the same latent assumption.

## Added: `AboutStat` — the hardcoded number/label cards are now a real CMS-managed list

Discussed two options before building — delete the cards entirely
(move similar content into the page's own CKEditor body) vs. a proper
CMS-managed list; chose the list. `apps/settings_app/models.py`'s new
`AboutStat` (`number` — a `CharField`, not an integer, since real
values include non-numeric text like "40+" — `label`, `order`) is the
same flat-list-with-manual-ordering shape as the existing `SocialLink`
right above it in that file, and every layer around it mirrors
`SocialLink`'s exactly: `AboutStatForm`, `apps/cms/views/about_stat.py`
(`AdministratorRequiredMixin` throughout, same access level as
`SocialLink`), `cms/about_stat_{list,form,confirm_delete}.html`, and a
"Statistikanı idarə et" card linked from `settings.html` next to the
existing "Sosial şəbəkələri idarə et" one. `apps.pages.views.AboutView`
now passes `AboutStat.objects.all()` into context;
`templates/pages/about.html`'s three hardcoded `.about-page__stat`
blocks became one `{% for %}` loop.

## Verification

`pytest`: `apps/cms/tests/test_crud.py` — `AboutStat` create/edit/delete
round-trips through the real CMS form and logs `ActivityLog`
(`ABOUT_STAT_CREATED`/`UPDATED`/`DELETED`), a non-Administrator gets
403; `apps/pages/tests.py` — the public About page actually renders
CMS-created stat rows (number and label both present in the response),
plus the existing About-page tests updated for the new fixed slug.
`makemigrations --check` clean, `collectstatic` re-verified under
`config.settings.production` again (same reasoning as Phase 44). 258
passed total (255 + 3).

# Phase 46 (short_description was invisible everywhere except the homepage hero)

## What was asked

User noticed News' "Qısa təsvir" (short_description) shows on the
homepage hero but not on the article detail page, and asked what it's
actually for, whether it should appear elsewhere, and whether it
should stay required. Discussed before changing anything.

## Found

`short_description` was doing real work already, just invisibly:
`news/detail.html` only ever read it inside `<meta name="description">`/
`og:description`/the JSON-LD `NewsArticle.description` — never as
visible page text — despite its own form widget
(`apps/news/forms.py`) already using the placeholder "Qısa təsvir
(dek)..." ("dek" — journalism term for a lead sentence under a
headline), implying it was always meant to render as one. Separately,
`components/news_card.html` (reused by category pages, search results,
tag pages, and "Oxşar xəbərlər") never showed it either — a direct gap
against CLAUDE.md ch.6 "Cards", which explicitly lists "Short
description" as a standard news-card field.

Discussed three questions and got a decision on each: show it as a
deck under the headline on the article page (yes); show it on regular
news cards too, matching the CLAUDE.md card spec (yes); keep it a
required field, given it now visibly matters in more places, not just
SEO (yes, unchanged).

## Fixed

- `templates/news/detail.html` — `article.short_description` now
  renders as `<p class="article__deck type-body-lg">` between the
  headline and the byline. New `.article__deck` rule in
  `static/css/pages/article.css` (color/spacing only — sizing comes
  from the existing `.type-body-lg` utility, not duplicated here).
- `templates/components/news_card.html` — same field added between
  title and meta, as `<p class="news-card__excerpt">`. New
  `.news-card__excerpt` in `static/css/components/cards.css`,
  line-clamped to 2 lines (1 for the `--compact` variant used by
  related articles) so a long excerpt can't stretch card heights
  unevenly across a grid row — reused by every page that includes this
  component, not just one.

## Verification

`pytest`: two new tests in `apps/news/tests/test_public_views.py` —
the article detail page's rendered HTML now contains
`short_description`'s text; a search-results card (exercising
`news_card.html`, the same component every other card-rendering page
shares) does too. `collectstatic` re-verified clean under
`config.settings.production` (same reasoning as Phase 44/45 — this
touched CSS again). 260 passed total (258 + 2).

# Phase 47 (author byline made opt-in, off by default)

## What was asked

Editor asked that the article byline stop automatically showing the
writer's name — most articles are aggregated/edited by staff rather
than individually reported, so the default should be anonymous
("Redaksiya"), with a checkbox on the News form to opt a specific
article into showing its real author.

## Added: `News.show_author_name`

New `BooleanField(default=False)` — off by default, matching the
request directly (not a "0 means unlimited"-style sentinel on an
existing field; a plain boolean is the actual right shape here). Added
to `NewsForm` and `news_form.html` right next to the existing
`is_featured`/`is_breaking` checkboxes, with an inline hint explaining
the fallback.

Two display sites needed the conditional, both in
`templates/news/detail.html` (grepped for every `article.author`
reference in public templates first to make sure neither was missed):

- The visible byline (`.article__author-name`) — shows the real name
  when checked, `"Redaksiya"` otherwise.
- The `NewsArticle` JSON-LD structured data's `author` object — when
  off, switches from `@type: Person` (a specific individual) to
  `@type: Organization` (the site itself, via `site_settings.site_name`)
  rather than either lying with a fake Person name or omitting `author`
  entirely, which Google's structured-data guidelines expect populated
  either way.

## Verification

`pytest`: `apps/news/tests/test_public_views.py` — the byline shows
"Redaksiya" and not the author's username by default; shows the real
username once `show_author_name=True`; `apps/cms/tests/test_crud.py` —
the checkbox actually persists as `True` when submitted checked, and
back to `False` when the field is omitted entirely (an unchecked HTML
checkbox sends nothing at all — the same "must actually reset, not
just leave the old value" concern verified for `home_show_all_categories`
in Phase 34). `makemigrations --check` clean. 263 passed total
(260 + 3).
