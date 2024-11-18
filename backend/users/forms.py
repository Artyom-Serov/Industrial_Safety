"""
Модуль форм для управления пользователями и организациями.
"""

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Organization


class CustomUserCreationForm(UserCreationForm):
    """
    Форма для создания нового пользователя, включая возможность выбора
    существующей или создания новой организации.
    """
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
        """
        Переопределение метода сохранения, позволяющее установить
        новую организацию, если она была введена.

        Параметры
            commit (bool): Указывает, сохранять ли объект в базе данных.

        Возвращает:
            User: Созданный или обновленный пользователь.
        """
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
    """
    Форма для редактирования данных пользователя, включая возможность
    изменения пароля и добавления новой организации.
    """
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
        """
        Инициализация формы с отключением обязательности выбора организации,
        если она не указана.
        """
        super().__init__(*args, **kwargs)
        self.fields['organization'].required = False
        self.fields['organization'].label = ("Наименование организации"
                                             "(если выбрано)")

    def clean(self):
        """Проверка совпадения паролей."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get("password1")
        password2 = cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            self.add_error('password2', "Пароли не совпадают.")

        return cleaned_data

    def save(self, commit=True):
        """
        Переопределение метода сохранения для добавления новой организации,
        если она была введена, и сохранения данных пользователя.

        Параметры:
            commit (bool): Указывает, сохранять ли объект в базе данных.

        Возвращает:
            User: Обновленный пользователь.
        """
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
