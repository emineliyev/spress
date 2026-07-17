from django import forms

from apps.core.forms import REQUIRED_MESSAGE

from .models import Tag

FIELD_CLASS = 'form-input'


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'slug']
        # USE_I18N = False (apps/core/forms.py docstring)
        error_messages = {'name': REQUIRED_MESSAGE}
        widgets = {
            'name': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'title-input'}),
            'slug': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'slug-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
