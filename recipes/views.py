from django.shortcuts import render
from django.contrib.auth.signals import user_logged_out, user_logged_in
from .signals import show_login_message, show_logout_message
from django.contrib import messages
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url="login")
def dashboard(request):
    return render(request, 'recipes/dashboard.html')