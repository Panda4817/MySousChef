from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings

from . import views


# All url routes for views
urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("search_ingredients", views.search_ingredients, name="search_ingredients"),
    path("pantry", views.pantry, name="pantry"),
    path("change-qty-pantry", views.change_qty, name="change-qty-pantry"),
    path("change-useby-pantry", views.change_useby, name="change-useby-pantry"),
    path("change-open-pantry", views.change_open, name="change-open-pantry"),
    path("change-frozen-pantry", views.change_frozen, name="change-frozen-pantry"),
    path("change-uw-pantry", views.change_use_within, name="change-uw-pantry"),
    path("delete-pantry-item", views.delete_pantry_item, name="delete-pantry-item"),
]