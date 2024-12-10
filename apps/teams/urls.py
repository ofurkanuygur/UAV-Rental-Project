from django.urls import path
from . import views

app_name = 'teams'

urlpatterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.create_team, name='create_team'),
    path('members/<int:team_id>/', views.team_members, name='team_members'),
    path('leader/<int:team_id>/', views.set_team_leader, name='set_team_leader'),
]
