from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect, Http404
from django.urls import reverse_lazy
from django.contrib.auth.signals import user_logged_out, user_logged_in
from .signals import show_login_message, show_logout_message
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .utils import *
from .models import *
from datetime import datetime
from django.conf import settings
from dateutil import parser
import pytz
import json
from .forms import *
import pprint
from django.core.cache import cache

# Configure clients
api_client = RecipeClient()

# Create your views here.

# Dashboard
@login_required(login_url=reverse_lazy("accounts:login"))
def dashboard(request):
    # Get personalised data from database
    items = list(UserToPantry.objects.filter(user=request.user).exclude(frozen__isnull=False).order_by('usebefore')[:5])
    for item in items:
        if item.usebefore != None:
            item.usebefore = (item.usebefore).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    opens = list(UserToPantry.objects.filter(user=request.user).exclude(frozen__isnull=False).order_by('opened')[:5])
    for o in opens:
        if o.opened != None:
            o.opened = (o.opened).strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    shopping = list(ShoppingList.objects.filter(user=request.user)[:5])
    recipes = list(UserToRecipe.objects.filter(user=request.user).order_by('-added')[:5])
    data = {}
    pantry_items = list(UserToPantry.objects.filter(user=request.user))
    names = []
    results = []
    if len(pantry_items) == 0:
        data = {'message': "No items in MyPantry to search with. Add ingredients to MyPantry.", 'recipes': None}
    else:
        for i in pantry_items:
            names.append(i.pantry_item.name)
        results = api_client.search_recipes_ingredients(names)
    if settings.DEBUG == True:
        print(results)
    if results != None:
        if results == [] or len(results) == 0:
            data = {
                'message': "No results. Add more items to MyPantry.",
                'recipes': None
            }
        else:
            data = prepare_simple_results(results)
    else:
        data = {
                'message': "API ERROR. Check back tomorrow. Sorry :("
            }
    context = {
        'items': items,
        'names': shopping,
        'recipes': recipes,
        'opens': opens,
        'data': data
    }
    return render(request, 'recipes/dashboard.html', context)

# Searching ingredients
@login_required(login_url=reverse_lazy("accounts:login"))
def search_ingredients(request):
    if request.method == 'POST':
        # Get data from form
        searchInput = request.POST['search_input']
        intolerance = request.POST.getlist('intolerance[]')
        if settings.DEBUG == 'True':
            print(intolerance)
        # Check what the intolerance selection is
        boolintolerance = check_list(intolerance)
        if boolintolerance == False:
            intolerance = None
        
        results = api_client.get_ingredients(searchInput, intolerance)
        if settings.DEBUG == 'True':
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
        # Get data from form
        ingredientName = request.POST['ingredientName']
        if settings.DEBUG == 'True':
            print(ingredientName)
        intolerance = request.POST.getlist('intolerance[]')
        if settings.DEBUG == 'True':
            print(intolerance)
        
        # Check what the intolerance selection is
        boolintolerance = check_list(intolerance)
        if boolintolerance == False:
            intolerance = None
        
        # Add item to pantry table in database
        data = addToPantry(ingredientName, user, intolerance)
        cache.clear()
        if 'ERROR' in data['message']:
            response_data = {
                'message': data['message']
            }
            response = JsonResponse(response_data)
            response.status_code = 404
            return response
        else:
            # Prepare data to send back to AJAX call
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
    
    # If request is GET
    items = list(UserToPantry.objects.filter(user=user))
    context = {
        'items': items,
    }

    return render(request, 'recipes/pantry.html', context)

# view for url to change quanity of pantry item
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
        cache.clear()
        response = {
            'id': usertopantry_id,
            'new_qty': new_qty
        }
        return JsonResponse(response)
    return redirect('recipes:pantry')

# view for url for changing use-by/best-before date
@login_required(login_url=reverse_lazy("accounts:login"))
def change_useby(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        usetext =  request.POST['datetext']
        usedate = request.POST['new_date']

        
        date = (parser.isoparse(usedate))
        if settings.DEBUG == 'True':
            print(date)
        inputdate = datetime.date(date)
        if settings.DEBUG == 'True':
            print(inputdate)
        today = timezone.now()
        todaydate = datetime.date(today)
        if settings.DEBUG == 'True':
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
        cache.clear()
        data = {
            'id': usertopantry_id,
            'datetext': usetext,
            'date': usedate,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:pantry')

# view for url for changing when opened date
@login_required(login_url=reverse_lazy("accounts:login"))
def change_open(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        opendate = request.POST['new_date']

        
        date = (parser.isoparse(opendate))
        if settings.DEBUG == 'True':
            print(date)
        inputdate = datetime.date(date)
        if settings.DEBUG == 'True':
            print(inputdate)
        today = timezone.now()
        todaydate = datetime.date(today)
        if settings.DEBUG == 'True':
            print(todaydate)
        if inputdate < todaydate:
            data = {
                'id': usertopantry_id,
                'message': "Date cannot be in the past",
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        if settings.DEBUG == 'True':
            print(date)
        
        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.opened = date
        item.save()
        cache.clear()
        data = {
            'id': usertopantry_id,
            'date': opendate,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:pantry')

# view for url for changing when frozen date
@login_required(login_url=reverse_lazy("accounts:login"))
def change_frozen(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        frozendate = request.POST['new_date']

        
        date = (parser.isoparse(frozendate))
        if settings.DEBUG == 'True':
            print(date)
        inputdate = datetime.date(date)
        if settings.DEBUG == 'True':
            print(inputdate)
        today = timezone.now()
        todaydate = datetime.date(today)
        if settings.DEBUG == 'True':
            print(todaydate)
        if inputdate < todaydate:
            data = {
                'id': usertopantry_id,
                'message': "Date cannot be in the past",
            }
            response = JsonResponse(data)
            response.status_code = 400
            return response
        if settings.DEBUG == 'True':
            print(date)
        
        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.frozen = date
        item.save()
        cache.clear()
        data = {
            'id': usertopantry_id,
            'date': frozendate,
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:pantry')

# view for url for changing use within information
@login_required(login_url=reverse_lazy("accounts:login"))
def change_use_within(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']
        uw = request.POST['uw']

        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.use_within = uw
        item.save()
        cache.clear()
        response = {
            'id': usertopantry_id,
            'uw': item.use_within,
        }
        return JsonResponse(response) 
    return redirect('recipes:pantry')

# view for url for deleting pantry item
@login_required(login_url=reverse_lazy("accounts:login"))
def delete_pantry_item(request):
    if request.method == 'POST':
        usertopantry_id = request.POST['usertopantry_id']

        item = UserToPantry.objects.get(pk=usertopantry_id)
        item.delete()
        cache.clear()
        response = {
            'id': usertopantry_id,
        }
        return JsonResponse(response) 
    return redirect('recipes:pantry')

# view for displaying search recipes page
@login_required(login_url=reverse_lazy("accounts:login"))
def search_recipes(request):
    return render(request, 'recipes/search.html')

# view for url for making a simple search request using just ingredients in pantry
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
        results = []
        results = api_client.search_recipes_ingredients(names)
        if results != None:
            if results == [] or len(results) == 0:
                data = {
                    'message': "No results. Add more items to MyPantry."
                }
                response = JsonResponse(data)
                response.status_code = 400
                return response
        else:
            data = {
                    'message': "API ERROR. Check back tomorrow. Sorry :("
                }
            response = JsonResponse(data)
            response.status_code = 500
            return response  
        
        data = prepare_simple_results(results)
        cache.clear()
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:search_recipes')

# view for url for searching recipes using complex method
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
        cache.clear()
        return response
    return redirect('recipes:search_recipes')

# View to add recipes to the liked table and view recipe page from a search
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
        cache.clear()
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
            cache.clear()
    steps = list(RecipeInstructions.objects.filter(recipe_id=recipe).order_by('step'))
    others = api_client.get_recipes_similar(recipe_id)
    similar = []
    if others != None:
        similar = get_similar_recipes(others)
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
        'steps': steps,
        'similar': similar
    }
    return render(request, 'recipes/recipe.html', context)

# view shopping list page and add items to list from virtual pantry
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
        cache.clear()
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

# view to add to shopping list
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
        cache.clear()
        data = {
            'id': item.id,
            'name': item.name
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:shopping_list')

# View to delete item on list
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
        cache.clear()
        response = JsonResponse({'ids': ids})
        response.status_code = 200
        return response
    return redirect('recipes:shopping_list')

# View myrecipes page and save add to myrecipes form
@login_required(login_url=reverse_lazy("accounts:login"))
def myrecipe(request):
    recipeform = MyRecipeInfoForm()
    ingredientsformset = IngredientsFormset(prefix="ingform", queryset=MyRecipeIngredients.objects.none())
    instructionsformset = InstructionsFormset(prefix="instrform", queryset=MyRecipeInstructions.objects.none())
    likedrecipes = list(UserToRecipe.objects.filter(user=request.user))
    myrecipes = list(UserToMyRecipe.objects.filter(user=request.user))
    
    if request.method == 'POST':
        recipeform = MyRecipeInfoForm(request.POST)
        ingredientsformset = IngredientsFormset(request.POST, prefix="ingform")
        instructionsformset = InstructionsFormset(request.POST, prefix="instrform")
        if recipeform.is_valid() and ingredientsformset.is_valid() and instructionsformset.is_valid():
            recipe = recipeform.save()
            for form in ingredientsformset:
                ingredient = form.save(commit=False)
                ingredient.recipe_id = recipe
                ingredient.save()
            for form in instructionsformset:
                instruction = form.save(commit=False)
                instruction.recipe_id = recipe
                instruction.save()
            usertomyrecipe = UserToMyRecipe(user=request.user, recipe_id=recipe)
            usertomyrecipe.save()
            cache.clear()
            messages.success(request, "Recipe added!")
            return redirect('recipes:myrecipe')
        
    context = {
        'recipeform': recipeform,
        'ingformset': ingredientsformset,
        'instrformset': instructionsformset,
        'recipes': likedrecipes,
        'myrecipes': myrecipes
    }
    return render(request, 'recipes/myrecipe.html', context)

# View to see the recipe page for own recipes created
@login_required(login_url=reverse_lazy("accounts:login"))
def myrecipe_page(request, recipe_id):
    try:
        recipe = MyRecipe.objects.get(pk=recipe_id)
    except MyRecipe.DoesNotExist:
        messages.error(request, "Recipe does not exist")
        return redirect('recipes:myrecipe')
    ingredients = list(MyRecipeIngredients.objects.filter(recipe_id=recipe))
    steps = list(MyRecipeInstructions.objects.filter(recipe_id=recipe).order_by('number'))
    context = {
        'recipe': recipe,
        'ingredients': ingredients,
        'steps': steps
    }
    return render(request, 'recipes/myrecipe_page.html', context)

# View to make substitution and convert units requests
@login_required(login_url=reverse_lazy("accounts:login"))
def extra_ingredient_info(request):
    if request.method == 'POST':
        name = request.POST['name']
        unit = request.POST['unit']
        amount = request.POST['amount']
        ingid = request.POST['id']
        subs = ""
        imperial = ""
        if unit == "None":
            imperial = "No unit conversion available"
        else:
            imperial = convertunit(name, unit, amount)
        results = api_client.get_substitute_name(name)
        if results != None:
            if results['status'] == "failure":
                subs = "No substitutes found"
            else:
                subs = ', '.join(results['substitutes'])  
        else:
            subs = "API ERROR. Check tomorrow. Sorry :("
        
        if imperial == None:
            imperial = "No unit conversion available"
        data = {
            'subs': subs,
            'imperial': imperial,
            'id': ingid
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:myrecipe')

# view to allow deleting liked recipes
@login_required(login_url=reverse_lazy("accounts:login"))
def delete_liked(request):
    if request.method == 'POST':
        recipe_id = request.POST['id']
        recipe  = Recipes.objects.get(pk=recipe_id)
        items = list(UserToRecipe.objects.filter(user=request.user).filter(recipe_id=recipe))
        if len(items) == 1:
            item = UserToRecipe.objects.get(pk=items[0].id)
            item.delete()
            cache.clear()
        else:
            if settings.DEBUG == 'True':
                print("error")
        data = {
            'id': recipe_id
        }
        response = JsonResponse(data)
        response.status_code = 200
        return response
    return redirect('recipes:myrecipe')

# view to delete a recipe created by user
@login_required(login_url=reverse_lazy("accounts:login"))
def delete_myrecipe(request):
    recipe_id = request.POST['recipe_id']
    recipe  = MyRecipe.objects.get(pk=recipe_id)
    items = list(UserToMyRecipe.objects.filter(user=request.user).filter(recipe_id=recipe))
    if len(items) == 1:
        item = UserToMyRecipe.objects.get(pk=items[0].id)
        item.delete()
        cache.clear()
    else:
        if settings.DEBUG == 'True':
            print("error")
    messages.info(request, "Recipe deleted")
    return redirect('recipes:myrecipe')