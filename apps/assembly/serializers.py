from rest_framework import serializers
from apps.parts.models import Aircraft, Part
from apps.teams.models import Team
from .models import AssembledAircraft

class AssembledAircraftSerializer(serializers.ModelSerializer):
    aircraft_type = serializers.PrimaryKeyRelatedField(
        queryset=Aircraft.objects.all(),
        required=True
    )
    assembly_team = serializers.PrimaryKeyRelatedField(
        queryset=Team.objects.all(),
        required=True
    )
    parts = serializers.PrimaryKeyRelatedField(
        queryset=Part.objects.all(),
        many=True,
        required=True
    )

    class Meta:
        model = AssembledAircraft
        fields = ['id', 'aircraft_type', 'assembly_team', 'parts', 'status', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at', 'status']
