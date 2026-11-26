from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db import transaction

from main.models import Profile, Project, Rating


DEMO_PASSWORD = 'wage-wave-demo'


class Command(BaseCommand):
    help = 'Create or refresh the Wage Wave showcase demo data.'

    @transaction.atomic
    def handle(self, *args, **options):
        Project.objects.filter(project_name__startswith='Demo ').delete()
        User.objects.filter(username__startswith='demo_').delete()

        land_owners = self.create_profiles([
            ('demo_land_alice', 'Alice Green', '120.00'),
            ('demo_land_ben', 'Ben Fields', '75.50'),
            ('demo_land_carla', 'Carla Orchard', '210.00'),
        ], Profile.RegisteringAs.LAND_OWNER, 'Riverside farms')
        labourers = self.create_profiles([
            ('demo_labour_dan', 'Daniel Okoro', None),
            ('demo_labour_emma', 'Emma Stone', None),
            ('demo_labour_farah', 'Farah Malik', None),
            ('demo_labour_gideon', 'Gideon Wells', None),
        ], Profile.RegisteringAs.LABOUR, 'Green Valley')
        machinery_owners = self.create_profiles([
            ('demo_machine_tractor', 'Tom Tractor', None, 2),
            ('demo_machine_harvester', 'Hana Harvester', None, 1),
            ('demo_machine_irrigation', 'Ibrahim Irrigation', None, 3),
        ], Profile.RegisteringAs.MACHINERY, 'Equipment Cooperative')

        project_a = Project.objects.create(
            project_name='Demo A - Riverside Vegetables',
            address='Riverside North Field',
            land_owner=land_owners[0],
            labour=labourers[0],
            machinery_contributor=machinery_owners[0],
            expected_timeline='12 weeks',
            invested_money='1450000.00',
            expected_revenue='2500000.00',
            description='A fully staffed vegetable project growing tomatoes, peppers, and leafy greens.',
            status=Project.Status.ACTIVE,
        )
        Project.objects.create(
            project_name='Demo B - Ben Fields Grains',
            address='Ben Fields East Plot',
            land_owner=land_owners[1],
            machinery_contributor=machinery_owners[1],
            expected_timeline='16 weeks',
            invested_money='1750000.00',
            expected_revenue='3000000.00',
            description='A grain project with land and a harvester ready, looking for a labour team.',
            status=Project.Status.LOOKING_FOR_LABOUR,
        )
        Project.objects.create(
            project_name='Demo C - Orchard Renewal',
            address='Carla Orchard West Block',
            labour=labourers[1],
            expected_timeline='20 weeks',
            invested_money='1150000.00',
            expected_revenue='2250000.00',
            description='An orchard renewal project looking for land and machinery partners.',
            status=Project.Status.LOOKING_FOR_LAND_MACHINERY,
        )
        project_d = Project.objects.create(
            project_name='Demo D - Community Harvest',
            address='Community Farm South Field',
            land_owner=land_owners[2],
            labour=labourers[2],
            machinery_contributor=machinery_owners[2],
            expected_timeline='14 weeks',
            invested_money='1550000.00',
            expected_revenue='2750000.00',
            description='A completed community harvest project that brought three local resources together.',
            status=Project.Status.COMPLETED,
        )
        Rating.objects.create(
            project=project_d,
            reviewer=land_owners[2],
            reviewed_user=labourers[2],
            rating=5,
            comment='Excellent coordination throughout the harvest.',
        )
        Rating.objects.create(
            project=project_d,
            reviewer=labourers[2],
            reviewed_user=land_owners[2],
            rating=4,
            comment='A generous and well-prepared land partner.',
        )
        Rating.objects.create(
            project=project_d,
            reviewer=machinery_owners[2],
            reviewed_user=labourers[2],
            rating=5,
            comment='Very reliable and easy to work with.',
        )

        self.stdout.write(self.style.SUCCESS('Wage Wave demo data loaded.'))
        self.stdout.write('Demo password for every demo user: wage-wave-demo')
        self.stdout.write('Run this command again any time to refresh the dataset.')

    def create_profiles(self, users, role, address):
        profiles = []
        for user_data in users:
            username, name, land_size = user_data[:3]
            machines_available = user_data[3] if len(user_data) > 3 else 0
            user = User.objects.create_user(username=username, password=DEMO_PASSWORD)
            profiles.append(Profile.objects.create(
                user=user,
                name=name,
                registering_as=role,
                address=address,
                land_size=land_size,
                machines_available=machines_available,
            ))
        return profiles