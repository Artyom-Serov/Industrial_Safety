from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Organization


class CustomUserCreationForm(UserCreationForm):
    new_organization = forms.CharField(
        max_length=255, required=False, label='Новая организация'
    )

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

    def save(self, commit=True):
        user = super().save(commit=False)
        new_organization = self.cleaned_data.get('new_organization')
        if new_organization:
            organization, created = Organization.objects.get_or_create(
                name=new_organization
            )
            user.organization = organization
        if commit:
            user.save()
        return user


class CustomUserEditForm(forms.ModelForm):
    password1 = forms.CharField(
        label='При необходимости смены пароля, укажите его',
        required=False, widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Введите новый пароль повторно',
        required=False, widget=forms.PasswordInput
    )
    new_organization = forms.CharField(
        max_length=255, required=False, label='Новая организация'
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'organization',
            'new_organization',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['organization'].required = False
        self.fields['organization'].label = \
            "Наименование организации (если выбрано)"

    def save(self, commit=True):
        user = super().save(commit=False)
        new_organization = self.cleaned_data.get('new_organization')
        if new_organization:
            organization, created = Organization.objects.get_or_create(
                name=new_organization
            )
            user.organization = organization
        if commit:
            user.save()
        return user
