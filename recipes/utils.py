import os
from django.shortcuts import render
from django.conf import settings
import requests
from urllib.parse import quote, urlencode
from django.db import models
from django.contrib.auth.models import User
from .models import *

api_key = os.getenv('API_KEY')

class RecipeClient(object):

    def __init__(self):
        self.host = "api.spoonacular.com"
        self.key = api_key
        self.session = requests.session()

    def _get(self, path, filters):
        filters.update({'apiKey': self.key})
        filter_str = urlencode(filters)
        try:
            response = self.session.get('https://{}{}?{}'.format(self.host, path, filter_str))
            response.raise_for_status()
        except requests.RequestException:
            return None

        try:
            return response.json()
        except (KeyError, TypeError, ValueError):
            return None


    def search_recipes_ingredients(self, ingredients):
        filters = {'ingredients': ',+'.join(ingredients), 'ignorePantry': 'false'}
        response = self._get('/recipes/findByIngredients', filters)
        return response
    
    def get_recipe_info(self, recipe_id):
        filters = {'includeNutrition': 'true'}
        response = self._get('/recipes/{}/information'.format(recipe_id), filters)
        return response
    
    def get_recipes_similar(self, recipe_id):
        filters = {'number': 5}
        response = self._get('/recipes/{}/similar'.format(recipe_id), filters)
        return response
    
    def search_recipes_complex(self, query, cuisine, diet, intolerances, includeIngredients, meal_type):
        filters_list = [cuisine, diet, intolerances, meal_type]
        filters = {}
        for filter in filters_list:
            if filter is not None:
                if filters_list.index(filter) == 0:
                    filters.update({'cuisine': cuisine})
                if filters_list.index(filter) == 1:
                    filters.update({'diet': diet})
                if filters_list.index(filter) == 2:
                    filters.update({'intolerances': ',+'.join(intolerances)})
                if filters_list.index(filter) == 3:
                    filters.update({'type': meal_type})
        filters.update({
            'query': query,
            'includeIngredients': ',+'.join(includeIngredients), 
            'ignorePantry': 'false',
            'fillIngredients': 'true',
        })
        response = self._get('/recipes/complexSearch', filters)
        return response
    
    def convert(self, ingredientName, sourceAmount, sourceUnit, targetUnit):
        filters = {
            'ingredientName': ingredientName, 
            'sourceAmount': sourceAmount,
            'sourceUnit': sourceUnit,
            'targetUnit': targetUnit,
        }
        response = self._get('/recipes/convert', filters)
        return response
    
    def get_ingredients(self, query, intolerances):
        filters = {'query': query, 'metaInformation': 'true'}
        if intolerances is not None:
            filters.update({'intolerances': ',+'.join(intolerances)})
        response = self._get('/food/ingredients/autocomplete', filters)
        return response
    
    def get_substitute_name(self, ingredientName):
        filters = {'ingredientName': ingredientName}
        response = self._get('/food/ingredients/substitutes', filters)
        return response


def check_intolerance(intolerance):
    check_intolerance = True
    if len(intolerance) != 0:
        for i in intolerance:
            if i == "0":
                check_intolerance = False
    else:
        check_intolerance = False
    return check_intolerance

def addToPantry(ingredientName, user, intolerance):
    pantry = list(Pantry.objects.all())
    userpantry = list(UserToPantry.objects.filter(user=user))
    already_in = False
    user_has = False
    message = ""
    for p in pantry:
        if ingredientName == p.name:
            already_in = True
            for u in userpantry:
                if u.pantry_item.api_id == p.api_id:
                    user_has = True
                    message = "Already in Pantry"
                    return message
            if user_has == False:
                relate = UserToPantry(user=user, pantry_item=p)
                relate.save()
                message = "Added to Pantry"
                return message
    
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
                return message
    message = "ERROR: Pantry item could not be found"
    return message