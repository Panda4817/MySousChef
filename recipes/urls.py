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
    path("search-recipes", views.search_recipes, name="search_recipes"),
    path("search-simple", views.search_simple, name="search_simple"),
    path("search-advanced", views.search_advanced, name="search_advanced"),
    path("recipe", views.myrecipe, name="myrecipe"),
    path("recipe/<int:recipe_id>", views.recipe, name="recipe"),
    path("myrecipe", views.myrecipe, name="myrecipe"),
    path("myrecipe/<int:recipe_id>", views.myrecipe_page, name="myrecipe_page"),
    path("shopping-list", views.shopping_list, name="shopping_list"),
    path("add-list", views.add_list, name="add_list"),
    path("delete-list", views.delete_list, name="delete_list"),
    path("extra-ingredient-info", views.extra_ingredient_info, name="extra_ingredient_info"),
    path("delete-liked", views.delete_liked, name="delete_liked"),
    path("delete-myrecipe", views.delete_myrecipe, name="delete_myrecipe"),
]