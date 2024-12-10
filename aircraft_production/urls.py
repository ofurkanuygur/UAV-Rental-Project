"""
URL configuration for aircraft_production project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from . import views

schema_view = get_schema_view(
    openapi.Info(
        title="UAV Production API",
        default_version='v1',
        description="API for managing UAV production process",
        terms_of_service="https://www.example.com/policies/terms/",
        contact=openapi.Contact(email="contact@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# Error handlers
handler404 = 'aircraft_production.views.custom_404'
handler500 = 'aircraft_production.views.custom_500'
handler403 = 'aircraft_production.views.custom_403'

urlpatterns = [
    # Admin interface
    path('admin/', admin.site.urls),
    
    # Frontend URLs
    path('', include('apps.accounts.urls')),  # Include accounts URLs at root
    path('teams/', include('apps.teams.urls', namespace='teams')),
    path('parts/', include('apps.parts.urls', namespace='parts')),
    path('assembly/', include('apps.assembly.urls', namespace='assembly')),
    
    # API Documentation
    path('swagger<format>/', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Serve media and static files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
