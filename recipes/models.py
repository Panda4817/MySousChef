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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pantry_item = models.ForeignKey(Pantry, on_delete=models.CASCADE)
    added = models.DateTimeField(default=timezone.now)
    opened = models.DateTimeField(default=timezone.now)
    usebefore = models.DateTimeField(default=timezone.now)
    bestbefore = models.DateTimeField(default=timezone.now)
    use_within = models.CharField(max_length=64, blank=True)

