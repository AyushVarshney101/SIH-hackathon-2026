from io import StringIO

from django.contrib.auth.models import User
from django.core.management import call_command
from django.test import TestCase

from main.models import Profile, Project, Rating


class LoadDemoDataCommandTests(TestCase):
    def test_loads_demo_data_from_json_and_is_repeatable(self):
        call_command('load_demo_data', stdout=StringIO())
        call_command('load_demo_data', stdout=StringIO())

        self.assertEqual(User.objects.filter(username__startswith='demo_').count(), 10)
        self.assertEqual(Profile.objects.count(), 10)
        self.assertEqual(Project.objects.count(), 4)
        self.assertEqual(Rating.objects.count(), 3)

        project = Project.objects.get(project_name='Demo A - Riverside Vegetables')
        self.assertEqual(project.land_owner.user.username, 'demo_land_alice')
        self.assertEqual(project.labour.user.username, 'demo_labour_dan')
