from django import forms

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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['position'].queryset = AdPosition.objects.filter(is_active=True)
        self.fields['end_date'].required = False
        self.fields['start_date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['end_date'].input_formats = ['%Y-%m-%dT%H:%M']

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        if start_date and end_date and end_date <= start_date:
            self.add_error('end_date', 'Bitmə tarixi başlama tarixindən sonra olmalıdır.')
        return cleaned_data
