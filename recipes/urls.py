from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings

from . import views


# All url routes for views
urlpatterns = [
    path("dashboard", views.dashboard, name="dashboard"),
    path("search_ingredients", views.search_ingredients, name="search_ingredients"),
    path("pantry", views.pantry, name="pantry"),
]