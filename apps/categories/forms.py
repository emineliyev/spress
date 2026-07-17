from django import forms

from apps.core.forms import REQUIRED_MESSAGE

from .models import Category

FIELD_CLASS = 'form-input'


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'slug', 'parent', 'is_active']
        # USE_I18N = False (apps/core/forms.py docstring)
        error_messages = {'name': REQUIRED_MESSAGE}
        widgets = {
            'name': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'title-input'}),
            'slug': forms.TextInput(attrs={'class': FIELD_CLASS, 'data-role': 'slug-input'}),
            'parent': forms.Select(attrs={'class': FIELD_CLASS}),
            'is_active': forms.CheckboxInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
        self.fields['parent'].required = False

        parent_queryset = Category.objects.active().visible().top_level()
        if self.instance.pk:
            parent_queryset = parent_queryset.exclude(pk=self.instance.pk)
        self.fields['parent'].queryset = parent_queryset

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        if parent and self.instance.pk and self.instance.children.exists():
            self.add_error(
                'parent',
                'Bu kateqoriyanın alt-kateqoriyaları var, ona görə özü başqa bir '
                'kateqoriyanın alt-kateqoriyası edilə bilməz.',
            )
        return cleaned_data
