from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Team
from .serializers import TeamSerializer
from apps.accounts.models import User, Profile

@login_required
def team_list(request):
    """Display list of teams and allow management"""
    # Süper kullanıcı tüm takımları görebilir
    if request.user.is_superuser:
        teams = Team.objects.all()
    # Takım liderleri sadece kendi takımlarını görebilir
    elif hasattr(request.user, 'led_teams'):
        teams = request.user.led_teams.all()
    # Normal kullanıcılar sadece kendi takımlarını görebilir
    elif hasattr(request.user, 'profile') and request.user.profile.team:
        teams = Team.objects.filter(id=request.user.profile.team.id)
    else:
        teams = Team.objects.none()

    # Atanmamış kullanıcıları bul
    unassigned_users = User.objects.filter(
        Q(profile__team__isnull=True) | Q(profile__isnull=True)
    ).exclude(id=request.user.id)

    context = {
        'teams': teams,
        'unassigned_users': unassigned_users,
        'team_types': Team.TEAM_TYPES,
        'is_superuser': request.user.is_superuser,
        'user_team': request.user.profile.team if hasattr(request.user, 'profile') else None
    }
    return render(request, 'teams/team_list.html', context)

@login_required
def create_team(request):
    """Create a new team"""
    if not request.user.is_superuser:
        messages.error(request, "Only administrators can create teams")
        return redirect('teams:team_list')
        
    if request.method == 'POST':
        name = request.POST.get('name')
        team_type = request.POST.get('team_type')
        description = request.POST.get('description', '')
        leader_id = request.POST.get('leader')
        
        try:
            leader = User.objects.get(id=leader_id) if leader_id else None
            
            team = Team.objects.create(
                name=name,
                team_type=team_type,
                description=description,
                leader=leader
            )
            
            # If leader is selected, add them to the team
            if leader and hasattr(leader, 'profile'):
                leader.profile.team = team
                leader.profile.save()
                
            messages.success(request, f"Team '{name}' created successfully")
            return redirect('teams:team_members', team_id=team.id)
            
        except Exception as e:
            messages.error(request, f"Error creating team: {str(e)}")
            
    return redirect('teams:team_list')

@login_required
def team_members(request, team_id):
    """Display and manage team members"""
    team = get_object_or_404(Team, id=team_id)
    
    # Sadece süper kullanıcı ve takım lideri erişebilir
    if not (request.user.is_superuser or team.leader == request.user):
        messages.error(request, "You don't have permission to manage team members")
        return redirect('teams:team_list')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        user_id = request.POST.get('user_id')
        
        try:
            user = User.objects.get(id=user_id)
            
            if action == 'add':
                # Kullanıcıyı takıma ekle
                if not hasattr(user, 'profile'):
                    Profile.objects.create(user=user, team=team)
                else:
                    user.profile.team = team
                    user.profile.save()
                messages.success(request, f"{user.get_full_name()} added to team")
                
            elif action == 'remove':
                # Kullanıcıyı takımdan çıkar
                if hasattr(user, 'profile'):
                    user.profile.team = None
                    user.profile.save()
                messages.success(request, f"{user.get_full_name()} removed from team")
                
            elif action == 'make_leader':
                # Kullanıcıyı takım lideri yap
                if request.user.is_superuser:  # Sadece süper kullanıcı lider atayabilir
                    team.leader = user
                    team.save()
                    messages.success(request, f"{user.get_full_name()} is now team leader")
                else:
                    messages.error(request, "Only administrators can assign team leaders")
                    
        except User.DoesNotExist:
            messages.error(request, "User not found")
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
    
    # Takıma atanabilecek kullanıcıları bul
    available_users = User.objects.filter(
        Q(profile__team__isnull=True) | Q(profile__isnull=True)
    ).exclude(id=request.user.id)
    
    context = {
        'team': team,
        'team_members': Profile.objects.filter(team=team),
        'available_users': available_users,
        'is_superuser': request.user.is_superuser
    }
    
    return render(request, 'teams/team_members.html', context)

@login_required
def set_team_leader(request, team_id):
    """Set team leader"""
    if not request.user.is_superuser:
        messages.error(request, "Only administrators can set team leaders")
        return redirect('teams:team_list')
        
    team = get_object_or_404(Team, id=team_id)
    
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        try:
            user = User.objects.get(id=user_id)
            team.leader = user
            team.save()
            messages.success(request, f"{user.get_full_name()} is now leader of {team.name}")
        except User.DoesNotExist:
            messages.error(request, "User not found")
            
    return redirect('teams:team_members', team_id=team.id)
