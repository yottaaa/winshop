from django.urls import path, include
from api import views as api_views
from core import views as core_views

urlpatterns = [
    path('', core_views.index, name='landing-page'),
    path('search_product/<str:keyword>/', api_views.search_product, name="search-product"),
]
