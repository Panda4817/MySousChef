from django.test import TestCase
from .models import Profile
from django.contrib.auth.models import User
import unittest

# Create your tests here.
class ModelsTestCase(TestCase):
    def setUp(self):
        # Create User instance
        user = User.objects.create(username="testing", email="testing@testing.com", password="hello")

    def test_count_user_instance(self):
        u = User.objects.filter(username="testing")
        self.assertEqual(len(u), 1)
    
    def test_count_profile_instance(self):
        u = User.objects.filter(username="testing")
        p = Profile.objects.filter(user=u[0])
        self.assertEqual(len(p), 1)
