import os
from django.shortcuts import render
from django.conf import settings
import requests
from urllib.parse import quote, urlencode
from django.db import models
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from .models import *
import pprint

# Get api key from environment variables
api_key = os.getenv('API_KEY')

# Created my own client class to make api requests
class RecipeClient(object):

    def __init__(self):
        self.host = "api.spoonacular.com"
        self.key = api_key
        self.session = requests.session()

    # add filter and create url for api request
    def _get(self, path, filters):
        filters.update({'apiKey': self.key})
        filter_str = urlencode(filters)
        try:
            if settings.DEBUG == 'True':
                print('https://{}{}?{}'.format(self.host, path, filter_str))
            response = self.session.get('https://{}{}?{}'.format(self.host, path, filter_str))
            response.raise_for_status()
        except requests.RequestException:
            return None

        try:
            return response.json()
        except (KeyError, TypeError, ValueError):
            return None

    # Search recipes using ingredients
    def search_recipes_ingredients(self, ingredients):
        filters = {'ingredients': ','.join(ingredients), 'number': 5, 'limitLicense': 'false', 'ranking': 2, 'ignorePantry': 'false'}
        response = self._get('/recipes/findByIngredients', filters)
        return response
    
    # Search recipe by id to get more info
    def get_recipe_info(self, recipe_id):
        filters = {'includeNutrition': 'false'}
        response = self._get('/recipes/{}/information'.format(recipe_id), filters)
        return response
    
    # Search recipes using id in bulk
    def get_recipe_bulk(self, recipe_id_list):
        filters = {
            'ids': ','.join(recipe_id_list),
            'includeNutrition': 'false',
        }
        response = self._get('/recipes/informationBulk', filters)
        return response
    
    # Search similar recipes to id given
    def get_recipes_similar(self, recipe_id):
        filters = {'number': 2}
        response = self._get('/recipes/{}/similar'.format(recipe_id), filters)
        return response
    
    # Search recipes using query word/phrase, cuisine type etc
    def search_recipes_complex(self, query, cuisine, diet, intolerances, includeIngredients, meal_type, sort, sortDirection):
        filters = {}
        filters.update({
            'query': query,
        })
        if cuisine is not None:
            filters.update({'cuisine': ','.join(cuisine)})
        if diet is not None:
            filters.update({'diet': diet})
        if intolerances is not None:
            filters.update({'intolerances': ','.join(intolerances)})
        if includeIngredients is not None:
            filters.update({'includeIngredients': ','.join(includeIngredients)})
        if meal_type is not None:
            filters.update({'type': meal_type})
        
        if includeIngredients is not None:
            filters.update({
                'instructionsRequired': False,
                'fillIngredients': True,
                'addRecipeInformation': True,
                'addRecipeNutrition': False,
                'ignorePantry': False,
            })
        else:
            filters.update({
                'instructionsRequired': False,
                'fillIngredients': True,
                'addRecipeInformation': True,
                'addRecipeNutrition': False,
                'ignorePantry': True,
            })
        if sort is not None:
            filters.update({
                'sort': sort,
                'sortDirection': sortDirection,
            })
        filters.update({
            'number': 5,
            'limitLicense': 'false'
        })
        response = self._get('/recipes/complexSearch', filters)
        return response
    
    # Convert units of ingredients (using to convert from metric to imperial if suitable)
    def convert(self, ingredientName, sourceAmount, sourceUnit, targetUnit):
        filters = {
            'ingredientName': ingredientName, 
            'sourceAmount': sourceAmount,
            'sourceUnit': sourceUnit,
            'targetUnit': targetUnit,
        }
        response = self._get('/recipes/convert', filters)
        return response
    
    # Search ingredients for virtual pantry
    def get_ingredients(self, query, intolerances):
        filters = {'query': query, 'metaInformation': 'true'}
        if intolerances is not None:
            filters.update({'intolerances': ','.join(intolerances)})
        response = self._get('/food/ingredients/autocomplete', filters)
        return response
    
    # Get substitute for an ingredient
    def get_substitute_name(self, ingredientName):
        filters = {'ingredientName': ingredientName}
        response = self._get('/food/ingredients/substitutes', filters)
        return response
    
    # Get recipe instructions to display them  for a given id
    def get_recipe_instructions(self, recipe_id):
        filters = {'stepBreakdown': True}
        response = self._get('/recipes/{}/analyzedInstructions'.format(recipe_id), filters)
        return response


# Check if a multiple select field data is filled out or not
def check_list(list_name):
    check_list = True
    if len(list_name) != 0:
        for i in list_name:
            if i == "0":
                check_list = False
    else:
        check_list = False
    return check_list

# Adds item to pantry and returns pantry item data
def addToPantry(ingredientName, user, intolerance):
    pantry = list(Pantry.objects.all())
    userpantry = list(UserToPantry.objects.filter(user=user))
    already_in = False
    user_has = False
    message = ""
    data = {}
    for p in pantry:
        if ingredientName == p.name:
            already_in = True
            for u in userpantry:
                if u.pantry_item.api_id == p.api_id:
                    user_has = True
                    message = "ERROR: Already in Pantry. You can change the quantity instead"
                    data.update({
                        'message': message,
                    })
                    return data
            if user_has == False:
                relate = UserToPantry(user=user, pantry_item=p)
                relate.save()
                message = "Added to Pantry"
                data.update({
                    'message': message,
                    'item': relate,
                })
                return data
    
    if already_in == False:
        api_client = RecipeClient()
        results = api_client.get_ingredients(ingredientName, intolerance)
        print(results)
        for result in results:
            if ingredientName == result['name']:
                item = Pantry(name=result['name'], api_id=result['id'], aisle=result['aisle'], image=result['image'])
                item.save()
                relate = UserToPantry(user=user, pantry_item=item)
                relate.save()
                message = "Added to Pantry"
                data.update({
                    'message': message,
                    'item': relate,
                })
                return data
    message = "ERROR: Pantry item could not be found or API error. Sorry :("
    data.update({
        'message': message,
    })
    return data

# searching recipes by ingredients, adds those in a database to reduce api call
def prepare_simple_results(results):
    recipes = []
    found = []
    not_found = []
    check_found = False
    database = list(Recipes.objects.all())
    
    for i in results:
        if i["missedIngredientCount"] == 0:
            recipes.append(i['id'])
    
    if len(recipes) == 0:
        for i in results:
            for j in database:
                if i['id'] == j.api_id:
                    found.append({
                        'id': j.api_id,
                        'image': j.image,
                        'title': j.title,
                        'serves': j.serves,
                        'time': j.time,
                        'health': j.health_score,
                        'url': j.source_url,
                        'credit': j.credit,
                        'likes': j.popularity
                    })
                    check_found = True
            if check_found == False:
                not_found.append(str(i['id']))
            check_found = False
        if len(not_found) > 0:
            api_client = RecipeClient()
            results2 = api_client.get_recipe_bulk(not_found)
            for i in results2:
                try:
                    wine = i['winePairing']['pairingText']
                except KeyError:
                    wine = "None"
                try:
                    img = i['image']
                except KeyError:
                    img = '/static/img/core-img/salad.png'
                item = Recipes(
                    api_id=i['id'],
                    title=i['title'],
                    image=img,
                    serves=i['servings'],
                    time=i['readyInMinutes'],
                    source_url=i['sourceUrl'],
                    credit=i['creditsText'],
                    health_score=i['healthScore'],
                    popularity=i['aggregateLikes'],
                    wine_pairing=wine
                )
                item.save()
                found.append({
                    'id': item.api_id,
                    'image': item.image,
                    'title': item.title,
                    'serves': item.serves,
                    'time': item.time,
                    'health': item.health_score,
                    'url': item.source_url,
                    'credit': item.credit,
                    'likes': item.popularity
                })
                for j in i['extendedIngredients']:
                    amount = j['measures']['metric']['amount']
                    unit = j['measures']['metric']['unitShort']
                    name = j['name']
                    if j['meta']:
                        meta = ', '.join(j['meta'])
                    else:
                        meta = ''
                    ing = RecipeIngredients(
                        recipe_id=item,
                        name=name,
                        amount=amount,
                        unit=unit,
                        meta=meta
                    )
                    ing.save()
        data = {
            'message': "No results with just MyPantry items. Add more items to MyPantry. Below are results in order of lowest to highest missing ingredients.",
            'recipes': found,
        }
        return data
    
    for i in recipes:
        for j in database:
            if i == j.api_id:
                found.append({
                        'id': j.api_id,
                        'image': j.image,
                        'title': j.title,
                        'serves': j.serves,
                        'time': j.time,
                        'health': j.health_score,
                        'url': j.source_url,
                        'credit': j.credit,
                        'likes': j.popularity
                    })
                check_found = True
        if check_found == False:
            not_found.append(i)
        check_found = False
    if len(not_found) > 0:
        api_client = RecipeClient()
        results2 = api_client.get_recipe_bulk(not_found)
        for i in results2:
            try:
                wine = i['winePairing']['pairingText']
            except KeyError:
                wine = "None"
            try:
                img = i['image']
            except KeyError:
                img = '/static/img/core-img/salad.png'
            item = Recipes(
                api_id=i['id'],
                title=i['title'],
                image=img,
                serves=i['servings'],
                time=i['readyInMinutes'],
                source_url=i['sourceUrl'],
                credit=i['creditsText'],
                health_score=i['healthScore'],
                popularity=i['aggregateLikes'],
                wine_pairing=wine
            )
            item.save()
            found.append({
                    'id': item.api_id,
                    'image': item.image,
                    'title': item.title,
                    'serves': item.serves,
                    'time': item.time,
                    'health': item.health_score,
                    'url': item.source_url,
                    'credit': item.credit,
                    'likes': item.popularity
                })
            for j in i['extendedIngredients']:
                amount = j['metirc']['amount']
                unit = j['metric']['unitShort']
                name = j['name']
                if j['meta']:
                    meta = ', '.join(j['meta'])
                else:
                    meta = ''
                ing = RecipeIngredients(
                    recipe_id=item,
                    name=name,
                    amount=amount,
                    unit=unit,
                    meta=meta
                )
                ing.save()
        
    data = {'recipes': found}
    return data

# Searching recipes using complex method, adds them to database
def prepare_advance_results(results):
    if results == None:
        data = {'message': "API ERROR. Check back tomorrow. Sorry :("}
        response = JsonResponse(data)
        response.status_code = 500
        return response 
    if len(results['results']) == 0:
        data = {'message': "No results. Try just searching without MyPantry items instead"}
        response = JsonResponse(data)
        response.status_code = 400
        return response
    
    recipes = []
    found = []
    check_found = False
    database = list(Recipes.objects.all())
    
    for i in results['results']:
        for j in database:
            if j.api_id == i['id']:
                found.append({
                    'id': j.api_id,
                    'image': j.image,
                    'title': j.title,
                    'serves': j.serves,
                    'time': j.time,
                    'health': j.health_score,
                    'url': j.source_url,
                    'credit': j.credit,
                    'likes': j.popularity,
                })
                check_found = True
        if check_found == False:
            try:
                wine = i['winePairing']['pairingText']
            except KeyError:
                wine = "None"
            try:
                img = i['image']
            except KeyError:
                img = '/static/img/core-img/salad.png'
            item = Recipes(
                api_id=i['id'],
                title=i['title'],
                image=img,
                serves=i['servings'],
                time=i['readyInMinutes'],
                source_url=i['sourceUrl'],
                credit=i['creditsText'],
                health_score=i['healthScore'],
                popularity=i['aggregateLikes'],
                wine_pairing=wine
            )
            item.save()
            found.append({
                'id': item.api_id,
                'image': item.image,
                'title': item.title,
                'serves': item.serves,
                'time': item.time,
                'health': item.health_score,
                'url': item.source_url,
                'credit': item.credit,
                'likes': item.popularity
            })
            for j in i['extendedIngredients']:
                amount = j['measures']['metric']['amount']
                unit = j['measures']['metric']['unitShort']
                name = j['name']
                if j['meta']:
                    meta = ', '.join(j['meta'])
                else:
                    meta = ''
                ing = RecipeIngredients(
                    recipe_id=item,
                    name=name,
                    amount=amount,
                    unit=unit,
                    meta=meta
                )
                ing.save()
        check_found = False
    data = {'recipes': found}
    response = JsonResponse(data)
    response.status_code = 200
    return response

# Converting units from metric to imperial if suitable
def convertunit(name, unit, amount):
    metric_weight = ['g', 'kg']
    metric_volume = ['ml', 'l']
    weight = False
    volume = False
    amount = float(amount)
    if unit.lower() in metric_weight:
        if unit == 'g':
            unit = 'grams'
        else:
            unit = 'kilograms'
        weight = True
    elif unit.lower() in metric_volume:
        if unit == 'ml':
            unit = 'millilitres'
        else:
            unit = 'litres'
        volume = True
    else:
        return None
    api_client = RecipeClient()
    result = ""
    if weight == True:
        if unit == 'kilograms':
            result = api_client.convert(name, amount, unit, "pounds")
        else:
            if amount > 500:
                result = api_client.convert(name, amount, unit, "pounds")
            else:
                result = api_client.convert(name, amount, unit, "ounces")
    else:
        if unit == 'litres':
            result = api_client.convert(name, amount, unit, "pints")
        else:
            if amount > 500:
                result = api_client.convert(name, amount, unit, "pints")
            else:
                result = api_client.convert(name, amount, unit, "cup")
    if result != None:
        return result['answer']
    else:
        return "API ERROR"

# get similar recipes to id given, adds results to database        
def get_similar_recipes(others):
    similar = []
    not_found = []
    api_client = RecipeClient()
    for other in others:
        try:
            sim = Recipes.objects.get(api_id=other['id'])
        except Recipes.DoesNotExist:
            n = api_client.get_recipe_info(other['id'])
            if settings.DEBUG == 'True':
                pprint.pprint(n)
            try:
                wine = n['winePairing']['pairingText']
            except KeyError:
                wine = "None"
            try:
                i = n['image']
            except KeyError:
                i = '/static/img/core-img/salad.png'
            sim = Recipes(
                api_id=n['id'],
                title=n['title'],
                image=i,
                serves=n['servings'],
                time=n['readyInMinutes'],
                source_url=n['sourceUrl'],
                credit=n['creditsText'],
                health_score=n['healthScore'],
                popularity=n['aggregateLikes'],
                wine_pairing=wine
                )
            sim.save()
            for j in n['extendedIngredients']:
                amount = j['measures']['metric']['amount']
                unit = j['measures']['metric']['unitShort']
                name = j['name']
                if j['meta']:
                    meta = ', '.join(j['meta'])
                else:
                    meta = ''
                ing = RecipeIngredients(
                    recipe_id=sim,
                    name=name,
                    amount=amount,
                    unit=unit,
                    meta=meta
                )
                ing.save()
        similar.append(sim)
    return similar
    

