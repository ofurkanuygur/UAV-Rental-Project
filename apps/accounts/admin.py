from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Profile

User = get_user_model()

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_team', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('username',)

    def get_team(self, obj):
        return obj.profile.team.name if obj.profile and obj.profile.team else '-'
    get_team.short_description = 'Team'

# Only register if User is not already registered
if not admin.site._registry.get(User):
    admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'team', 'created_at', 'updated_at')
    list_filter = ('team',)
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)
