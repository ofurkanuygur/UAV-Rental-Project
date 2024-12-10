from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model"""
    email = models.EmailField(_('email address'), unique=True)
    
    # Add related_name to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_user_set',
        related_query_name='custom_user',
    )
    
    def __str__(self):
        return self.get_full_name() or self.username

class Profile(models.Model):
    """User profile model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    team = models.ForeignKey(
        'teams.Team',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='team_members'
    )
    phone = models.CharField(max_length=15, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_image = models.ImageField(
        upload_to='profile_images/',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()}'s Profile"

    def can_manage_wings(self):
        return self.team and self.team.team_type == 'wing'

    def can_manage_fuselage(self):
        return self.team and self.team.team_type == 'fuselage'

    def can_manage_tail(self):
        return self.team and self.team.team_type == 'tail'

    def can_manage_avionics(self):
        return self.team and self.team.team_type == 'avionics'

    def can_manage_assembly(self):
        return self.team and self.team.team_type == 'assembly'

    def can_view_part(self, part):
        """Check if user can view a specific part based on their team"""
        if not self.team:
            return False
        
        if self.team.team_type == 'assembly':
            return True  # Assembly team can view all parts
            
        part_type = part.part_type.lower() if hasattr(part, 'part_type') else ''
        team_type = self.team.team_type
        
        return (
            (team_type == 'wing' and 'wing' in part_type) or
            (team_type == 'fuselage' and 'fuselage' in part_type) or
            (team_type == 'tail' and 'tail' in part_type) or
            (team_type == 'avionics' and 'avionics' in part_type)
        )

    def can_edit_part(self, part):
        """Check if user can edit a specific part based on their team"""
        if not self.team:
            return False
            
        if self.team.team_type == 'assembly':
            return False  # Assembly team can't edit parts
            
        part_type = part.part_type.lower() if hasattr(part, 'part_type') else ''
        team_type = self.team.team_type
        
        return (
            (team_type == 'wing' and 'wing' in part_type) or
            (team_type == 'fuselage' and 'fuselage' in part_type) or
            (team_type == 'tail' and 'tail' in part_type) or
            (team_type == 'avionics' and 'avionics' in part_type)
        )

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')
