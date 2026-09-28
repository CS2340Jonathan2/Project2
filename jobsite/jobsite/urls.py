from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('profile/', include('profiles.urls')),
    path('jobs/', include('jobs.urls')),
    path('cart/', include('cart.urls')),
]
