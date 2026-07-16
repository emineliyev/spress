from django.urls import path

from . import views

app_name = 'advertisements'

urlpatterns = [
    path('<int:pk>/', views.AdClickView.as_view(), name='click'),
]
