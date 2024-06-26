from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = (
            'username',
            'organization',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2'
        )


class CustomUserEditForm(UserChangeForm):
    class Meta:
        model = User
        fields = (
            'username',
            'organization',
            'email',
            'first_name',
            'last_name',
            'password'
        )
