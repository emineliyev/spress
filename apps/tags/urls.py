from django.urls import path

from . import views

app_name = 'tags'

urlpatterns = [
    path('<slug:slug>/', views.TagDetailView.as_view(), name='detail'),
]
