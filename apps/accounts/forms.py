from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import PasswordChangeForm as DjangoPasswordChangeForm
from django.contrib.auth.forms import PasswordResetForm as DjangoPasswordResetForm
from django.contrib.auth.forms import SetPasswordForm as DjangoSetPasswordForm
from django.forms import PasswordInput, TextInput

from .models import User

FIELD_CLASS = 'form-input'


class LoginForm(AuthenticationForm):
    """Azerbaijani labels — see PasswordResetForm below for why Django's
    own built-in "Username"/"Password" labels render as literal English
    (USE_I18N = False, no translation catalog to fall back on)."""

    error_messages = {
        # No %(username)s placeholder — Django fills it from the model
        # field's verbose_name ("username"), not this form's Azerbaijani
        # label override below, so it would render as literal English
        # either way.
        'invalid_login': (
            'Zəhmət olmasa düzgün istifadəçi adı və şifrə daxil edin. '
            'Hər iki sahə böyük/kiçik hərflərə həssas ola bilər.'
        ),
        'inactive': 'Bu hesab deaktiv edilib.',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'İstifadəçi adı'
        self.fields['username'].widget = TextInput(attrs={'class': FIELD_CLASS, 'autofocus': True})
        self.fields['password'].label = 'Şifrə'
        self.fields['password'].widget = PasswordInput(attrs={'class': FIELD_CLASS})


class PasswordResetForm(DjangoPasswordResetForm):
    """Azerbaijani labels for Django's built-in form — this project has
    `USE_I18N = False` (CLAUDE.md ch.3 "No multilingual architecture"), so
    Django's own English field labels/help text render as literal English
    with no translation catalog to fall back on. Overridden here rather
    than left as-is, the same way every other form in this project hand-
    writes its Azerbaijani labels."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].label = 'E-poçt'
        self.fields['email'].widget.attrs.update({'class': FIELD_CLASS})


class SetPasswordForm(DjangoSetPasswordForm):
    """Same USE_I18N=False reasoning as PasswordResetForm above."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['new_password1'].label = 'Yeni şifrə'
        self.fields['new_password1'].widget.attrs.update({'class': FIELD_CLASS})
        self.fields['new_password1'].help_text = (
            'Şifrə ən azı 10 simvoldan ibarət olmalıdır, şəxsi məlumatlarınıza '
            '(ad, istifadəçi adı və s.) bənzər olmamalı, tamamilə rəqəmlərdən '
            'ibarət olmamalı və geniş yayılmış şifrələrdən biri olmamalıdır.'
        )
        self.fields['new_password2'].label = 'Yeni şifrə (təkrar)'
        self.fields['new_password2'].widget.attrs.update({'class': FIELD_CLASS})
        self.fields['new_password2'].help_text = 'Təsdiq üçün eyni şifrəni yenidən daxil edin.'


class ChangePasswordForm(DjangoPasswordChangeForm):
    """Self-service password change (apps/cms/views/profile.py's
    ChangePasswordView) — same USE_I18N=False reasoning as
    PasswordResetForm/SetPasswordForm above, plus the same help text
    SetPasswordForm already shows so both password-setting screens in
    the CMS explain the requirement identically."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['old_password'].label = 'Cari şifrə'
        self.fields['old_password'].widget.attrs.update({'class': FIELD_CLASS})
        self.fields['new_password1'].label = 'Yeni şifrə'
        self.fields['new_password1'].widget.attrs.update({'class': FIELD_CLASS})
        self.fields['new_password1'].help_text = (
            'Şifrə ən azı 10 simvoldan ibarət olmalıdır, şəxsi məlumatlarınıza '
            '(ad, istifadəçi adı və s.) bənzər olmamalı, tamamilə rəqəmlərdən '
            'ibarət olmamalı və geniş yayılmış şifrələrdən biri olmamalıdır.'
        )
        self.fields['new_password2'].label = 'Yeni şifrə (təkrar)'
        self.fields['new_password2'].widget.attrs.update({'class': FIELD_CLASS})
        self.fields['new_password2'].help_text = 'Təsdiq üçün eyni şifrəni yenidən daxil edin.'


class UserForm(forms.ModelForm):
    """CMS user management (apps/cms/views/user.py). Password is never a
    field here — accounts always get a password via the email reset flow
    (apps/accounts/services.py), never typed in by an administrator
    (CLAUDE.md ch.12: "Never display passwords. Never email passwords.")."""

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'phone', 'role', 'is_active']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'last_name': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'username': forms.TextInput(attrs={'class': FIELD_CLASS}),
            'email': forms.EmailInput(attrs={'class': FIELD_CLASS}),
            'phone': forms.TextInput(attrs={'class': FIELD_CLASS, 'placeholder': '+994 XX XXX XX XX'}),
            'role': forms.Select(attrs={'class': FIELD_CLASS}),
        }

    def clean_email(self):
        email = self.cleaned_data['email'].strip()
        if not email:
            raise forms.ValidationError('E-poçt ünvanı mütləqdir.')
        conflict = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            conflict = conflict.exclude(pk=self.instance.pk)
        if conflict.exists():
            raise forms.ValidationError('Bu e-poçt ünvanı artıq istifadə olunur.')
        return email
