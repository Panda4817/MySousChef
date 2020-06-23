from django.test import TestCase, Client
from .models import Profile
from django.contrib.auth.models import User
import unittest
from .forms import SignUpForm
from .signals import show_login_message, show_logout_message
from django.contrib.auth.signals import user_logged_out, user_logged_in
from django.contrib import messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware

# Create your tests here.
class ModelsTestCase(TestCase):
    def setUp(self):
        # Create User instance
        u = User.objects.create_user('testing', password='hello')

    def test_count_user_instance(self):
        u = User.objects.filter(username="testing")
        self.assertEqual(len(u), 1)
    
    def test_count_profile_instance(self):
        u = User.objects.filter(username="testing")
        p = Profile.objects.filter(user=u[0])
        self.assertEqual(len(p), 1)
    
    def test_index(self):
        c = Client()
        response = c.get("", secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_register(self):
        c = Client()
        response = c.get("/register", secure=True)
        self.assertEqual(response.status_code, 200)
    
    def test_login(self):
        c = Client()
        u = User.objects.get_by_natural_key('testing')
        request = c.get("/login", secure=True, follow = True)
        self.assertEqual(request.status_code, 200)
        request2 = c.login(username='testing', password="hello")
        self.assertTrue(request2)
        
    def test_logout(self):
        c = Client()
        u = User.objects.get_by_natural_key('testing')
        c.login(username='testing', password="hello")
        check = c.get("/logout", secure=True, follow=True)
        self.assertRedirects(check, "https://testserver/", 302, 200)
    
    def test_account(self):
        c = Client()
        u = User.objects.get_by_natural_key('testing')
        c.login(username='testing', password="hello")
        response = c.get("/account", secure=True, follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_contact(self):
        c = Client()
        response = c.get("/contact", secure=True)
        self.assertEqual(response.status_code, 200)
        c.login(username='testing', password="hello")
        response2 = c.get("/contact", secure=True)
        self.assertEqual(response2.status_code, 200)

