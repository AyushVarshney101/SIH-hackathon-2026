from django.db import models
from django.conf import settings


class Profile(models.Model):
	class RegisteringAs(models.TextChoices):
		LAND_OWNER = 'land_owner', 'Land Owner'
		LABOUR = 'labour', 'Labour'
		MACHINERY = 'machinery', 'Idle Farming Machinery'

	user = models.OneToOneField(
		settings.AUTH_USER_MODEL,
		on_delete=models.CASCADE,
		blank=True,
		null=True,
		related_name='profile',
	)
	name = models.CharField(max_length=150)
	registering_as = models.CharField(max_length=20, choices=RegisteringAs.choices)
	address = models.CharField(max_length=255)
	land_size = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
	machines_available = models.PositiveIntegerField(default=0)

	def __str__(self):
		return self.name


class Project(models.Model):
	class Status(models.TextChoices):
		PLANNING = 'planning', 'Planning'
		ACTIVE = 'active', 'Active'
		LOOKING_FOR_LABOUR = 'looking_for_labour', 'Looking for Labour'
		LOOKING_FOR_LAND_MACHINERY = 'looking_for_land_machinery', 'Looking for Land + Machinery'
		COMPLETED = 'completed', 'Completed'

	project_name = models.CharField(max_length=150)
	address = models.CharField(max_length=255)
	land_owner = models.ForeignKey(
		Profile,
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
		related_name='land_projects',
	)
	labour = models.ForeignKey(
		Profile,
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
		related_name='labour_projects',
	)
	machinery_contributor = models.ForeignKey(
		Profile,
		on_delete=models.SET_NULL,
		blank=True,
		null=True,
		related_name='machinery_projects',
	)
	expected_timeline = models.CharField(max_length=100)
	invested_money = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	expected_revenue = models.DecimalField(max_digits=12, decimal_places=2, default=0)
	description = models.TextField(blank=True)
	status = models.CharField(max_length=30, choices=Status.choices, default=Status.PLANNING)

	def __str__(self):
		return self.project_name


class Rating(models.Model):
	project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='ratings')
	reviewer = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ratings_given')
	reviewed_user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='ratings_received')
	rating = models.PositiveSmallIntegerField()
	comment = models.TextField(blank=True)

	def __str__(self):
		return f'{self.rating}/5 for {self.reviewed_user}'
