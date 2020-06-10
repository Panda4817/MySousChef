from django.contrib import admin
from .models import *

# Register your models here.

class UserToPantryAdmin(admin.ModelAdmin):
    list_display = ['pk', 'user', 'pantry_item', 'added', 'opened', 'usebefore', 'bestbefore', 'use_within']

class PantryAdmin(admin.ModelAdmin):
    model = Pantry
    list_display = ['pk', 'name', 'api_id', 'aisle', 'image']

admin.site.register(Pantry, PantryAdmin)
admin.site.register(UserToPantry, UserToPantryAdmin)