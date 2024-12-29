from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('login/', views.user_login, name='login'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path(
        'profile/edit/<int:user_id>/',
        views.admin_edit_user_profile,
        name='edit_user_profile'
    ),
    path('register/', views.user_register, name='register'),
    path('logout/', views.user_logout, name='logout'),
]
