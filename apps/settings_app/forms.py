from django import forms

from apps.core.forms import INVALID_URL_MESSAGE, MAX_VALUE_MESSAGE, MIN_VALUE_MESSAGE, REQUIRED_MESSAGE

from .models import HOME_CATEGORY_SECTIONS_MAX, HOME_CATEGORY_SECTIONS_MIN, SiteSettings, SocialLink

FIELD_CLASS = 'form-input'


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'footer_text', 'contact_email',
            'logo', 'favicon',
            'contact_phone', 'contact_address',
            'home_category_sections_count',
        ]
        # USE_I18N = False (apps/core/forms.py docstring)
        error_messages = {
            'site_name': REQUIRED_MESSAGE,
            'home_category_sections_count': {**MIN_VALUE_MESSAGE, **MAX_VALUE_MESSAGE},
        }
        widgets = {
            'site_name': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'footer_text': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'contact_email': forms.EmailInput(attrs={'class': FIELD_CLASS}),
            # Not visible widgets — static/js/cms/image-pickers.js sets
            # these hidden inputs' values once an image is staged/cropped
            # via the Media Library pipeline (see templates/cms/settings.html).
            'logo': forms.HiddenInput(attrs={'data-role': 'picker-input'}),
            'favicon': forms.HiddenInput(attrs={'data-role': 'picker-input'}),
            'contact_phone': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'contact_address': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'home_category_sections_count': forms.NumberInput(attrs={
                'class': FIELD_CLASS,
                'min': HOME_CATEGORY_SECTIONS_MIN,
                'max': HOME_CATEGORY_SECTIONS_MAX,
            }),
        }


class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ['platform', 'url', 'order']
        # USE_I18N = False (apps/core/forms.py docstring)
        error_messages = {
            'platform': REQUIRED_MESSAGE,
            'url': {**REQUIRED_MESSAGE, **INVALID_URL_MESSAGE},
        }
        widgets = {
            'platform': forms.Select(attrs={'class': FIELD_CLASS}),
            'url': forms.URLInput(attrs={'class': FIELD_CLASS, 'placeholder': 'https://...'}),
            'order': forms.NumberInput(attrs={'class': FIELD_CLASS, 'min': 0}),
        }
