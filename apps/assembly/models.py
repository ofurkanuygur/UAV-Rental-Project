from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.parts.models import Aircraft, Part
from apps.teams.models import Team

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
