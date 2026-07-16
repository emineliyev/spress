from django.urls import path

from . import views

app_name = 'categories'

urlpatterns = [
    path('<slug:category_slug>/', views.CategoryDetailView.as_view(), name='category_detail'),
    path('<slug:category_slug>/<slug:subcategory_slug>/', views.CategoryDetailView.as_view(), name='subcategory_detail'),
]
