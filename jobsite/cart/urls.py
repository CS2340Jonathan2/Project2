from django.urls import path
from . import views
urlpatterns = [
    path('<int:id>/add/', views.add, name='cart.add'),
    path('confirm/', views.confirm, name='cart.confirm'),
    path('', views.index, name='cart.index'),
]