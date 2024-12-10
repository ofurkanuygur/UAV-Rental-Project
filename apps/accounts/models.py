from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.teams.models import Team

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='team_members')
    phone = models.CharField(max_length=20, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def can_manage_wings(self):
        return self.team and self.team.name.lower() == 'wing team'

    def can_manage_fuselage(self):
        return self.team and self.team.name.lower() == 'fuselage team'

    def can_manage_tail(self):
        return self.team and self.team.name.lower() == 'tail team'

    def can_manage_avionics(self):
        return self.team and self.team.name.lower() == 'avionics team'

    def can_manage_assembly(self):
        return self.team and self.team.name.lower() == 'assembly team'

    def can_view_part(self, part):
        """Check if user can view a specific part based on their team"""
        if not self.team:
            return False
        
        if self.team.name.lower() == 'assembly team':
            return True  # Assembly team can view all parts
            
        part_type = part.part_type.lower() if hasattr(part, 'part_type') else ''
        team_name = self.team.name.lower()
        
        return (
            (team_name == 'wing team' and 'wing' in part_type) or
            (team_name == 'fuselage team' and 'fuselage' in part_type) or
            (team_name == 'tail team' and 'tail' in part_type) or
            (team_name == 'avionics team' and 'avionics' in part_type)
        )

    def can_edit_part(self, part):
        """Check if user can edit a specific part based on their team"""
        if not self.team:
            return False
            
        if self.team.name.lower() == 'assembly team':
            return False  # Assembly team can't edit parts
            
        part_type = part.part_type.lower() if hasattr(part, 'part_type') else ''
        team_name = self.team.name.lower()
        
        return (
            (team_name == 'wing team' and 'wing' in part_type) or
            (team_name == 'fuselage team' and 'fuselage' in part_type) or
            (team_name == 'tail team' and 'tail' in part_type) or
            (team_name == 'avionics team' and 'avionics' in part_type)
        )

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile instance for all newly created User instances."""
    if created:
        Profile.objects.create(user=instance)
