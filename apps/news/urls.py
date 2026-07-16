from django.urls import path

from . import views

app_name = 'news'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('search/', views.NewsSearchView.as_view(), name='search'),
    path('news/<slug:slug>/', views.NewsDetailView.as_view(), name='detail'),
]
