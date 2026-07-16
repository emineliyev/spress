from django import forms

from .models import Page

FIELD_CLASS = 'form-input'


class PageForm(forms.ModelForm):
    """CMS management for Page (apps/cms/views/page.py). Now exposes the
    full SEOFieldsMixin set (Phase 11) — previously only meta_title/
    meta_description were editable here."""

    class Meta:
        model = Page
        fields = [
            'title', 'slug', 'content', 'is_published',
            'meta_title', 'meta_description', 'meta_keywords', 'canonical_url',
            'og_title', 'og_description', 'og_image', 'robots_index', 'robots_follow',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'title-input'}),
            'slug': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'slug-input'}),
            'meta_title': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'meta_description': forms.Textarea(attrs={'class': FIELD_CLASS, 'rows': 3}),
            'meta_keywords': forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': 'açar, sözlər, vergüllə'}),
            'canonical_url': forms.URLInput(attrs={'class': FIELD_CLASS, 'placeholder': 'https://...'}),
            'og_title': forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': 'Sosial şəbəkələrdə görünəcək başlıq'}),
            'og_description': forms.Textarea(attrs={'class': FIELD_CLASS, 'rows': 3}),
            # Not a visible widget — static/js/cms/image-pickers.js sets
            # this hidden input's value once an image is staged/cropped
            # via the Media Library pipeline.
            'og_image': forms.HiddenInput(attrs={'data-role': 'picker-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['og_image'].required = False


# USE_I18N = False means Django's own built-in field error messages
# ("This field is required.", "Enter a valid email address.") render as
# literal English with no translation catalog to fall back on — the same
# root cause already fixed for LoginForm/PasswordResetForm/SetPasswordForm
# (apps/accounts/forms.py). Every field below gets an explicit Azerbaijani
# override for the same reason.
_REQUIRED_MESSAGE = {'required': 'Bu sahənin doldurulması mütləqdir.'}
_MAX_LENGTH_MESSAGE = {'max_length': 'Bu sahə ən çoxu %(limit_value)d simvol ola bilər.'}


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120, label='Ad Soyad',
        widget=forms.TextInput(attrs={'class': FIELD_CLASS}),
        error_messages={**_REQUIRED_MESSAGE, **_MAX_LENGTH_MESSAGE},
    )
    email = forms.EmailField(
        label='E-poçt',
        widget=forms.EmailInput(attrs={'class': FIELD_CLASS}),
        error_messages={**_REQUIRED_MESSAGE, 'invalid': 'Düzgün e-poçt ünvanı daxil edin.'},
    )
    subject = forms.CharField(
        max_length=200, label='Mövzu',
        widget=forms.TextInput(attrs={'class': FIELD_CLASS}),
        error_messages={**_REQUIRED_MESSAGE, **_MAX_LENGTH_MESSAGE},
    )
    message = forms.CharField(
        max_length=4000, label='Mesaj',
        widget=forms.Textarea(attrs={'class': FIELD_CLASS, 'rows': 6}),
        error_messages={**_REQUIRED_MESSAGE, **_MAX_LENGTH_MESSAGE},
    )
