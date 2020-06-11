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

admin.site.register(Pantry, PantryAdmin)
admin.site.register(UserToPantry, UserToPantryAdmin)