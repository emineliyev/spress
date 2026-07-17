from django import forms

from apps.core.forms import INVALID_URL_MESSAGE, REQUIRED_MESSAGE

from .models import AdPosition, Advertisement

FIELD_CLASS = 'form-input'


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = [
            'title', 'position', 'banner', 'target_url', 'client_name',
            'price', 'start_date', 'end_date', 'is_active',
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'position': forms.Select(attrs={'class': FIELD_CLASS}),
            # Not a visible widget — static/js/cms/settings.js's
            # initImagePickers() sets this hidden input's value once a
            # banner is staged/cropped via the Media Library pipeline.
            'banner': forms.HiddenInput(attrs={'data-role': 'picker-input'}),
            'target_url': forms.URLInput(attrs={'class': FIELD_CLASS, 'placeholder': 'https://...'}),
            'client_name': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'price': forms.NumberInput(attrs={'class': FIELD_CLASS, 'step': '0.01'}),
            'start_date': forms.DateTimeInput(attrs={'class': FIELD_CLASS, 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'end_date': forms.DateTimeInput(attrs={'class': FIELD_CLASS, 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
        }
        # USE_I18N = False (apps/core/forms.py docstring) — without this,
        # a blank required field (most often "Başlama tarixi", which has
        # no obvious visual "required" cue) rendered Django's stock
        # English "This field is required." — easy to miss or not
        # recognize, which reads as "the form silently isn't saving"
        # rather than a fixable validation error.
        error_messages = {
            'title': REQUIRED_MESSAGE,
            'position': REQUIRED_MESSAGE,
            'banner': REQUIRED_MESSAGE,
            'target_url': {**REQUIRED_MESSAGE, **INVALID_URL_MESSAGE},
            'start_date': REQUIRED_MESSAGE,
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].queryset = AdPosition.objects.filter(is_active=True)
        self.fields['end_date'].required = False
        self.fields['start_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_date'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        position = cleaned_data.get('position')
        is_active = cleaned_data.get('is_active')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        if start_date and end_date and end_date <= start_date:
            self.add_error('end_date', 'Bitmə tarixi başlama tarixindən sonra olmalıdır.')

        # {% ad_slot %} (apps/advertisements/templatetags/ads.py) just
        # picks the most-recently-created active campaign for a position —
        # two simultaneously-active campaigns in the same slot means the
        # older one silently stops showing, with no warning anywhere. Block
        # it here instead (user's explicit choice over auto-deactivating).
        if position and is_active and start_date:
            conflicting = Advertisement.objects.visible().filter(position=position, is_active=True)
            if self.instance.pk:
                conflicting = conflicting.exclude(pk=self.instance.pk)
            for other in conflicting:
                if _ranges_overlap(start_date, end_date, other.start_date, other.end_date):
                    self.add_error(
                        'position',
                        f'Bu mövqedə "{other.title}" adlı reklam artıq bu tarix aralığında aktivdir. '
                        'Əvvəlcə onu deaktiv edin və ya silin.',
                    )
                    break

        return cleaned_data


def _ranges_overlap(start_a, end_a, start_b, end_b):
    """True if [start_a, end_a] and [start_b, end_b] share any point in
    time — either end may be `None`, meaning "no upper bound"."""
    if end_a is not None and start_b > end_a:
        return False
    if end_b is not None and start_a > end_b:
        return False
    return True
