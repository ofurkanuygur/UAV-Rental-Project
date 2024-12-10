from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.parts.models import Aircraft, Part
from apps.teams.models import Team
from apps.accounts.models import User

class AssembledAircraft(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    aircraft_type = models.ForeignKey(
        Aircraft,
        on_delete=models.PROTECT,
        related_name='assembled_aircraft'
    )
    assembly_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='assembled_aircraft'
    )
    parts = models.ManyToManyField(
        Part,
        related_name='assembled_in'
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.aircraft_type} - {self.status}"

    class Meta:
        verbose_name = _('Assembled Aircraft')
        verbose_name_plural = _('Assembled Aircraft')
        ordering = ['-created_at']

class WorkflowStep(models.Model):
    class StepType(models.TextChoices):
        WING_PRODUCTION = 'WING_PRODUCTION', _('Wing Production')
        FUSELAGE_PRODUCTION = 'FUSELAGE_PRODUCTION', _('Fuselage Production')
        TAIL_PRODUCTION = 'TAIL_PRODUCTION', _('Tail Production')
        AVIONICS_PRODUCTION = 'AVIONICS_PRODUCTION', _('Avionics Production')
        QUALITY_CHECK = 'QUALITY_CHECK', _('Quality Check')
        ASSEMBLY = 'ASSEMBLY', _('Assembly')
        TESTING = 'TESTING', _('Testing')
        FINAL_CHECK = 'FINAL_CHECK', _('Final Check')

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        BLOCKED = 'BLOCKED', _('Blocked')

    assembled_aircraft = models.ForeignKey(
        AssembledAircraft,
        on_delete=models.CASCADE,
        related_name='workflow_steps'
    )
    step_type = models.CharField(
        max_length=50,
        choices=StepType.choices
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    assigned_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='assigned_steps'
    )
    assigned_user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_steps'
    )
    notes = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_step_type_display()} - {self.get_status_display()}"

    class Meta:
        verbose_name = _('Workflow Step')
        verbose_name_plural = _('Workflow Steps')
        ordering = ['created_at']
