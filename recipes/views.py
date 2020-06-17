from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.contrib.auth.signals import user_logged_out, user_logged_in
from .signals import show_login_message, show_logout_message
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import RecipeClient, check_list, addToPantry, prepare_simple_results, prepare_advance_results
from .models import *
from datetime import datetime
from django.conf import settings
from dateutil import parser
import pytz
import json

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
        boolintolerance = check_list(intolerance)
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
        boolintolerance = check_list(intolerance)
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

@login_required(login_url=reverse_lazy("accounts:login"))
def search_recipes(request):
    return render(request, 'recipes/search.html')

@login_required(login_url=reverse_lazy("accounts:login"))
def search_simple(request):
    if request.method =='POST':
        user = request.user.id
        pantry_items = list(UserToPantry.objects.filter(user=user))
        if len(pantry_items) == 0:
            data = {
                'message': "No items in MyPantry to search with. Add ingredients to MyPantry."
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response

        names = [] 
        for i in pantry_items:
            names.append(i.pantry_item.name)
        
        results = api_client.search_recipes_ingredients(names)
        
        if len(results) == 0:
            data = {
                'message': "No results. Add more items to MyPantry."
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        
        response = prepare_simple_results(results)
        return response
    return redirect('recipes:search_recipes')


@login_required(login_url=reverse_lazy("accounts:login"))
def search_advanced(request):
    if request.method =='POST':
        user = request.user.id
        query = request.POST['query']
        if not query:
            data = {
                'message': "Must enter query word/phrase for advanced search"
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        
        ingredients = request.POST['ingredients']
        names = []
        if ingredients == 'yes':
            pantry_items = list(UserToPantry.objects.filter(user=user))
            if len(pantry_items) == 0:
                data = {
                    'message': "No items in MyPantry to search with. Add ingredients to MyPantry."
                }
                response = JsonResponse(data)
                response.status_code = 400
                return response 
            for i in pantry_items:
                names.append(i.pantry_item.name)
        else:
            names = None
        
        intolerance = request.POST.getlist('intolerance[]')
        boolintolerance = check_list(intolerance)
        if boolintolerance == False:
            intolerance = None
        
        diet = request.POST['diet']
        if not diet or diet == '0':
            diet = None
        meal_type = request.POST['meal_type']
        if not meal_type or meal_type == '0':
            meal_type = None
        
        cuisine = request.POST.getlist('cuisine[]')
        boolcuisine = check_list(cuisine)
        if boolcuisine == False:
            cuisine = None
        
        sort = request.POST['sort']
        sort_direction = ''
        if sort == 'No Sort':
            sort = None
            sort_direction = None
        elif sort == 'time':
            sort_direction = 'asc'
        else:
            sort_direction = 'desc'
        
        results = api_client.search_recipes_complex(query, cuisine, diet, intolerance, names, meal_type, sort, sort_direction)
        response = prepare_advance_results(results)
        return response
    return redirect('recipes:search_recipes')

@login_required(login_url=reverse_lazy("accounts:login"))
def recipe(request, recipe_id):
    if request.method == 'POST':
        api_id = request.POST['api_id']
        try:
            recipe = Recipes.objects.get(api_id=recipe_id)
        except Recipes.DoesNotExist:
            data = {
                'message': "Error finding recipe, try later."
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        alreadyliked = list(UserToRecipe.objects.filter(user=request.user).filter(recipe_id=recipe))
        if len(alreadyliked) > 0:
            data = {
                'message': "Already liked!"
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        
        liked = UserToRecipe(user=request.user, recipe_id=recipe)
        liked.save()
        data = {
            'message': "Added"
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response

    try:
        recipe = Recipes.objects.get(api_id=recipe_id)
    except Recipes.DoesNotExist:
        messages.error(request, "Recipe does not exist")
        return redirect('recipes:search_recipes')
    ingredients = list(RecipeIngredients.objects.filter(recipe_id=recipe))
    steps = list(RecipeInstructions.objects.filter(recipe_id=recipe).order_by('step'))
    if steps == []:
        results = api_client.get_recipe_instructions(recipe_id)
        if results == []:
            messages.error(request, "Cannot retrieve instructions. Go to the source website.")
            return redirect('recipes:search_recipes')
        for i in results[0]['steps']:
            instruction = RecipeInstructions(
                recipe_id=recipe,
                step=i['number'],
                description=i['step'],
            )
            instruction.save()
    steps = list(RecipeInstructions.objects.filter(recipe_id=recipe).order_by('step'))
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
        'steps': steps
    }
    return render(request, 'recipes/recipe.html', context)

@login_required(login_url=reverse_lazy("accounts:login"))
def shopping_list(request):
    if request.method == 'POST':
        pantry_id = request.POST['pantry_id']
        pantryitem = UserToPantry.objects.get(pk=pantry_id)
        items = list(ShoppingList.objects.filter(user=request.user.id))
        for item in items:
            if item.name == pantryitem.pantry_item.name.title():
                data = {
                'id': pantry_id,
                'message': "Item already added to shopping list"
                }
                response = JsonResponse(data)
                response.status_code = 400
                return response
        itemsave = ShoppingList(user=request.user, name=pantryitem.pantry_item.name.title())
        itemsave.save()
        data = {
            'id': pantry_id
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response


    items = list(ShoppingList.objects.filter(user=request.user.id))
    context = {}
    if len(items) > 0:
        context.update({'items': items})
    return render(request, 'recipes/shopping_list.html', context)

@login_required(login_url=reverse_lazy("accounts:login"))
def add_list(request):
    if request.method == 'POST':
        name = request.POST['name']
        if not name:
            data = {
                'message': "Must enter name of item"
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        items = list(ShoppingList.objects.filter(user=request.user.id))
        for item in items:
            if name.title() == item.name:
                data = {
                'message': "Item already added to shopping list"
                }
                response = JsonResponse(data)
                response.status_code = 400
                return response
        item = ShoppingList(user=request.user, name=name.title())
        item.save()
        data = {
            'id': item.id,
            'name': item.name
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:shopping_list')

@login_required(login_url=reverse_lazy("accounts:login"))
def delete_list(request):
    if request.method == 'POST':
        names = request.POST.getlist('names[]')
        if len(names) == 0:
            data = {
                'message': "Must check items in the list to remove them."
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        items = list(ShoppingList.objects.filter(user=request.user.id))
        ids = []
        for item in items:
            if item.name in names:
                ids.append(item.id)
                itemtod = ShoppingList.objects.get(pk=item.id)
                itemtod.delete()
        response = JsonResponse({'ids': ids})
        response.status_code = 200
        return response
    return redirect('recipes:shopping_list')

@login_required(login_url=reverse_lazy("accounts:login"))
def myrecipe(request):
    return render(request, 'recipes/myrecipe.html')

