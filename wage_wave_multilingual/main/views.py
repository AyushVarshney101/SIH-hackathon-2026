import json
import re
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from .forms import ProjectForm, RatingForm, RegistrationForm
from .models import Profile, Project, Rating

def home(request):
	return render(request, 'main/home.html')


def register(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	form = RegistrationForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		user = User.objects.create_user(
			username=form.cleaned_data['username'],
			password=form.cleaned_data['password'],
		)
		profile = Profile.objects.create(
			user=user,
			name=form.cleaned_data['name'],
			registering_as=form.cleaned_data['registering_as'],
			address=form.cleaned_data['address'],
			machines_available=form.cleaned_data.get('machines_available') or 0,
		)
		login(request, user)
		return redirect('dashboard')
	return render(request, 'main/register.html', {'form': form})


def login_view(request):
	if request.user.is_authenticated:
		return redirect('dashboard')
	error = None
	if request.method == 'POST':
		username = request.POST.get('username', '')
		password = request.POST.get('password', '')
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			return redirect('dashboard')
		error = 'Invalid username or password.'
	return render(request, 'main/login.html', {'error': error})


@login_required
def dashboard(request):
	profile = request.user.profile
	dashboard_names = {
		Profile.RegisteringAs.LABOUR: 'labour_dashboard',
		Profile.RegisteringAs.LAND_OWNER: 'land_owner_dashboard',
		Profile.RegisteringAs.MACHINERY: 'machinery_dashboard',
	}
	return redirect(dashboard_names[profile.registering_as])


@login_required
def role_dashboard(request, role):
	profile = request.user.profile
	if profile.registering_as != role:
		return redirect('dashboard')
	return render(request, 'main/dashboard.html', {
		'profile': profile,
		'dashboard_role': role,
	})


def labour_dashboard(request):
	return role_dashboard(request, Profile.RegisteringAs.LABOUR)


def land_owner_dashboard(request):
	return role_dashboard(request, Profile.RegisteringAs.LAND_OWNER)


def machinery_dashboard(request):
	return role_dashboard(request, Profile.RegisteringAs.MACHINERY)


def marketplace(request):
	return render(request, 'main/marketplace.html')


@login_required
def placeholder_page(request, page_name):
	page_details = {
		'find-work': ('Find Work', 'Browse farming opportunities that need your skills.'),
		'list-land': ('List Land', 'Share idle farmland with a collaborative farming project.'),
		'contribute-machinery': ('Contribute Idle Machinery', 'Make your available machinery visible to farming projects.'),
		'profile': ('Profile', 'Your Wage Wave profile details will appear here.'),
		'current-projects': ('Current Projects', 'Project listings and vacancies will appear here.'),
	}
	title, description = page_details[page_name]
	return render(request, 'main/placeholder.html', {
		'page_title': title,
		'page_description': description,
	})


@login_required
def profile_page(request):
	profile = request.user.profile
	involved = Q(land_owner=profile) | Q(labour=profile) | Q(machinery_contributor=profile)
	current_projects = Project.objects.select_related(
		'land_owner', 'labour', 'machinery_contributor',
	).filter(involved).exclude(status=Project.Status.COMPLETED)
	completed_projects = Project.objects.select_related(
		'land_owner', 'labour', 'machinery_contributor',
	).filter(involved, status=Project.Status.COMPLETED)

	def project_summary(project, include_ratings=False):
		participants = []
		rate_participants = []
		role = ''
		for participant, participant_role in (
			(project.land_owner, 'Land Owner'),
			(project.labour, 'Labour'),
			(project.machinery_contributor, 'Machinery Contributor'),
		):
			if participant and participant.id == profile.id:
				role = participant_role
			elif participant:
				participants.append(participant.name)
				participant_rating = Rating.objects.filter(
					project=project,
					reviewer=profile,
					reviewed_user=participant,
				).first() if include_ratings else None
				rate_participants.append({
					'profile': participant,
					'role': participant_role,
					'rating': participant_rating,
					'stars': '★' * participant_rating.rating + '☆' * (5 - participant_rating.rating) if participant_rating else '',
				})
		received_ratings = Rating.objects.filter(project=project, reviewed_user=profile) if include_ratings else []
		return {
			'project': project,
			'role': role,
			'participants': participants,
			'ratings': [
				{'rating': rating, 'stars': '★' * rating.rating + '☆' * (5 - rating.rating)}
				for rating in received_ratings
			],
			'rate_participants': rate_participants,
		}

	return render(request, 'main/profile.html', {
		'profile': profile,
		'rating_form': RatingForm(),
		'current_projects': [project_summary(project) for project in current_projects],
		'completed_projects': [project_summary(project, include_ratings=True) for project in completed_projects],
	})


@login_required
@require_POST
def rate_participant(request, project_id, participant_id):
	project = get_object_or_404(Project, pk=project_id)
	reviewer = request.user.profile
	participant = get_object_or_404(Profile, pk=participant_id)
	project_participants = [project.land_owner, project.labour, project.machinery_contributor]
	if project.status != Project.Status.COMPLETED:
		messages.error(request, 'Only completed projects can be rated.')
	elif reviewer not in project_participants or participant not in project_participants:
		messages.error(request, 'Only project participants can give or receive ratings.')
	elif reviewer == participant:
		messages.error(request, 'You cannot rate yourself.')
	else:
		form = RatingForm(request.POST)
		if form.is_valid():
			Rating.objects.update_or_create(
				project=project,
				reviewer=reviewer,
				reviewed_user=participant,
				defaults={
					'rating': form.cleaned_data['rating'],
					'comment': form.cleaned_data['comment'],
				},
			)
			messages.success(request, f'Your rating for {participant.name} was saved.')
		else:
			messages.error(request, 'Choose a rating before submitting.')
	return redirect('profile')


@login_required
def resource_opportunities(request, resource):
	resource_details = {
		'labour': {
			'role': Profile.RegisteringAs.LABOUR,
			'field': 'labour',
			'title': 'Find Work',
			'intro': 'Find farming projects looking for manual labour.',
			'vacancy': 'Labour Required',
		},
		'land': {
			'role': Profile.RegisteringAs.LAND_OWNER,
			'field': 'land_owner',
			'title': 'Find Land',
			'intro': 'Find farming projects looking for productive farmland.',
			'vacancy': 'Land Required',
		},
		'machinery': {
			'role': Profile.RegisteringAs.MACHINERY,
			'field': 'machinery_contributor',
			'title': 'Find Machinery',
			'intro': 'Find farming projects looking for useful machinery.',
			'vacancy': 'Machinery Required',
		},
	}
	details = resource_details[resource]
	if request.user.profile.registering_as != details['role']:
		return redirect('dashboard')
	projects = Project.objects.select_related(
		'land_owner', 'labour', 'machinery_contributor',
	).filter(**{f"{details['field']}__isnull": True})
	return render(request, 'main/resource_opportunities.html', {
		'projects': projects,
		'resource': resource,
		'resource_title': details['title'],
		'resource_intro': details['intro'],
		'vacancy_label': details['vacancy'],
	})


def find_work(request):
	return resource_opportunities(request, 'labour')


def list_land(request):
	return resource_opportunities(request, 'land')


def contribute_machinery(request):
	return resource_opportunities(request, 'machinery')


@login_required
@require_POST
def enrol_in_project(request, project_id, resource):
	resource_details = {
		'labour': (Profile.RegisteringAs.LABOUR, 'labour', 'find_work', 'Labour'),
		'land': (Profile.RegisteringAs.LAND_OWNER, 'land_owner', 'list_land', 'Land'),
		'machinery': (Profile.RegisteringAs.MACHINERY, 'machinery_contributor', 'contribute_machinery', 'Machinery'),
	}
	role, field, page_name, resource_name = resource_details[resource]
	if request.user.profile.registering_as != role:
		return redirect('dashboard')
	project = get_object_or_404(Project, pk=project_id)
	if getattr(project, field) is not None:
		messages.error(request, f'{resource_name} is no longer needed for this project.')
	else:
		setattr(project, field, request.user.profile)
		project.save(update_fields=[field])
		messages.success(request, f'You joined {project.project_name}.')
	return redirect(page_name)


@login_required
def current_projects(request):
	projects = Project.objects.select_related(
		'land_owner', 'labour', 'machinery_contributor',
	).all()
	return render(request, 'main/current_projects.html', {'projects': projects})


@login_required
def project_detail(request, project_id):
	project = get_object_or_404(
		Project.objects.select_related('land_owner', 'labour', 'machinery_contributor'),
		pk=project_id,
	)
	return render(request, 'main/project_detail.html', {'project': project})


@login_required
def project_create(request):
	form = ProjectForm(request.POST or None)
	if request.method == 'POST' and form.is_valid():
		form.save()
		return redirect('current_projects')
	return render(request, 'main/project_form.html', {'form': form})


def logout_view(request):
	logout(request)
	return redirect('home')


DASHBOARD_URL_NAMES = {
	Profile.RegisteringAs.LABOUR: 'labour_dashboard',
	Profile.RegisteringAs.LAND_OWNER: 'land_owner_dashboard',
	Profile.RegisteringAs.MACHINERY: 'machinery_dashboard',
}


def _username_from_name(name):
	# "Ravi Kumar" -> "ravikumar". Falls back to "user" if nothing usable
	# (e.g. the name came through as only punctuation/whitespace).
	#
	# NOTE: this used to strip to [a-zA-Z0-9] only. The voice assistant runs
	# the whole conversation in Hindi, so Gemini often transcribes the name
	# in Devanagari script (e.g. "रवि कुमार") rather than Latin letters. An
	# ASCII-only regex threw all of that away, so *every* Devanagari name
	# collapsed to the same generic "user" account, and voice login (which
	# re-derives the username the same way) could only ever match the first
	# person who happened to register that way. \w in Python's re module is
	# Unicode-aware by default, so this keeps Devanagari/other scripts too.
	slug = re.sub(r'[^\w]', '', name, flags=re.UNICODE).lower()
	return slug or 'user'


def _unique_username(name):
	base = _username_from_name(name)
	username = base
	counter = 1
	while User.objects.filter(username=username).exists():
		counter += 1
		username = f'{base}{counter}'
	return username


def _create_user_with_unique_username(name, password):
	# _unique_username's "check, then create" is two separate steps, not one
	# atomic operation. If register_user ever fires twice in quick succession
	# for the same name (Gemini re-issuing a call it thinks didn't land is
	# the most likely trigger), both calls can pass the exists() check before
	# either commits, and the loser hits a raw IntegrityError on save. That
	# error has no matching branch in the voice assistant's script, so it
	# ends up improvising something like "technical error, please wait" and
	# retrying the exact same (still-colliding) name forever.
	#
	# Retry a few times on that specific collision instead of ever surfacing
	# it to the caller — from the model's perspective this should just work.
	for _ in range(5):
		username = _unique_username(name)
		try:
			return User.objects.create_user(username=username, password=password)
		except IntegrityError:
			continue
	raise IntegrityError(f'Could not allocate a unique username for {name!r} after 5 attempts.')


@csrf_exempt
def voice_register(request):
	# NOTE: csrf_exempt because the voice widget's fetch() call has no CSRF
	# token to send. This is a real attack surface for an endpoint that
	# creates accounts with a password — fine for a hackathon demo, but
	# before any real deployment this should require a CSRF token (or a
	# signed session token minted when the WebSocket connects) instead of
	# being wide open.
	if request.method != 'POST':
		return JsonResponse({'status': 'invalid method'}, status=405)
	try:
		data = json.loads(request.body)
		name = (data.get('name') or '').strip()
		password = data.get('password') or ''
		registering_as = data.get('registering_as') or ''
		address = (data.get('address') or '').strip() or 'Not provided'
		land_size = data.get('land_size')
		machines_available = data.get('machines_available') or 0

		if not name or not password:
			return JsonResponse({'status': 'error', 'message': 'Name and password are required.'}, status=400)
		if registering_as not in Profile.RegisteringAs.values:
			return JsonResponse({'status': 'error', 'message': 'registering_as must be one of: land_owner, labour, machinery.'}, status=400)
		if len(password) < 4:
			return JsonResponse({'status': 'error', 'message': 'Password must be at least 4 characters.'}, status=400)

		user = _create_user_with_unique_username(name, password)
		username = user.username
		Profile.objects.create(
			user=user,
			name=name,
			registering_as=registering_as,
			address=address,
			land_size=land_size if registering_as == Profile.RegisteringAs.LAND_OWNER else None,
			machines_available=machines_available if registering_as == Profile.RegisteringAs.MACHINERY else 0,
		)
		login(request, user)

		return JsonResponse({
			'status': 'success',
			'username': username,
			'redirect': reverse(DASHBOARD_URL_NAMES[registering_as]),
		})
	except Exception as e:
		# Log the real exception server-side (visible in the runserver
		# terminal) instead of handing raw Python error text back to Gemini
		# — the voice assistant has no script for an arbitrary stack trace
		# and tends to improvise a vague "technical error" excuse when it
		# gets one, then retry the exact same call forever.
		print(f'[voice_register] unexpected error: {e!r}')
		return JsonResponse({'status': 'error', 'message': 'registration_failed'}, status=400)


@csrf_exempt
def voice_login(request):
	# Same CSRF caveat as voice_register above.
	if request.method != 'POST':
		return JsonResponse({'status': 'invalid method'}, status=405)
	try:
		data = json.loads(request.body)
		name = (data.get('name') or '').strip()
		password = data.get('password') or ''
		if not name or not password:
			return JsonResponse({'status': 'error', 'message': 'Name and password are required.'}, status=400)

		# NOTE: we used to re-derive a username from this session's speech
		# transcription and authenticate() against that. That only works if
		# today's transcription slugs to exactly the string that was stored
		# at registration time. It doesn't hold up in practice — the
		# registering_as regex has changed over time (see _username_from_name's
		# history), and even without a code change, Gemini can transcribe the
		# same spoken name differently across two separate sessions (script,
		# spacing, a mis-heard syllable). Any mismatch made login fail forever
		# with no way for the user to recover, since they never see their
		# stored username.
		#
		# Instead, match against the Profile.name that was actually stored at
		# registration, normalized the same way, and verify the password
		# against whichever account matches. This is immune to the username
		# column being stale or having been derived under old logic.
		target = _username_from_name(name)
		user = None
		for profile in Profile.objects.select_related('user').filter(user__isnull=False):
			if _username_from_name(profile.name) == target and profile.user.check_password(password):
				user = profile.user
				break

		if user is None:
			return JsonResponse({'status': 'error', 'message': 'invalid_credentials'}, status=401)

		login(request, user)
		profile = user.profile
		return JsonResponse({
			'status': 'success',
			'redirect': reverse(DASHBOARD_URL_NAMES[profile.registering_as]),
		})
	except Exception as e:
		print(f'[voice_login] unexpected error: {e!r}')
		return JsonResponse({'status': 'error', 'message': 'login_failed'}, status=400)