from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.parts.models import Aircraft, Part
from apps.teams.models import Team
from apps.accounts.models import User
from django.utils import timezone

class AssembledAircraft(models.Model):
    """Model for assembled aircraft"""
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')

    name = models.CharField(max_length=100, default='Unnamed Aircraft')
    aircraft_type = models.CharField(
        max_length=20,
        choices=Aircraft.AIRCRAFT_TYPES,
        verbose_name=_('Aircraft Type'),
        default='tb2'
    )
    description = models.TextField(blank=True)
    parts = models.ManyToManyField(
        Part,
        related_name='assembled_in',
        verbose_name=_('Used Parts')
    )
    assembly_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        related_name='assembled_aircraft',
        verbose_name=_('Assembly Team')
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_aircraft_type_display()} - {self.name}"

    def get_status_badge_color(self):
        """Get the Bootstrap color class for the status badge"""
        return {
            self.Status.PENDING: 'warning text-dark',
            self.Status.IN_PROGRESS: 'primary',
            self.Status.COMPLETED: 'success',
            self.Status.FAILED: 'danger',
        }.get(self.status, 'secondary')

    def update_status(self):
        """Update aircraft status based on workflow steps"""
        steps = self.workflow_steps.all()
        if not steps.exists():
            return

        if steps.filter(status=WorkflowStep.Status.FAILED).exists():
            self.status = self.Status.FAILED
        elif steps.filter(status=WorkflowStep.Status.IN_PROGRESS).exists():
            self.status = self.Status.IN_PROGRESS
        elif steps.filter(status=WorkflowStep.Status.PENDING).exists():
            self.status = self.Status.IN_PROGRESS
        else:
            # All steps are completed
            self.status = self.Status.COMPLETED
        
        self.save()

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

    def get_status_badge_color(self):
        """Get the Bootstrap color class for the status badge"""
        return {
            self.Status.PENDING: 'warning text-dark',
            self.Status.IN_PROGRESS: 'primary',
            self.Status.COMPLETED: 'success',
            self.Status.FAILED: 'danger',
            self.Status.BLOCKED: 'secondary',
        }.get(self.status, 'secondary')

    def get_previous_step(self):
        """Get the previous step in the workflow sequence"""
        step_order = list(self.StepType.values)
        current_index = step_order.index(self.step_type)
        if current_index > 0:
            previous_type = step_order[current_index - 1]
            return self.assembled_aircraft.workflow_steps.filter(
                step_type=previous_type
            ).first()
        return None

    def can_start(self):
        """Check if this step can be started"""
        previous_step = self.get_previous_step()
        if previous_step:
            return previous_step.status == self.Status.COMPLETED
        return True

    def validate_start(self):
        """Validate if the step can be started"""
        if not self.can_start():
            raise ValidationError(
                "Previous step must be completed before starting this step"
            )
        if self.status != self.Status.PENDING:
            raise ValidationError(
                "Only pending steps can be started"
            )

    def validate_complete(self):
        """Validate if the step can be completed"""
        if self.status != self.Status.IN_PROGRESS:
            raise ValidationError(
                "Only in-progress steps can be completed"
            )

    def start(self, user):
        """Start the workflow step"""
        self.validate_start()
        self.status = self.Status.IN_PROGRESS
        self.assigned_user = user
        self.started_at = timezone.now()
        self.save()
        self.assembled_aircraft.update_status()

    def complete(self, success=True):
        """Complete the workflow step"""
        self.validate_complete()
        self.status = self.Status.COMPLETED if success else self.Status.FAILED
        self.completed_at = timezone.now()
        self.save()
        self.assembled_aircraft.update_status()

    class Meta:
        verbose_name = _('Workflow Step')
        verbose_name_plural = _('Workflow Steps')
        ordering = ['created_at']
