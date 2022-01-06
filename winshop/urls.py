from django.urls import path, include
from api import views as api_views

urlpatterns = [
    path('search_product/<str:keyword>/', api_views.search_product, name="search-product"),
]
