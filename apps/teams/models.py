from django.db import models
from django.utils.translation import gettext_lazy as _

class Team(models.Model):
    class TeamType(models.TextChoices):
        WING = 'WING', _('Wing Team')
        FUSELAGE = 'FUSELAGE', _('Fuselage Team')
        TAIL = 'TAIL', _('Tail Team')
        AVIONICS = 'AVIONICS', _('Avionics Team')
        ASSEMBLY = 'ASSEMBLY', _('Assembly Team')
    
    name = models.CharField(max_length=100)
    team_type = models.CharField(
        max_length=20,
        choices=TeamType.choices,
        default=TeamType.WING
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_team_type_display()}"

    class Meta:
        verbose_name = _('Team')
        verbose_name_plural = _('Teams')
        ordering = ['name']
