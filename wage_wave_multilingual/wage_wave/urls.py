"""
URL configuration for wage_wave project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path

from main.views import (
    dashboard,
    contribute_machinery,
    current_projects,
    enrol_in_project,
    find_work,
    home,
    land_owner_dashboard,
    list_land,
    labour_dashboard,
    login_view,
    logout_view,
    marketplace,
    machinery_dashboard,
    placeholder_page,
    project_create,
    project_detail,
    profile_page,
    rate_participant,
    register,
    voice_login,
    voice_register,
)

urlpatterns = [
    # Powers the navbar language switcher (POST with a 'language' field).
    # No URL prefixing (no /en/, /hi/, ...) — language is kept in the session.
    path('i18n/', include('django.conf.urls.i18n')),
    path('', home, name='home'),
    path('register/', register, name='register'),
    path('login/', login_view, name='login'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/labour/', labour_dashboard, name='labour_dashboard'),
    path('dashboard/land-owner/', land_owner_dashboard, name='land_owner_dashboard'),
    path('dashboard/machinery/', machinery_dashboard, name='machinery_dashboard'),
    path('marketplace/', marketplace, name='marketplace'),
    path('find-work/', find_work, name='find_work'),
    path('find-work/<int:project_id>/enrol/', lambda request, project_id: enrol_in_project(request, project_id, 'labour'), name='enrol_labour'),
    path('list-land/', list_land, name='list_land'),
    path('list-land/<int:project_id>/enrol/', lambda request, project_id: enrol_in_project(request, project_id, 'land'), name='enrol_land'),
    path('contribute-machinery/', contribute_machinery, name='contribute_machinery'),
    path('contribute-machinery/<int:project_id>/enrol/', lambda request, project_id: enrol_in_project(request, project_id, 'machinery'), name='enrol_machinery'),
    path('profile/', profile_page, name='profile'),
    path('current-projects/<int:project_id>/rate/<int:participant_id>/', rate_participant, name='rate_participant'),
    path('current-projects/', current_projects, name='current_projects'),
    path('current-projects/new/', project_create, name='project_create'),
    path('current-projects/<int:project_id>/', project_detail, name='project_detail'),
    path('logout/', logout_view, name='logout'),
    path('admin/', admin.site.urls),
    path('api/voice-register/', voice_register, name='voice_register'),
    path('api/voice-login/', voice_login, name='voice_login'),
]
