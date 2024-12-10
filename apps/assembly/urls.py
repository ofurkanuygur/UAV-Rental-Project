from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssembledAircraftViewSet, WorkflowStepViewSet

router = DefaultRouter()
router.register(r'aircraft', AssembledAircraftViewSet, basename='assembled-aircraft')
router.register(r'workflow', WorkflowStepViewSet, basename='workflow-step')

# URL patterns for assembly management
urlpatterns = [
    # Router URLs
    path('', include(router.urls)),
    
    # Additional endpoints
    path('available-parts/', 
         AssembledAircraftViewSet.as_view({'get': 'available_parts'}), 
         name='available-parts'),
    
    path('statistics/', 
         AssembledAircraftViewSet.as_view({'get': 'assembly_statistics'}), 
         name='assembly-statistics'),
    
    path('inventory-check/', 
         AssembledAircraftViewSet.as_view({'get': 'inventory_check'}), 
         name='inventory-check'),
    
    path('aircraft/<int:pk>/part-details/', 
         AssembledAircraftViewSet.as_view({'get': 'part_details'}), 
         name='part-details'),
    
    # Aircraft workflow steps
    path('aircraft/<int:pk>/workflow-progress/',
         AssembledAircraftViewSet.as_view({'get': 'workflow_progress'}),
         name='workflow-progress'),
         
    # Workflow step actions
    path('workflow/<int:pk>/start/',
         WorkflowStepViewSet.as_view({'post': 'start_step'}),
         name='start-step'),
         
    path('workflow/<int:pk>/complete/',
         WorkflowStepViewSet.as_view({'post': 'complete_step'}),
         name='complete-step'),
]
