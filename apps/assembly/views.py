from rest_framework import viewsets, permissions, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Count, Q
from .models import AssembledAircraft
from .serializers import AssembledAircraftSerializer
from apps.parts.models import Part, Aircraft

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

class AssembledAircraftViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing assembled aircraft.
    Only assembly team members can create/modify aircraft.
    """
    queryset = AssembledAircraft.objects.all()
    serializer_class = AssembledAircraftSerializer
    permission_classes = [permissions.IsAuthenticated, AssemblyTeamRequired]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['serial_number']
    filterset_fields = ['aircraft_type', 'assembly_team']
    ordering_fields = ['assembly_date', 'serial_number']

    def perform_create(self, serializer):
        """
        Set the assembly team automatically based on the user's team
        """
        serializer.save(assembly_team=self.request.user.profile.team)

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
