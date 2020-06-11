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

