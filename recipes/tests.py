from django.test import TestCase, Client
from .models import *
from django.contrib.auth.models import User
import unittest
from django.db.utils import IntegrityError
from django.conf import settings

# Create your tests here.
class ModelsTestCase(TestCase):
    def setUp(self):
        u = User.objects.create_user('test', password='test')
        p = Pantry.objects.create(name="milk", api_id=123, aisle="dairy", image="milk.png")
        e = Pantry.objects.create(name="egg", api_id=456, aisle="dairy", image="egg.png")
        
    def test_str_pantry(self):
        p = Pantry.objects.filter(name='milk')
        self.assertEqual(p[0].__str__(), "milk - 123 - dairy")
    
    def test_usertopantry_valid(self):
        p = Pantry.objects.filter(name='milk')
        u = User.objects.filter(username='test')
        utp = UserToPantry.objects.create(user=u[0], pantry_item=p[0])
        self.assertTrue(utp.is_valid_usertopantry())

    def test_usertopantry_invalid(self):
        p = Pantry.objects.filter(name='egg')
        u = User.objects.filter(username='test')
        with self.assertRaises(expected_exception=IntegrityError):
            utp = UserToPantry.objects.create(user=u[0], pantry_item=p[0], quantity=0)
    
    def test_pantry_view(self):
        c = Client()
        u = User.objects.get_by_natural_key('test')
        c.force_login(u)
        response = c.get("/pantry", secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_shopping_list_view(self):
        c = Client()
        u = User.objects.get_by_natural_key('test')
        c.force_login(u)
        response = c.get("/shopping-list", secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_search_recipes_view(self):
        c = Client()
        u = User.objects.get_by_natural_key('test')
        c.force_login(u)
        response = c.get("/search-recipes", secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_myrecipes_view(self):
        c = Client()
        u = User.objects.get_by_natural_key('test')
        c.force_login(u)
        response = c.get("/myrecipe", secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_dashboard_view(self):
        c = Client()
        u = User.objects.get_by_natural_key('test')
        c.force_login(u)
        response = c.get("/dashboard", secure=True)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_view_without_login(self):
        c = Client()
        response = c.get("/dashboard", secure=True, follow=True)
        self.assertRedirects(response, "https://testserver/login?next=%2fdashboard", 302, 200)
