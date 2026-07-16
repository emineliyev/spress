from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import PasswordResetForm, SetPasswordForm

app_name = 'accounts'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path(
        'sifre-sifirla/',
        auth_views.PasswordResetView.as_view(
            form_class=PasswordResetForm,
            template_name='accounts/password_reset_form.html',
            email_template_name='accounts/password_reset_email.html',
            subject_template_name='accounts/password_reset_subject.txt',
            success_url=reverse_lazy('accounts:password_reset_done'),
        ),
        name='password_reset',
    ),
    path(
        'sifre-sifirla/gonderildi/',
        auth_views.PasswordResetDoneView.as_view(template_name='accounts/password_reset_done.html'),
        name='password_reset_done',
    ),
    path(
        'sifre-sifirla/<uidb64>/<token>/',
        auth_views.PasswordResetConfirmView.as_view(
            form_class=SetPasswordForm,
            template_name='accounts/password_reset_confirm.html',
            success_url=reverse_lazy('accounts:password_reset_complete'),
        ),
        name='password_reset_confirm',
    ),
    path(
        'sifre-sifirla/tamamlandi/',
        auth_views.PasswordResetCompleteView.as_view(template_name='accounts/password_reset_complete.html'),
        name='password_reset_complete',
    ),
]
