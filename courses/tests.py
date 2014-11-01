from django.test import TestCase
from courses.models import *

# Create your tests here.

class DataFill(TestCase):
    def setUp(self):
        s = Style(name="Social 1")
        s.save()

    def test_something(self):
        pass