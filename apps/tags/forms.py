from django import forms

from .models import Tag

FIELD_CLASS = 'form-input'


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name', 'slug']
        widgets = {
            'name': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'title-input'}),
            'slug': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'slug-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
