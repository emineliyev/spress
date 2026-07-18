"""
Shared settings for all environments.

Environment-specific overrides live in development.py / production.py.
Nothing here should ever contain secrets — every sensitive or
environment-dependent value is read from the process environment
(CLAUDE.md ch.12 "Environment Variables").
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY')

AUTH_USER_MODEL = 'accounts.User'
LOGIN_URL = 'accounts:login'
LOGIN_REDIRECT_URL = 'cms:dashboard'


# ---------------------------------------------------------------------------
# Applications
# ---------------------------------------------------------------------------

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
]

THIRD_PARTY_APPS = [
    # CKEditor 5, not django-ckeditor's bundled CKEditor 4 — CKEditor 4 is
    # EOL with unfixed security issues (Django itself warns about this on
    # startup; CLAUDE.md ch.15 "avoid abandoned libraries"). The image
    # upload endpoint it ships is staff-gated by default but deliberately
    # unused (no upload button in the toolbar below) — a file-upload path
    # that bypasses MediaFile would create a second, inconsistent image
    # pipeline ahead of the Media Library phase.
    'django_ckeditor_5',
]

PROJECT_APPS = [
    'apps.core',
    'apps.accounts',
    'apps.users',
    'apps.categories',
    'apps.tags',
    'apps.news',
    'apps.media_manager',
    'apps.seo',
    'apps.settings_app',
    'apps.advertisements',
    'apps.pages',
    'apps.cms',
    'apps.logs',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + PROJECT_APPS

# CKEditor 5 toolbar — the full CLAUDE.md ch.3 allow-list. Images upload
# through CKEditorImageUploadView (apps/cms/views/media.py), which reuses
# the Media Library pipeline (stage_upload/process_crop — WebP, thumbnail,
# a real MediaFile row) instead of django_ckeditor_5's own upload view,
# which would just dump the raw file under MEDIA_ROOT. Video uses a
# custom, YouTube-only mediaEmbed provider (static/js/cms/
# ckeditor-youtube-embed.js) instead of the library default, which would
# both allow every provider (Vimeo/Twitter/…, not asked for) and save
# inline `style="..."` attributes CLAUDE.md forbids. Must match
# apps/core/utils.py's bleach allow-list.
CKEDITOR_5_CONFIGS = {
    'default': {
        'toolbar': [
            'heading', '|',
            'bold', 'italic', 'underline', '|',
            'bulletedList', 'numberedList', 'blockQuote', '|',
            'link', 'insertTable', 'uploadImage', 'mediaEmbed', '|',
            'alignment', '|',
            'undo', 'redo',
        ],
        'image': {
            # alignLeft/alignRight float the image and let body text wrap
            # around it (user-requested) — produces `image-style-align-
            # left/right` classes, styled in static/css/components/
            # rich-text.css. alignCenter/block stay available as the
            # non-wrapping default.
            #
            # No equivalent exists for video: tried the generic Style
            # plugin (bundled) with `element: 'figure'` and `element:
            # 'oembed'` targeting the MediaEmbed widget — its toolbar
            # button stayed disabled either way (verified live in a
            # browser, not assumed from docs). CKEditor5's Style command
            # only recognizes schemas it has built-in support for
            # (image, table); MediaEmbed's widget isn't one of them, and
            # extending that requires writing an actual CKEditor5 plugin
            # (a JS class with its own schema/converter registration),
            # not a config change — this bundle is pre-built by
            # django_ckeditor_5, not compiled from source in this
            # project, so that's a materially bigger undertaking than
            # this phase's other changes.
            'toolbar': [
                'imageStyle:alignLeft', 'imageStyle:alignCenter', 'imageStyle:alignRight', '|',
                'toggleImageCaption', 'imageTextAlternative',
            ],
        },
        'mediaEmbed': {
            'previewsInData': True,
            'providers': [
                {
                    # A single combined regex, not a list of three — the
                    # widget's JS config reviver (django_ckeditor_5's
                    # app.js) detects a regex-shaped value by calling
                    # `value.toString()`, and `Array.prototype.toString()`
                    # joins elements with commas before that check runs,
                    # silently mangling a list of regex strings into one
                    # unusable blob. One alternation avoids the bug
                    # entirely (match[1] is the video ID in every branch).
                    'name': 'youtube',
                    'url': r'/^(?:(?:m\.)?youtube\.com\/(?:watch\?v=|shorts\/)|youtu\.be\/)([\w-]+)/',
                    'html': 'callback:ckeditorYoutubeEmbedHtml',
                },
            ],
        },
        'height': 420,
    },
}

# Points django_ckeditor_5's widget at our own upload view instead of the
# package's default (see CKEDITOR_5_CONFIGS comment above).
CK_EDITOR_5_UPLOAD_FILE_VIEW_NAME = 'cms:ckeditor_image_upload'

# Trimmed from the package's default ('jpeg','png','gif','bmp','webp',
# 'tiff') down to what apps/media_manager/services.py's
# ALLOWED_CONTENT_TYPES actually accepts, so the file picker doesn't
# offer formats the pipeline would just reject after upload. 'svg' is
# deliberately absent: CKEditor5's own Image plugin has no built-in
# extension→MIME entry for it (confirmed — the file input's rendered
# `accept` attribute has no `image/svg+xml` regardless of this setting),
# so it's never actually selectable through this button no matter what's
# listed here. SVGs remain fully supported everywhere else (Media
# Library, Featured/OG image pickers) — only inline body-content SVG
# insertion isn't possible, a CKEditor5 limitation, not this project's.
CKEDITOR_5_UPLOAD_FILE_TYPES = ['jpeg', 'png', 'webp']

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site',
                'apps.core.context_processors.cms_notifications',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'


# ---------------------------------------------------------------------------
# Database (PostgreSQL — CLAUDE.md ch.10, never SQLite in production)
# ---------------------------------------------------------------------------

DATABASES = {
    'default': env.db(
        'DATABASE_URL',
        default='postgres://postgres:postgres@localhost:5432/news_db',
    ),
}
DATABASES['default']['ATOMIC_REQUESTS'] = True


# ---------------------------------------------------------------------------
# Cache (Redis — CLAUDE.md ch.13)
# ---------------------------------------------------------------------------

REDIS_URL = env('REDIS_URL', default='redis://127.0.0.1:6379/1')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
    },
}
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'


# ---------------------------------------------------------------------------
# Celery (background tasks — CLAUDE.md ch.4/13)
# ---------------------------------------------------------------------------

CELERY_BROKER_URL = env('CELERY_BROKER_URL', default=env('REDIS_URL', default='redis://127.0.0.1:6379/2'))
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default=CELERY_BROKER_URL)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'Asia/Baku'


# ---------------------------------------------------------------------------
# Password validation
# ---------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 10}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# ---------------------------------------------------------------------------
# Localization — single language (Azerbaijani), no i18n architecture
# (CLAUDE.md ch.3 "Language" — do not implement translation models/i18n)
# ---------------------------------------------------------------------------

LANGUAGE_CODE = 'az'
TIME_ZONE = 'Asia/Baku'
USE_I18N = False
USE_TZ = True


# ---------------------------------------------------------------------------
# Static & media files (CLAUDE.md ch.3 "File Storage" — never mixed)
# ---------------------------------------------------------------------------

STATIC_URL = 'static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ---------------------------------------------------------------------------
# Logging (CLAUDE.md ch.3/12 — separate application/security/errors/tasks logs)
# ---------------------------------------------------------------------------

LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'structured': {
            'format': '{asctime} {levelname} {name} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'structured',
        },
        'application_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'application.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'structured',
        },
        'security_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'security.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'structured',
        },
        'error_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'errors.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'structured',
        },
        'tasks_file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': LOG_DIR / 'tasks.log',
            'maxBytes': 10 * 1024 * 1024,
            'backupCount': 5,
            'formatter': 'structured',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'application_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.request': {
            'handlers': ['console', 'error_file'],
            'level': 'ERROR',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console', 'security_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'celery': {
            'handlers': ['console', 'tasks_file'],
            'level': 'INFO',
            'propagate': False,
        },
        'news_portal': {
            'handlers': ['console', 'application_file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
