"""Shared form-validation building blocks (CLAUDE.md ch.4 core/ "Reusable services").

`USE_I18N = False` (CLAUDE.md ch.3 "Language") means Django's own
built-in field error messages ("This field is required.", "Enter a
valid URL.") render as literal English with no translation catalog to
fall back on. Every form with a required/validated field needs an
explicit Azerbaijani override — merge these into a field's
`error_messages` kwarg (plain `forms.Form`) or a `ModelForm.Meta.error_messages`
entry, instead of redefining the same strings per form.
"""

REQUIRED_MESSAGE = {'required': 'Bu sahənin doldurulması mütləqdir.'}
MAX_LENGTH_MESSAGE = {'max_length': 'Bu sahə ən çoxu %(limit_value)d simvol ola bilər.'}
INVALID_URL_MESSAGE = {'invalid': 'Düzgün URL daxil edin (məsələn, https://misal.az).'}
INVALID_EMAIL_MESSAGE = {'invalid': 'Düzgün e-poçt ünvanı daxil edin.'}
MIN_VALUE_MESSAGE = {'min_value': 'Bu sahə ən azı %(limit_value)d ola bilər.'}
MAX_VALUE_MESSAGE = {'max_value': 'Bu sahə ən çoxu %(limit_value)d ola bilər.'}
