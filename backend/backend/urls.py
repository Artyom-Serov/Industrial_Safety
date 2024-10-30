"""
URL configuration for backend project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path('users/', include('users.urls')),
    path('', include('facility.urls')),
    path('documents/', include('documents.urls')),
]
