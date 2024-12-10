from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'assembly'

router = DefaultRouter()
router.register(r'aircraft', views.AssembledAircraftViewSet, basename='assembled-aircraft')
router.register(r'workflow', views.WorkflowStepViewSet, basename='workflow-step')

urlpatterns = [
    # Frontend Views
    path('', views.workflow_list, name='workflow_list'),
    path('workflow/<int:pk>/', views.workflow_detail, name='workflow_detail'),
    path('create/', views.create_aircraft, name='create_aircraft'),
    path('quality-checks/', views.quality_checks, name='quality_checks'),
    path('statistics/', views.team_statistics, name='team_statistics'),
    path('api/available-parts/', views.available_parts, name='available_parts'),
    
    # API endpoints
    path('api/', include(router.urls)),
]
