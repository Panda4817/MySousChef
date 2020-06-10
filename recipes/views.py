from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.signals import user_logged_out, user_logged_in
from .signals import show_login_message, show_logout_message
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import RecipeClient, check_intolerance, addToPantry
from .models import *

# Configure clients
api_client = RecipeClient()

# Create your views here.
@login_required(login_url=reverse_lazy("accounts:login"))
def dashboard(request):
    return render(request, 'recipes/dashboard.html')

@login_required(login_url=reverse_lazy("accounts:login"))
def search_ingredients(request):
    if request.method == 'POST':
        # Get data from form
        searchInput = request.POST['search_input']
        intolerance = request.POST.getlist('intolerance[]')
        print(intolerance)
        # Check what the intolerance selection is
        boolintolerance = check_intolerance(intolerance)
        if boolintolerance == False:
            intolerance = None
        
        results = api_client.get_ingredients(searchInput, intolerance)
        print(results)
        # Prepare data to send back to ajax
        ingredient_list = []
        input_correct = False
        for result in results:
            ingredient_list.append(result['name'])
            if searchInput == result['name']:
                input_correct = True
            
        response = {
            'json_list': ingredient_list,
            'input_correct': input_correct
        }
        
        return JsonResponse(response) 
    return redirect('recipes:pantry')

@login_required(login_url=reverse_lazy("accounts:login"))
def pantry(request):
    user = User.objects.get(pk=request.user.id) 
    if request.method == 'POST':
        ingredientName = request.POST['search']
        print(ingredientName)
        intolerance = request.POST.getlist('intolerance[]')
        print(intolerance)
        
        # Check what the intolerance selection is
        boolintolerance = check_intolerance(intolerance)
        if boolintolerance == False:
            intolerance = None
        
        message = addToPantry(ingredientName, user, intolerance)

        if 'ERROR' in message:
            messages.error(request, message)
        else:
            messages.success(request, message)      
        return redirect('recipes:pantry')
    
    items = list(UserToPantry.objects.filter(user=user))
    context = {
        'items': items,
    }

    return render(request, 'recipes/pantry.html', context)
