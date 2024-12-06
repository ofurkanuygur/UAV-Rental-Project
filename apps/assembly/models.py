from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from apps.parts.models import Aircraft, Part
from apps.teams.models import Team

class AssembledAircraft(models.Model):
    aircraft_type = models.ForeignKey(
        Aircraft,
        on_delete=models.PROTECT,
        related_name='assembled_aircraft'
    )
    wing = models.OneToOneField(
        Part,
        on_delete=models.PROTECT,
        related_name='assembled_as_wing',
        limit_choices_to={'part_type': Part.PartType.WING, 'is_used': False}
    )
    fuselage = models.OneToOneField(
        Part,
        on_delete=models.PROTECT,
        related_name='assembled_as_fuselage',
        limit_choices_to={'part_type': Part.PartType.FUSELAGE, 'is_used': False}
    )
    tail = models.OneToOneField(
        Part,
        on_delete=models.PROTECT,
        related_name='assembled_as_tail',
        limit_choices_to={'part_type': Part.PartType.TAIL, 'is_used': False}
    )
    avionics = models.OneToOneField(
        Part,
        on_delete=models.PROTECT,
        related_name='assembled_as_avionics',
        limit_choices_to={'part_type': Part.PartType.AVIONICS, 'is_used': False}
    )
    assembly_team = models.ForeignKey(
        Team,
        on_delete=models.PROTECT,
        limit_choices_to={'team_type': Team.TeamType.ASSEMBLY}
    )
    serial_number = models.CharField(max_length=100, unique=True)
    assembly_date = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    def clean(self):
        # Validate all parts belong to the same aircraft type
        parts = [self.wing, self.fuselage, self.tail, self.avionics]
        for part in parts:
            if part and part.aircraft_type != self.aircraft_type:
                raise ValidationError(
                    _(f'{part.get_part_type_display()} part is not compatible with {self.aircraft_type} aircraft.')
                )
            if part and part.is_used:
                raise ValidationError(
                    _(f'{part.get_part_type_display()} part is already used in another aircraft.')
                )

    def save(self, *args, **kwargs):
        # Mark all parts as used
        parts = [self.wing, self.fuselage, self.tail, self.avionics]
        for part in parts:
            if part:
                part.is_used = True
                part.save()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.aircraft_type} - {self.serial_number}"

    class Meta:
        verbose_name = _('Assembled Aircraft')
        verbose_name_plural = _('Assembled Aircraft')
        ordering = ['-assembly_date']
