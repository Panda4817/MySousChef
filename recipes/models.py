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

class RecipeIngredients(models.Model):
    recipe_id = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=7, decimal_places=3)
    unit = models.CharField(max_length=64)
    meta = models.CharField(max_length=200, blank=True)

class RecipeInstructions(models.Model):
    recipe_id = models.ForeignKey(Recipes, on_delete=models.CASCADE)
    step = models.PositiveIntegerField()
    description = models.TextField()

