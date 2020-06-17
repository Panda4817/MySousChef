from django.contrib import admin
from .models import *

# Register your models here.
class ProfileAdmin(admin.ModelAdmin):
    model = Profile
    list_display = ['pk', 'user', 'email_confirmed', 'accept_policies']


admin.site.register(Profile, ProfileAdmin)