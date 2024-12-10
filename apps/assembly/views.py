from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from django.utils import timezone
from django.db import transaction
from .models import AssembledAircraft, WorkflowStep
from .serializers import AssembledAircraftSerializer, WorkflowStepSerializer
from apps.parts.models import Part, Aircraft
from apps.teams.models import Team

class AssemblyTeamRequired(permissions.BasePermission):
    """
    Custom permission to only allow assembly team members to access/modify.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.profile.team and
            request.user.profile.team.team_type == 'ASSEMBLY'
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
        if user.profile.team.team_type == Team.TeamType.ASSEMBLY:
            return WorkflowStep.objects.all()
        
        # Other teams can only see their assigned steps
        return WorkflowStep.objects.filter(assigned_team=user.profile.team)

    @action(detail=True, methods=['post'])
    def start_step(self, request, pk=None):
        """Start a workflow step"""
        step = self.get_object()
        
        if step.status != WorkflowStep.Status.PENDING:
            return Response(
                {'error': 'Step can only be started when pending'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        step.status = WorkflowStep.Status.IN_PROGRESS
        step.started_at = timezone.now()
        step.assigned_user = request.user
        step.save()
        
        return Response(self.get_serializer(step).data)

    @action(detail=True, methods=['post'])
    def complete_step(self, request, pk=None):
        """Complete a workflow step"""
        step = self.get_object()
        
        if step.status != WorkflowStep.Status.IN_PROGRESS:
            return Response(
                {'error': 'Step can only be completed when in progress'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        step.status = WorkflowStep.Status.COMPLETED
        step.completed_at = timezone.now()
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
            ('WING_PRODUCTION', Team.TeamType.WING),
            ('FUSELAGE_PRODUCTION', Team.TeamType.FUSELAGE),
            ('TAIL_PRODUCTION', Team.TeamType.TAIL),
            ('AVIONICS_PRODUCTION', Team.TeamType.AVIONICS),
            ('QUALITY_CHECK', Team.TeamType.ASSEMBLY),
            ('ASSEMBLY', Team.TeamType.ASSEMBLY),
            ('TESTING', Team.TeamType.ASSEMBLY),
            ('FINAL_CHECK', Team.TeamType.ASSEMBLY),
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
        
        return Response({
            'total_steps': total_steps,
            'completed_steps': completed_steps,
            'in_progress_steps': in_progress_steps,
            'completion_percentage': (completed_steps / total_steps * 100) if total_steps > 0 else 0,
            'current_steps': WorkflowStepSerializer(
                steps.filter(status=WorkflowStep.Status.IN_PROGRESS),
                many=True
            ).data
        })

    @action(detail=False, methods=['get'])
    def available_parts(self, request):
        """
        Get a list of available parts for assembly
        """
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
        """
        Get assembly statistics
        """
        # Get statistics by aircraft type
        stats = {
            'total_assembled': self.get_queryset().count(),
            'by_aircraft_type': self.get_queryset().values(
                'aircraft_type__aircraft_type'
            ).annotate(count=Count('id')),
            'recent_assemblies': self.get_queryset().order_by(
                '-assembly_date'
            )[:5].values('serial_number', 'aircraft_type__aircraft_type', 'assembly_date')
        }
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def inventory_check(self, request):
        """
        Check inventory status for all aircraft types
        """
        aircraft_types = Aircraft.objects.all()
        inventory_status = {}

        for aircraft in aircraft_types:
            parts_needed = {
                Part.PartType.WING: 1,
                Part.PartType.FUSELAGE: 1,
                Part.PartType.TAIL: 1,
                Part.PartType.AVIONICS: 1,
            }
            
            available_parts = {}
            missing_parts = []
            
            for part_type, count_needed in parts_needed.items():
                available_count = Part.objects.filter(
                    aircraft_type=aircraft,
                    part_type=part_type,
                    is_used=False
                ).count()
                
                available_parts[part_type] = available_count
                
                if available_count < count_needed:
                    missing_parts.append({
                        'part_type': part_type,
                        'available': available_count,
                        'needed': count_needed
                    })
            
            inventory_status[aircraft.aircraft_type] = {
                'can_assemble': len(missing_parts) == 0,
                'available_parts': available_parts,
                'missing_parts': missing_parts
            }
        
        return Response(inventory_status)

    @action(detail=True, methods=['get'])
    def part_details(self, request, pk=None):
        """
        Get detailed information about parts used in an assembled aircraft
        """
        aircraft = self.get_object()
        parts = {
            'wing': aircraft.wing,
            'fuselage': aircraft.fuselage,
            'tail': aircraft.tail,
            'avionics': aircraft.avionics
        }
        
        details = {}
        for part_name, part in parts.items():
            details[part_name] = {
                'serial_number': part.serial_number,
                'part_type': part.get_part_type_display(),
                'produced_by': part.team.name,
                'production_date': part.created_at
            }
        
        return Response(details)
