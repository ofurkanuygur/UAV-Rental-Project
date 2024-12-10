from django.db import models

class Team(models.Model):
    TEAM_TYPES = (
        ('wing', 'Wing Team'),
        ('fuselage', 'Fuselage Team'),
        ('tail', 'Tail Team'),
        ('avionics', 'Avionics Team'),
        ('assembly', 'Assembly Team'),
    )

    name = models.CharField(max_length=100)
    team_type = models.CharField(max_length=20, choices=TEAM_TYPES)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
