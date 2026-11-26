import json
from pathlib import Path

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from main.models import Profile, Project, Rating


DEMO_PASSWORD = 'wage-wave-demo'
DEMO_DATA_FILE = Path(__file__).resolve().parents[2] / 'data' / 'demo_data.json'


class Command(BaseCommand):
    help = 'Create or refresh the Wage Wave showcase demo data.'

    @transaction.atomic
    def handle(self, *args, **options):
        data = json.loads(DEMO_DATA_FILE.read_text(encoding='utf-8'))

        Project.objects.filter(project_name__startswith='Demo ').delete()
        User.objects.filter(username__startswith='demo_').delete()

        profiles = self.create_profiles(data['profiles'])
        projects = self.create_projects(data['projects'], profiles)
        self.create_ratings(data['ratings'], projects, profiles)

        self.stdout.write(self.style.SUCCESS('Wage Wave demo data loaded.'))
        self.stdout.write('Demo password for every demo user: wage-wave-demo')
        self.stdout.write('Run this command again any time to refresh the dataset.')

    def create_profiles(self, profile_data):
        profiles = {}
        for item in profile_data:
            user = User.objects.create_user(
                username=item['username'],
                password=DEMO_PASSWORD,
            )
            profiles[item['username']] = Profile.objects.create(
                user=user,
                name=item['name'],
                registering_as=item['registering_as'],
                address=item['address'],
                land_size=item['land_size'],
                machines_available=item['machines_available'],
            )
        return profiles

    def create_projects(self, project_data, profiles):
        projects = {}
        profile_fields = ('land_owner', 'labour', 'machinery_contributor')
        for item in project_data:
            fields = {
                field: profiles[item[field]] if item[field] else None
                for field in profile_fields
            }
            project = Project.objects.create(
                project_name=item['project_name'],
                address=item['address'],
                expected_timeline=item['expected_timeline'],
                invested_money=item['invested_money'],
                expected_revenue=item['expected_revenue'],
                description=item['description'],
                status=item['status'],
                **fields,
            )
            projects[item['project_name']] = project
        return projects

    def create_ratings(self, rating_data, projects, profiles):
        for item in rating_data:
            Rating.objects.create(
                project=projects[item['project']],
                reviewer=profiles[item['reviewer']],
                reviewed_user=profiles[item['reviewed_user']],
                rating=item['rating'],
                comment=item['comment'],
            )