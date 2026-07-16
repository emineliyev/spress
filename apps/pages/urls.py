from django.urls import path

from . import views

app_name = 'pages'

urlpatterns = [
    path('about/', views.AboutView.as_view(), name='about'),
    path('contacts/', views.ContactView.as_view(), name='contact'),
    # Generic catch-all for any other published static page (privacy-policy,
    # terms-of-use, ...). Must stay last so the explicit paths above win.
    path('<slug:slug>/', views.PageDetailView.as_view(), name='detail'),
]
