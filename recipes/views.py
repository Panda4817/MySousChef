from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.urls import reverse_lazy
from django.contrib.auth.signals import user_logged_out, user_logged_in
from .signals import show_login_message, show_logout_message
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import RecipeClient, check_intolerance, addToPantry
from .models import *
from datetime import datetime
from django.conf import settings
from dateutil import parser
import pytz

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
        
        if len(ingredient_list) > 0:
            data = {
                'json_list': ingredient_list,
                'input_correct': input_correct
            }    
            response = JsonResponse(data)
            response.status_code = 200
        else:
            data = {
                'message': 'Pantry item not found',
            }
            response = JsonResponse(data)
            response.status_code = 404

        return response 
    return redirect('recipes:pantry')

@login_required(login_url=reverse_lazy("accounts:login"))
def pantry(request):
    user = User.objects.get(pk=request.user.id) 
    if request.method == 'POST':
        ingredientName = request.POST['ingredientName']
        print(ingredientName)
        intolerance = request.POST.getlist('intolerance[]')
        print(intolerance)
        
        # Check what the intolerance selection is
        boolintolerance = check_intolerance(intolerance)
        if boolintolerance == False:
            intolerance = None
        
        data = addToPantry(ingredientName, user, intolerance)
        if 'ERROR' in data['message']:
            response_data = {
                'message': data['message']
            }
            response = JsonResponse(response_data)
            response.status_code = 404
            return response
        else:
            added = (data['item'].added).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
            new_aisle = data['item'].pantry_item.aisle
            if ';' in data['item'].pantry_item.aisle:
                aisle = data['item'].pantry_item.aisle
                new_aisle = aisle.replace(';', ', ')
            response_data = {
                'message': data['message'],
                'id': data['item'].id,
                'name': data['item'].pantry_item.name,
                'aisle': new_aisle,
                'image': data['item'].pantry_item.image,
                'added': added,
                'quantity': data['item'].quantity,
            } 
            response = JsonResponse(response_data)
            response.status_code = 200
            return response   
        return redirect('recipes:pantry')
    
    items = list(UserToPantry.objects.filter(user=user))
    context = {
        'items': items,
    }

    return render(request, 'recipes/pantry.html', context)

@login_required(login_url=reverse_lazy("accounts:login"))
def change_qty(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        new_qty =  request.POST['new_qty']

        if int(new_qty) < 1:
            data = {
                'id': usertopantry_id,
                'message': "Number must ne 1 or more",
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response

        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.quantity = new_qty
        item.save()

        response = {
            'id': usertopantry_id,
            'new_qty': new_qty
        }
        return JsonResponse(response)
    return redirect('recipes:pantry')


@login_required(login_url=reverse_lazy("accounts:login"))
def change_useby(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        usetext =  request.POST['datetext']
        usedate = request.POST['new_date']

        
        date = (parser.isoparse(usedate))
        print(date)
        inputdate = datetime.date(date)
        print(inputdate)
        today = timezone.now()
        todaydate = datetime.date(today)
        print(todaydate)
        if inputdate < todaydate:
            data = {
                'id': usertopantry_id,
                'message': "Date cannot be in the past",
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response

        
        
        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.usebefore_text = usetext
        item.usebefore = date
        item.save()

        data = {
            'id': usertopantry_id,
            'datetext': usetext,
            'date': usedate,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:pantry')

@login_required(login_url=reverse_lazy("accounts:login"))
def change_open(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        opendate = request.POST['new_date']

        
        date = (parser.isoparse(opendate))
        print(date)
        inputdate = datetime.date(date)
        print(inputdate)
        today = timezone.now()
        todaydate = datetime.date(today)
        print(todaydate)
        if inputdate < todaydate:
            data = {
                'id': usertopantry_id,
                'message': "Date cannot be in the past",
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        print(date)
        
        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.opened = date
        item.save()

        data = {
            'id': usertopantry_id,
            'date': opendate,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:pantry')

@login_required(login_url=reverse_lazy("accounts:login"))
def change_frozen(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        frozendate = request.POST['new_date']

        
        date = (parser.isoparse(frozendate))
        print(date)
        inputdate = datetime.date(date)
        print(inputdate)
        today = timezone.now()
        todaydate = datetime.date(today)
        print(todaydate)
        if inputdate < todaydate:
            data = {
                'id': usertopantry_id,
                'message': "Date cannot be in the past",
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        print(date)
        
        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.frozen = date
        item.save()

        data = {
            'id': usertopantry_id,
            'date': frozendate,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:pantry')

@login_required(login_url=reverse_lazy("accounts:login"))
def change_use_within(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        uw = request.POST['uw']

        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.use_within = uw
        item.save()

        response = {
            'id': usertopantry_id,
            'uw': item.use_within,
        }
        return JsonResponse(response) 
    return redirect('recipes:pantry')

@login_required(login_url=reverse_lazy("accounts:login"))
def delete_pantry_item(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']

        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.delete()

        response = {
            'id': usertopantry_id,
        }
        return JsonResponse(response) 
    return redirect('recipes:pantry')