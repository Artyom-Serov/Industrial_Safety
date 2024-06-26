from django import forms
from django.contrib.auth.forms import UserCreationForm
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


class CustomUserEditForm(forms.ModelForm):
    password1 = forms.CharField(
        label='При необходимости смены пароля, укажите его',
        required=False, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Введите новый пароль повторно', required=False, widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = (
            'username',
            'organization',
            'email',
            'first_name',
            'last_name'
        )

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password1 != password2:
            self.add_error('password2', "Пароли должны совпадать.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password1")
        if password:
            user.set_password(password)
        if commit:
            user.save()
        return user
