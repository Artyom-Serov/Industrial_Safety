from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Organization
from .forms import CustomUserEditForm, CustomUserCreationForm


class CustomUserAdmin(UserAdmin):
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
        ('Personal info', {'fields': (
            'first_name', 'last_name', 'email', 'organization'
        )}),
        ('Permissions', {'fields': (
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
    list_display = ('name',)
    search_fields = ('name',)
    ordering = ('name',)


admin.site.register(User, CustomUserAdmin)
admin.site.register(Organization, OrganizationAdmin)
