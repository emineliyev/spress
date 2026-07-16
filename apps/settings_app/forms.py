from django import forms

from .models import SiteSettings, SocialLink

FIELD_CLASS = 'form-input'


class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSettings
        fields = [
            'site_name', 'footer_text', 'contact_email',
            'logo', 'favicon',
            'contact_phone', 'contact_address',
        ]
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
        }


class SocialLinkForm(forms.ModelForm):
    class Meta:
        model = SocialLink
        fields = ['platform', 'url', 'order']
        widgets = {
            'platform': forms.Select(attrs={'class': FIELD_CLASS}),
            'url': forms.URLInput(attrs={'class': FIELD_CLASS, 'placeholder': 'https://...'}),
            'order': forms.NumberInput(attrs={'class': FIELD_CLASS, 'min': 0}),
        }
