from django.contrib import admin
from .models import *
from django.contrib import messages
from django.utils.translation import ngettext

# Register your models here.

class UserToPantryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'pantry_item', 'added', 'opened', 'frozen', 'usebefore_text', 'usebefore', 'use_within', 'quantity']
    actions = ['make_optional_null']
    
    
    # Custom action to change dates to null
    def make_optional_null(self, request, queryset):
        updated = queryset.update(opened=None,frozen=None, usebefore=None)
        self.message_user(request, ngettext(
            '%d opened, frozen and usebefore are now null',
            '%d dates are now null',
            updated,
        ) % updated, messages.SUCCESS)
    make_optional_null.short_description = "Change dates to null"



class PantryAdmin(admin.ModelAdmin):
    model = Pantry
    list_display = ['pk', 'name', 'api_id', 'aisle', 'image']

class RecipesAdmin(admin.ModelAdmin):
    model = Recipes
    list_display = ['pk', 'api_id', 'title', 'image', 'serves', 'time', 'source_url', 'credit', 'health_score', 'popularity', 'wine_pairing']

class RecipeIngredientsAdmin(admin.ModelAdmin):
    model = RecipeIngredients
    list_display = ['pk', 'recipe_id', 'name', 'amount', 'unit', 'meta']

class RecipeInstructionsAdmin(admin.ModelAdmin):
    model = RecipeInstructions
    list_display = ['pk', 'recipe_id', 'step', 'description']

class ShoppingListAdmin(admin.ModelAdmin):
    model = ShoppingList
    list_display = ['pk', 'name']

class MyRecipeAdmin(admin.ModelAdmin):
    model = MyRecipe
    list_display = ['pk', 'title', 'image', 'serves', 'time', 'wine_pairing']

class MyRecipeIngredientsAdmin(admin.ModelAdmin):
    model = MyRecipeIngredients
    list_display = ['pk', 'recipe_id', 'name', 'amount', 'unit', 'meta']

class MyRecipeInstructionsAdmin(admin.ModelAdmin):
    model = MyRecipeInstructions
    list_display = ['pk', 'recipe_id', 'number', 'step']


admin.site.register(Pantry, PantryAdmin)
admin.site.register(UserToPantry, UserToPantryAdmin)
admin.site.register(Recipes, RecipesAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(RecipeInstructions, RecipeInstructionsAdmin)
admin.site.register(ShoppingList, ShoppingListAdmin)
admin.site.register(MyRecipe, MyRecipeAdmin)
admin.site.register(MyRecipeIngredients, MyRecipeIngredientsAdmin)
admin.site.register(MyRecipeInstructions, MyRecipeInstructionsAdmin)
