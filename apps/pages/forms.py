from django import forms

from apps.core.forms import INVALID_EMAIL_MESSAGE, MAX_LENGTH_MESSAGE, REQUIRED_MESSAGE

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
        # USE_I18N = False (apps/core/forms.py docstring) — title/content
        # are the only required fields here.
        error_messages = {
            'title': {**REQUIRED_MESSAGE, **MAX_LENGTH_MESSAGE},
            'content': REQUIRED_MESSAGE,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['og_image'].required = False


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=120, label='Ad Soyad',
        widget=forms.TextInput(attrs={'class': FIELD_CLASS}),
        error_messages={**REQUIRED_MESSAGE, **MAX_LENGTH_MESSAGE},
    )
    # Neither is required on its own — clean() below only requires that at
    # least one of the two is filled in, so a sender can leave out
    # whichever reply channel they don't want to share.
    email = forms.EmailField(
        label='E-poçt', required=False,
        widget=forms.EmailInput(attrs={'class': FIELD_CLASS}),
        error_messages={**INVALID_EMAIL_MESSAGE},
    )
    phone = forms.CharField(
        max_length=30, label='Telefon', required=False,
        widget=forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': '+994 XX XXX XX XX'}),
        error_messages={**MAX_LENGTH_MESSAGE},
    )
    subject = forms.CharField(
        max_length=200, label='Mövzu',
        widget=forms.TextInput(attrs={'class': FIELD_CLASS}),
        error_messages={**REQUIRED_MESSAGE, **MAX_LENGTH_MESSAGE},
    )
    message = forms.CharField(
        max_length=4000, label='Mesaj',
        widget=forms.Textarea(attrs={'class': FIELD_CLASS, 'rows': 6}),
        error_messages={**REQUIRED_MESSAGE, **MAX_LENGTH_MESSAGE},
    )

    def clean(self):
        cleaned_data = super().clean()
        if not cleaned_data.get('email') and not cleaned_data.get('phone'):
            self.add_error(None, 'E-poçt və ya telefon nömrəsindən ən azı birini daxil edin.')
        return cleaned_data
