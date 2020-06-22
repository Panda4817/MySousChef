from django.db import models
from django.contrib.auth.models import User
from datetime import datetime
from django.utils import timezone

# Create your models here.
# Pantry items
class Pantry(models.Model):
    name = models.CharField(max_length=64)
    api_id = models.PositiveIntegerField()
    aisle = models.CharField(max_length=64)
    image = models.CharField(max_length=64)

    def __str__(self):
        return f"{self.name} - {self.api_id} - {self.aisle}"

# User to ingredient mapping
class UserToPantry(models.Model):
    TEXT_CHOICES = [
        ('Use By', 'Use By'),
        ('Best Before', 'Best Before')
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pantry_item = models.ForeignKey(Pantry, on_delete=models.CASCADE)
    added = models.DateTimeField(default=timezone.now)
    opened = models.DateTimeField(null=True, blank=True)
    frozen = models.DateTimeField(null=True, blank=True)
    usebefore = models.DateTimeField(null=True, blank=True)
    usebefore_text = models.CharField(max_length=64, null=True, choices=TEXT_CHOICES)
    use_within = models.CharField(max_length=64, blank=True)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.CheckConstraint(check=models.Q(
                quantity__gt=0), name='quantity_gt_0')
        ]
# Store recipes from search results
class Recipes(models.Model):
    api_id = models.PositiveIntegerField()
    title = models.CharField(max_length=200)
    image = models.URLField()
    serves = models.PositiveIntegerField()
    time = models.PositiveIntegerField()
    source_url = models.URLField()
    credit = models.CharField(max_length=200, null=True)
    health_score = models.DecimalField(max_digits=4, decimal_places=2)
    popularity = models.PositiveIntegerField()
    wine_pairing = models.TextField(blank=True)

    def __str__(self):
        return f"{self.api_id} - {self.title}"
# Store ingredients for recipes
class RecipeIngredients(models.Model):
    recipe_id = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=7, decimal_places=3)
    unit = models.CharField(max_length=64)
    meta = models.CharField(max_length=200, blank=True)
# Store instructions for recipes
class RecipeInstructions(models.Model):
    recipe_id = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    step = models.PositiveIntegerField()
    description = models.TextField()
# Map user to recipe if a recipe is 'liked'
class UserToRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    added = models.DateTimeField(default=timezone.now)
# Map items added to shopping list to user
class ShoppingList(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
# Model of storing own recipes
class MyRecipe(models.Model):
    IMAGE_CHOICES = [
        ('salad.png', 'salad.png'),
        ('pizza.png', 'pizza.png'),
        ('pancake.png', 'pancake.png'),
        ('cake2.png', 'cake2.png'),
        ('hamburger.png', 'hamburger.png'),
        ('rib.png', 'rib.png'),
    ]
    title = models.CharField(max_length=200)
    serves = models.PositiveIntegerField()
    time = models.PositiveIntegerField()
    wine_pairing = models.TextField(blank=True)
    image = models.CharField(max_length=64, default="salad.png", choices=IMAGE_CHOICES)
# Map ingredients to myrecipes
class MyRecipeIngredients(models.Model):
    recipe_id = models.ForeignKey(MyRecipe, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=7, decimal_places=3)
    unit = models.CharField(max_length=64, blank=True)
    meta = models.CharField(max_length=200, blank=True)
# Map instructions to myrecipes
class MyRecipeInstructions(models.Model):
    recipe_id = models.ForeignKey(MyRecipe, on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    step = models.TextField()
# Map user to own recipes
class UserToMyRecipe(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    recipe_id = models.ForeignKey(MyRecipe, on_delete=models.CASCADE)

