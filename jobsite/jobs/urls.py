from django.urls import path
from . import views

app_name = 'jobs'

urlpatterns = [
    path('search/', views.search, name='search'),
    path('recommendations/', views.job_recommendations, name='recommendations'),
    path('map/', views.job_map, name='map'),
    path('map-data/', views.map_data, name='map_data'),
    path('<int:job_id>/apply/', views.apply, name='apply'),
]
