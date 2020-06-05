import os
from django.shortcuts import render
from django.conf import settings
import requests
from urllib.parse import quote, urlencode

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
        filters = {'ingredients': ',+'.join(ingredients)}
        response = self._get('/recipes/findByIngredients', filters)
        return response