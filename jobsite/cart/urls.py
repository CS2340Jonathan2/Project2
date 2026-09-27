from django.urls import path

from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_list, name='cart_list'),
    path('add/<int:job_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:job_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('apply/<int:job_id>/', views.apply_to_job, name='apply_to_job'),
    path('applications/', views.application_list, name='application_list'),
]