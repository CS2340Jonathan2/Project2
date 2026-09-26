from django.urls import path

from . import views

app_name = 'jobs'

urlpatterns = [
    path('map/', views.job_map, name='map'),
    path('map-data/', views.map_data, name='map_data'),
]
