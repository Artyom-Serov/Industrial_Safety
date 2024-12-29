"""
Модуль администрирования для управления моделями User и Organization
в интерфейсе Django Admin.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import Organization, User


class CustomUserAdmin(UserAdmin):
    """
    Класс для настройки модели User в админ-панели.

    Предоставляет настраиваемое отображение модели User в админ-панели Django,
    включая поля, фильтры и параметры поиска.

    Атрибуты:
        add_form (ModelForm): Форма для создания нового пользователя.
        form (ModelForm): Форма для редактирования существующего пользователя.
        model (Model): Модель User, регистрируемая с данной конфигурацией.
        list_display (tuple): Поля для отображения в списке пользователей.
        list_filter (tuple): Поля для фильтрации в списке пользователей.
        fieldsets (tuple): Разметка полей для детального просмотра
            пользователя.
        add_fieldsets (tuple): Разметка полей для формы создания пользователя.
        search_fields (tuple): Поля для поиска пользователей в админ-панели.
        ordering (tuple): Сортировка списка пользователей по умолчанию.
    """
    add_form = CustomUserCreationForm
    form = CustomUserEditForm
    model = User
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'organization',
        'is_staff',
        'is_active'
    )
    list_filter = ('is_staff', 'is_active', 'organization')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Информация о пользователе', {'fields': (
            'first_name', 'last_name', 'email', 'organization'
        )}),
        ('Права доступа', {'fields': (
            'is_staff', 'is_active', 'groups', 'user_permissions'
        )}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username', 'email', 'first_name', 'last_name',
                'organization', 'password1', 'password2', 'is_staff',
                'is_active'
            )}
         ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)


class OrganizationAdmin(admin.ModelAdmin):
    """
    Класс для настройки модели Organization в админ-панели.

    Атрибуты:
        list_display (tuple): Поля для отображения в списке организаций.
        search_fields (tuple): Поля для поиска организаций в админ-панели.
        ordering (tuple): Сортировка списка организаций по умолчанию.
    """
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
