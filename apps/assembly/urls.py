from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssembledAircraftViewSet

router = DefaultRouter()
router.register(r'aircraft', AssembledAircraftViewSet, basename='assembled-aircraft')

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
]
