from django.urls import path

from .views import (AdminDeleteUserView, AdminEditUserProfileView,
                    EditProfileView, UserLoginView, UserLogoutView,
                    UserProfileView, UserRegisterView)

app_name = 'users'

urlpatterns = [
    path('login/', UserLoginView.as_view(), name='login'),
    path('profile/', UserProfileView.as_view(), name='profile'),
    path('profile/edit/', EditProfileView.as_view(), name='edit_profile'),
    path(
        'profile/edit/<int:user_id>/',
        AdminEditUserProfileView.as_view(),
        name='edit_user_profile'
    ),
    path(
        'profile/delete/<int:user_id>/',
        AdminDeleteUserView.as_view(),
        name='delete_user'
    ),
    path('register/', UserRegisterView.as_view(), name='register'),
    path('logout/', UserLogoutView.as_view(), name='logout'),
]
