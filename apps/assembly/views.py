from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q, Sum, F, ExpressionWrapper, FloatField
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ValidationError
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import AssembledAircraft, WorkflowStep
from .serializers import AssembledAircraftSerializer, WorkflowStepSerializer
from apps.parts.models import Part, Aircraft
from apps.teams.models import Team
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

# Frontend Views
@login_required
def workflow_list(request):
    """Display list of all assembly workflows"""
    aircrafts = AssembledAircraft.objects.select_related(
        'assembly_team'
    ).prefetch_related('workflow_steps').all()
    teams = Team.objects.all()
    aircraft_types = Aircraft.objects.all()
    
    # Apply filters
    status_filter = request.GET.get('status')
    team_filter = request.GET.get('team')
    aircraft_type_filter = request.GET.get('aircraft_type')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    ordering = request.GET.get('ordering', '-created_at')
    
    if status_filter:
        aircrafts = aircrafts.filter(status=status_filter)
    if team_filter:
        aircrafts = aircrafts.filter(assembly_team_id=team_filter)
    if aircraft_type_filter:
        aircrafts = aircrafts.filter(aircraft_type_id=aircraft_type_filter)
    if date_from:
        aircrafts = aircrafts.filter(created_at__gte=date_from)
    if date_to:
        aircrafts = aircrafts.filter(created_at__lte=date_to)
    
    # Calculate statistics
    total_count = aircrafts.count()
    status_stats = dict(aircrafts.values('status').annotate(count=Count('id')).values_list('status', 'count'))
    team_stats = dict(aircrafts.values('assembly_team__name').annotate(count=Count('id')).values_list('assembly_team__name', 'count'))
    
    # Calculate completion rates
    completion_stats = aircrafts.aggregate(
        total_steps=Count('workflow_steps'),
        completed_steps=Count('workflow_steps', filter=Q(workflow_steps__status='COMPLETED')),
        failed_steps=Count('workflow_steps', filter=Q(workflow_steps__status='FAILED'))
    )
    
    if completion_stats['total_steps'] > 0:
        completion_stats['completion_rate'] = (completion_stats['completed_steps'] / completion_stats['total_steps']) * 100
    else:
        completion_stats['completion_rate'] = 0
    
    aircrafts = aircrafts.order_by(ordering)
    
    context = {
        'aircrafts': aircrafts,
        'teams': teams,
        'aircraft_types': aircraft_types,
        'total_count': total_count,
        'status_stats': status_stats,
        'team_stats': team_stats,
        'completion_stats': completion_stats,
        'selected_status': status_filter,
        'selected_team': team_filter,
        'selected_aircraft_type': aircraft_type_filter,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'selected_ordering': ordering
    }
    return render(request, 'assembly/workflow_list.html', context)

@login_required
def workflow_detail(request, pk):
    """Display details of a specific assembly workflow"""
    aircraft = get_object_or_404(AssembledAircraft, pk=pk)
    workflow_steps = aircraft.workflow_steps.all().order_by('created_at')
    
    # Calculate completion percentage
    total_steps = workflow_steps.count()
    completed_steps = workflow_steps.filter(status=WorkflowStep.Status.COMPLETED).count()
    completion_percentage = (completed_steps / total_steps * 100) if total_steps > 0 else 0
    
    # Check if all steps are completed
    all_steps_completed = all(
        step.status == WorkflowStep.Status.COMPLETED 
        for step in workflow_steps
    )
    
    context = {
        'aircraft': aircraft,
        'workflow_steps': workflow_steps,
        'completion_percentage': completion_percentage,
        'all_steps_completed': all_steps_completed
    }
    return render(request, 'assembly/workflow_detail.html', context)

@login_required
def create_aircraft(request):
    """Create a new aircraft assembly workflow"""
    if not request.user.profile.team or request.user.profile.team.team_type != 'assembly':
        messages.error(request, "Only assembly team members can create new aircraft assemblies")
        return redirect('assembly:workflow_list')
        
    if request.method == 'POST':
        try:
            aircraft_type_id = request.POST.get('aircraft_type')
            aircraft_name = request.POST.get('aircraft_name')
            
            if not aircraft_name:
                messages.error(request, "Aircraft name is required")
                return redirect('assembly:workflow_list')
            
            # Create new aircraft type if it doesn't exist
            aircraft_type, created = Aircraft.objects.get_or_create(
                id=aircraft_type_id if aircraft_type_id else None,
                defaults={
                    'name': aircraft_name,
                    'description': request.POST.get('description', '')
                }
            )
            
            with transaction.atomic():
                # Create the assembled aircraft
                assembled_aircraft = AssembledAircraft.objects.create(
                    aircraft_type=aircraft_type,
                    assembly_team=request.user.profile.team,
                    status=AssembledAircraft.Status.PENDING
                )
                
                # Create required parts for each team
                required_parts = {
                    'wing': [
                        ('wing_main', 'Ana Kanat'),
                        ('wing_aileron', 'Kanatçık'),
                        ('wing_flap', 'Flap'),
                        ('wing_slat', 'Slat'),
                    ],
                    'fuselage': [
                        ('fuselage_main', 'Ana Gövde'),
                        ('fuselage_nose', 'Burun Bölümü'),
                        ('fuselage_tail', 'Kuyruk Bölümü'),
                        ('fuselage_door', 'Kapı'),
                    ],
                    'tail': [
                        ('tail_vertical', 'Dikey Stabilizatör'),
                        ('tail_horizontal', 'Yatay Stabilizatör'),
                        ('tail_rudder', 'Dümen'),
                        ('tail_elevator', 'Elevator'),
                    ],
                    'avionics': [
                        ('avionics_flight_control', 'Uçuş Kontrol Sistemi'),
                        ('avionics_navigation', 'Navigasyon Sistemi'),
                        ('avionics_communication', 'İletişim Sistemi'),
                        ('avionics_radar', 'Radar Sistemi'),
                    ]
                }
                
                # Create parts for each team
                for team_type, parts in required_parts.items():
                    team = Team.objects.filter(team_type=team_type).first()
                    if team:
                        for part_type, part_name in parts:
                            part = Part.objects.create(
                                name=f"{part_name} - {aircraft_name}",
                                part_type=part_type,
                                description=f"{part_name} for {aircraft_name}",
                                team=team,
                                created_by=request.user,
                                status='pending'
                            )
                            assembled_aircraft.parts.add(part)
                
                # Create workflow steps
                steps = [
                    ('WING_PRODUCTION', 'wing'),
                    ('FUSELAGE_PRODUCTION', 'fuselage'),
                    ('TAIL_PRODUCTION', 'tail'),
                    ('AVIONICS_PRODUCTION', 'avionics'),
                    ('QUALITY_CHECK', 'assembly'),
                    ('ASSEMBLY', 'assembly'),
                    ('TESTING', 'assembly'),
                    ('FINAL_CHECK', 'assembly'),
                ]
                
                for step_type, team_type in steps:
                    team = Team.objects.filter(team_type=team_type).first()
                    if team:
                        WorkflowStep.objects.create(
                            assembled_aircraft=assembled_aircraft,
                            step_type=step_type,
                            assigned_team=team
                        )
                
            messages.success(request, "New aircraft assembly workflow created successfully")
            return redirect('assembly:workflow_detail', pk=assembled_aircraft.id)
            
        except Aircraft.DoesNotExist:
            messages.error(request, "Invalid aircraft type selected")
        except Exception as e:
            messages.error(request, f"Error creating aircraft assembly: {str(e)}")
    
    return redirect('assembly:workflow_list')

@login_required
def quality_checks(request):
    """Display quality checks for assembly team"""
    if not request.user.profile.team or request.user.profile.team.team_type != 'assembly':
        messages.error(request, "Only assembly team members can access quality checks")
        return redirect('home')
        
    # Get all workflow steps that are quality checks
    quality_steps = WorkflowStep.objects.filter(
        step_type='QUALITY_CHECK'
    ).select_related(
        'assembled_aircraft',
        'assigned_team'
    ).order_by('-created_at')
    
    # Apply filters
    status_filter = request.GET.get('status')
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    aircraft_type = request.GET.get('aircraft_type')
    
    if status_filter:
        quality_steps = quality_steps.filter(status=status_filter)
    if date_from:
        quality_steps = quality_steps.filter(created_at__gte=date_from)
    if date_to:
        quality_steps = quality_steps.filter(created_at__lte=date_to)
    if aircraft_type:
        quality_steps = quality_steps.filter(assembled_aircraft__aircraft_type_id=aircraft_type)
    
    # Calculate statistics
    stats = {
        'total_checks': quality_steps.count(),
        'passed_checks': quality_steps.filter(status='COMPLETED').count(),
        'failed_checks': quality_steps.filter(status='FAILED').count(),
        'pending_checks': quality_steps.filter(status='PENDING').count(),
        'in_progress_checks': quality_steps.filter(status='IN_PROGRESS').count(),
    }
    
    if stats['total_checks'] > 0:
        stats['pass_rate'] = (stats['passed_checks'] / stats['total_checks']) * 100
    else:
        stats['pass_rate'] = 0
    
    context = {
        'quality_steps': quality_steps,
        'status_choices': WorkflowStep.Status.choices,
        'aircraft_types': Aircraft.objects.all(),
        'stats': stats,
        'selected_status': status_filter,
        'selected_date_from': date_from,
        'selected_date_to': date_to,
        'selected_aircraft_type': aircraft_type
    }
    return render(request, 'assembly/quality_checks.html', context)

@login_required
def team_statistics(request):
    """Display team statistics"""
    # Date filters
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    
    # Base queries
    parts_query = Part.objects.all()
    workflow_query = WorkflowStep.objects.all()
    
    # Apply date filters if provided
    if date_from:
        try:
            date_from = datetime.strptime(date_from, '%Y-%m-%d')
            parts_query = parts_query.filter(created_at__gte=date_from)
            workflow_query = workflow_query.filter(created_at__gte=date_from)
        except ValueError:
            messages.error(request, 'Geçersiz başlangıç tarihi formatı')
            
    if date_to:
        try:
            date_to = datetime.strptime(date_to, '%Y-%m-%d')
            parts_query = parts_query.filter(created_at__lte=date_to)
            workflow_query = workflow_query.filter(created_at__lte=date_to)
        except ValueError:
            messages.error(request, 'Geçersiz bitiş tarihi formatı')
    
    # Get all teams
    teams = Team.objects.all()
    
    # Statistics for each team
    team_stats = []
    for team in teams:
        # Part statistics
        team_parts = parts_query.filter(team=team)
        total_parts = team_parts.count()
        completed_parts = team_parts.filter(status='completed').count()
        in_production = team_parts.filter(status='in_production').count()
        quality_passed = team_parts.filter(quality_check_status='passed').count()
        
        # Calculate completion rate
        completion_rate = (completed_parts / total_parts * 100) if total_parts > 0 else 0
        
        # Calculate quality rate
        quality_rate = (quality_passed / completed_parts * 100) if completed_parts > 0 else 0
        
        # Workflow statistics (only for assembly team)
        if team.team_type == 'assembly':
            team_workflows = workflow_query.filter(assigned_team=team)
            total_workflows = team_workflows.count()
            completed_workflows = team_workflows.filter(status='completed').count()
            in_progress = team_workflows.filter(status='in_progress').count()
            workflow_completion_rate = (completed_workflows / total_workflows * 100) if total_workflows > 0 else 0
            
            # Get aircraft distribution from assembled aircraft
            aircraft_distribution = {}
            assembled_aircraft = AssembledAircraft.objects.filter(
                workflow_steps__in=team_workflows
            ).distinct()
            
            for aircraft in assembled_aircraft:
                aircraft_type = aircraft.get_aircraft_type_display()
                if aircraft_type not in aircraft_distribution:
                    aircraft_distribution[aircraft_type] = 0
                aircraft_distribution[aircraft_type] += 1
        else:
            total_workflows = 0
            completed_workflows = 0
            in_progress = 0
            workflow_completion_rate = 0
            
            # Get aircraft distribution from parts
            aircraft_distribution = {}
            for aircraft_type, name in Aircraft.AIRCRAFT_TYPES:
                count = team_parts.filter(aircraft_type=aircraft_type).count()
                if count > 0:
                    aircraft_distribution[name] = count
        
        team_stats.append({
            'team': team,
            'total_parts': total_parts,
            'completed_parts': completed_parts,
            'in_production': in_production,
            'quality_passed': quality_passed,
            'completion_rate': round(completion_rate, 1),
            'quality_rate': round(quality_rate, 1),
            'total_workflows': total_workflows,
            'completed_workflows': completed_workflows,
            'in_progress': in_progress,
            'workflow_completion_rate': round(workflow_completion_rate, 1),
            'aircraft_distribution': aircraft_distribution
        })
    
    context = {
        'team_stats': team_stats,
        'date_from': date_from.strftime('%Y-%m-%d') if date_from else '',
        'date_to': date_to.strftime('%Y-%m-%d') if date_to else ''
    }
    
    return render(request, 'assembly/team_statistics.html', context)

class AssemblyTeamRequired(permissions.BasePermission):
    """
    Custom permission to only allow assembly team members to access/modify.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.profile.team and
            request.user.profile.team.team_type == 'assembly'
        )

class WorkflowStepViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing workflow steps.
    """
    queryset = WorkflowStep.objects.all()
    serializer_class = WorkflowStepSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'step_type', 'assigned_team', 'assigned_user']
    search_fields = ['notes']
    ordering_fields = ['created_at', 'started_at', 'completed_at']

    def get_queryset(self):
        """Filter steps based on user's team"""
        user = self.request.user
        if not hasattr(user, 'profile') or not user.profile.team:
            return WorkflowStep.objects.none()
        
        # Assembly team can see all steps
        if user.profile.team.team_type == 'assembly':
            return WorkflowStep.objects.all()
        
        # Other teams can only see their assigned steps
        return WorkflowStep.objects.filter(assigned_team=user.profile.team)

    @action(detail=True, methods=['post'])
    def start(self, request, pk=None):
        """Start a workflow step"""
        step = self.get_object()
        
        try:
            step.start(request.user)
            return Response(self.get_serializer(step).data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Complete a workflow step"""
        step = self.get_object()
        success = request.data.get('success', True)
        
        try:
            step.complete(success=success)
            return Response(self.get_serializer(step).data)
        except ValidationError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'])
    def add_note(self, request, pk=None):
        """Add a note to the workflow step"""
        step = self.get_object()
        note = request.data.get('note')
        
        if not note:
            return Response(
                {'error': 'Not alanı boş olamaz'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        step.notes = f"{step.notes}\n{timezone.now().strftime('%Y-%m-%d %H:%M:%S')}: {note}".strip()
        step.save()
        
        return Response(self.get_serializer(step).data)

class AssembledAircraftViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing assembled aircraft.
    """
    queryset = AssembledAircraft.objects.all()
    serializer_class = AssembledAircraftSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['status', 'assembly_team']
    search_fields = ['aircraft_type__name']
    ordering_fields = ['created_at', 'updated_at']

    @transaction.atomic
    def perform_create(self, serializer):
        """Create assembled aircraft and initialize workflow steps"""
        aircraft = serializer.save()
        
        # Create workflow steps in sequence
        steps = [
            ('WING_PRODUCTION', 'wing'),
            ('FUSELAGE_PRODUCTION', 'fuselage'),
            ('TAIL_PRODUCTION', 'tail'),
            ('AVIONICS_PRODUCTION', 'avionics'),
            ('QUALITY_CHECK', 'assembly'),
            ('ASSEMBLY', 'assembly'),
            ('TESTING', 'assembly'),
            ('FINAL_CHECK', 'assembly'),
        ]
        
        for step_type, team_type in steps:
            team = Team.objects.filter(team_type=team_type).first()
            if team:
                WorkflowStep.objects.create(
                    assembled_aircraft=aircraft,
                    step_type=step_type,
                    assigned_team=team
                )

    @action(detail=True)
    def workflow_progress(self, request, pk=None):
        """Get workflow progress for an aircraft"""
        aircraft = self.get_object()
        steps = aircraft.workflow_steps.all()
        
        total_steps = steps.count()
        completed_steps = steps.filter(status=WorkflowStep.Status.COMPLETED).count()
        in_progress_steps = steps.filter(status=WorkflowStep.Status.IN_PROGRESS).count()
        failed_steps = steps.filter(status=WorkflowStep.Status.FAILED).count()
        
        # Get current active steps
        active_steps = steps.filter(
            Q(status=WorkflowStep.Status.IN_PROGRESS) |
            Q(status=WorkflowStep.Status.PENDING)
        ).order_by('created_at')
        
        # Find next available step
        next_step = None
        for step in active_steps:
            if step.can_start():
                next_step = step
                break
        
        return Response({
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'in_progress_steps': in_progress_steps,
            'failed_steps': failed_steps,
            'completion_percentage': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'current_steps': WorkflowStepSerializer(
                active_steps,
                many=True
            ).data,
            'next_step': WorkflowStepSerializer(next_step).data if next_step else None,
            'status': aircraft.status
        })

    @action(detail=True, methods=['post'])
    def finalize_assembly(self, request, pk=None):
        """
        Finalize aircraft assembly after all steps are completed
        Only assembly team can perform this action
        """
        if not request.user.profile.team or request.user.profile.team.team_type != 'assembly':
            return Response(
                {'error': 'Only assembly team can finalize assembly'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        aircraft = self.get_object()
        steps = aircraft.workflow_steps.all()
        
        # Check if all steps are completed
        if not all(step.status == WorkflowStep.Status.COMPLETED for step in steps):
            return Response(
                {'error': 'All workflow steps must be completed before finalizing assembly'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Update aircraft status
        aircraft.status = AssembledAircraft.Status.COMPLETED
        aircraft.save()
        
        # Mark all parts as used
        aircraft.parts.all().update(is_used=True)
        
        return Response(self.get_serializer(aircraft).data)

    @action(detail=False, methods=['get'])
    def available_parts(self, request):
        """Get a list of available parts for assembly"""
        aircraft_type = request.query_params.get('aircraft_type')
        if not aircraft_type:
            return Response(
                {'error': 'aircraft_type parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        parts = {}
        for part_type in Part.PartType.values:
            parts[part_type] = Part.objects.filter(
                aircraft_type=aircraft_type,
                part_type=part_type,
                is_used=False
            ).count()

        return Response(parts)

    @action(detail=False, methods=['get'])
    def assembly_statistics(self, request):
        """Get assembly statistics"""
        stats = {
            'total_assembled': self.get_queryset().count(),
            'by_status': self.get_queryset().values(
                'status'
            ).annotate(count=Count('id')),
            'by_aircraft_type': self.get_queryset().values(
                'aircraft_type__aircraft_type'
            ).annotate(count=Count('id')),
            'recent_assemblies': self.get_queryset().order_by(
                '-created_at'
            )[:5].values(
                'id',
                'aircraft_type__aircraft_type',
                'status',
                'created_at'
            )
        }
        
        return Response(stats)

    @action(detail=True)
    def part_details(self, request, pk=None):
        """Get detailed information about parts used in an assembled aircraft"""
        aircraft = self.get_object()
        parts = aircraft.parts.all()
        
        details = {}
        for part in parts:
            details[part.get_part_type_display()] = {
                'id': part.id,
                'serial_number': part.serial_number,
                'part_type': part.get_part_type_display(),
                'produced_by': part.team.name,
                'production_date': part.created_at,
                'quality_check_passed': part.quality_check_passed,
                'quality_notes': part.quality_notes
            }
        
        return Response(details)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def available_parts(request):
    """Get available parts for assembly based on aircraft type"""
    aircraft_type = request.GET.get('aircraft_type')
    if not aircraft_type:
        return Response({'error': 'Aircraft type is required'}, status=400)
        
    # Get unused parts for the specified aircraft type
    parts = Part.objects.filter(
        aircraft_type=aircraft_type,
        is_used=False,
        status='completed',
        quality_check_status='passed'
    ).select_related('team')
    
    # Group parts by type
    parts_by_type = {}
    for part in parts:
        part_type = part.get_part_type_display()
        if part_type not in parts_by_type:
            parts_by_type[part_type] = []
            
        parts_by_type[part_type].append({
            'id': part.id,
            'name': part.name,
            'serial_number': part.serial_number,
            'team': part.team.name if part.team else None,
            'created_at': part.created_at.strftime('%Y-%m-%d %H:%M')
        })
    
    return Response(parts_by_type)
