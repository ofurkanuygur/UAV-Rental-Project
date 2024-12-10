from rest_framework import serializers
from apps.parts.models import Aircraft, Part
from apps.teams.models import Team
from apps.accounts.models import User
from .models import AssembledAircraft, WorkflowStep

class WorkflowStepSerializer(serializers.ModelSerializer):
    step_type_display = serializers.CharField(source='get_step_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    assigned_user_name = serializers.CharField(source='assigned_user.get_full_name', read_only=True)
    assigned_team_name = serializers.CharField(source='assigned_team.name', read_only=True)

    class Meta:
        model = WorkflowStep
        fields = [
            'id', 'assembled_aircraft', 'step_type', 'step_type_display',
            'status', 'status_display', 'assigned_team', 'assigned_team_name',
            'assigned_user', 'assigned_user_name', 'notes', 'started_at',
            'completed_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

class AssembledAircraftSerializer(serializers.ModelSerializer):
    workflow_steps = WorkflowStepSerializer(many=True, read_only=True)
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
        fields = [
            'id', 'aircraft_type', 'assembly_team', 'parts',
            'status', 'workflow_steps', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'status']
