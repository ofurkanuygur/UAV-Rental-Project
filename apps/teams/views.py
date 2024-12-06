from rest_framework import viewsets, permissions
from .models import Team
from .serializers import TeamSerializer

class TeamViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing teams.
    Provides CRUD operations for teams.
    """
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """
        Optionally restricts the returned teams by filtering against
        a `team_type` query parameter in the URL.
        """
        queryset = Team.objects.all()
        team_type = self.request.query_params.get('team_type', None)
        if team_type is not None:
            queryset = queryset.filter(team_type=team_type)
        return queryset
