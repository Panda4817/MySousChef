from django.urls import path
from django.contrib.auth import views as auth_views
from django.conf import settings

from . import views


# All url routes for views
urlpatterns = [
    path("", views.index, name="index"),
]