"""
Модуль представлений, управляющих пользователями и организациями.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.cache import cache
from django.core.exceptions import PermissionDenied
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.decorators import method_decorator
from django.views import View

from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import Organization, User


class UserLoginView(View):
    """
    Обрабатывает вход пользователя, проверяя имя пользователя, пароль и
    организацию. При успешной аутентификации перенаправляет на
    главную страницу приложения.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Рендер шаблона страницы входа с сообщением об ошибке
        при неудачной попытке входа.
    """
    template_name = 'users/login.html'

    def get(self, request):
        organizations = cache.get('organizations')
        if not organizations:
            organizations = Organization.objects.all()
            cache.set(
                'organizations', organizations, timeout=settings.CACHE_TTL
            )
        return render(
            request, self.template_name, {'organizations': organizations}
        )

    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        organization_id = request.POST.get('organization')

        try:
            organization = Organization.objects.get(id=organization_id)
        except Organization.DoesNotExist:
            organization = None

        user = authenticate(request, username=username, password=password)
        if user is not None and user.organization == organization:
            login(request, user)
            return redirect('facility:index')
        else:
            messages.error(
                request, 'Неверные имя пользователя, пароль или организация.'
            )

        organizations = cache.get('organizations')
        return render(
            request, self.template_name, {'organizations': organizations}
        )


@method_decorator(login_required, name='dispatch')
class UserProfileView(View):
    """
    Отображает профиль текущего пользователя.
    Если пользователь — администратор,
    также отображает список всех пользователей.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Рендер шаблона страницы профиля пользователя.
    """
    template_name = 'users/profile.html'

    def get(self, request):
        context = {'user': request.user}

        if request.user.is_superuser:
            users = cache.get('all_users')
            if not users:
                users = User.objects.all()
                cache.set('all_users', users, timeout=settings.CACHE_TTL)

            paginator = Paginator(users, settings.DISPLAY_COUNT)
            page_number = request.GET.get('page') or 1

            try:
                page_obj = paginator.get_page(page_number)
            except ValueError:
                page_obj = paginator.get_page(1)

            context.update({
                'page_obj': page_obj,
                'is_paginated': paginator.num_pages > 1,
            })

        return render(request, self.template_name, context)


@method_decorator(login_required, name='dispatch')
class EditProfileView(View):
    """
    Обрабатывает редактирование профиля текущего пользователя. При успешной
    валидации формы сохраняет изменения и перенаправляет
    на профиль пользователя.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Рендер шаблона редактирования профиля.
    """
    template_name = 'users/edit_profile.html'

    def get(self, request):
        form = CustomUserEditForm(instance=request.user)
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
        return render(request, self.template_name, {'form': form})


@method_decorator(login_required, name='dispatch')
class AdminEditUserProfileView(LoginRequiredMixin, View):
    """
    Позволяет администратору редактировать профиль любого пользователя.

    Параметры:
        request (HttpRequest): Объект запроса.
        user_id (int): Идентификатор пользователя для редактирования.

    Возвращает:
        HttpResponse: Рендер шаблона редактирования профиля указанного
        пользователя.
    """
    template_name = 'users/edit_profile.html'

    def get(self, request, user_id):
        if not request.user.is_superuser:
            raise PermissionDenied
        user = get_object_or_404(User, id=user_id)
        form = CustomUserEditForm(instance=user)
        return render(
            request, self.template_name, {'form': form, 'edit_user': user}
        )

    def post(self, request, user_id):
        if not request.user.is_superuser:
            raise PermissionDenied
        user = get_object_or_404(User, id=user_id)
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            cache.clear()
            return redirect('users:profile')
        return render(
            request, self.template_name, {'form': form, 'edit_user': user}
        )


class AdminDeleteUserView(LoginRequiredMixin, View):
    """
    Позволяет администратору удалять пользователей.
    """
    template_name = "users/delete_profile_confirm.html"

    def get(self, request, user_id):
        if not request.user.is_superuser:
            raise PermissionDenied

        user_to_delete = get_object_or_404(User, id=user_id)
        return render(
            request, self.template_name, {"user_to_delete": user_to_delete}
        )

    @staticmethod
    def post(request, user_id):
        if not request.user.is_superuser:
            raise PermissionDenied

        user_to_delete = get_object_or_404(User, id=user_id)
        if user_to_delete == request.user:
            raise PermissionDenied

        user_to_delete.delete()
        cache.clear()
        return redirect("users:profile")


def is_admin(user):
    """
    Проверяет, является ли пользователь администратором.

    Параметры:
        user (User): Пользователь для проверки.

    Возвращает:
        bool: True, если пользователь — администратор, иначе False.
    """
    return user.is_superuser


@method_decorator(user_passes_test(is_admin), name='dispatch')
class UserRegisterView(View):
    """
    Обрабатывает регистрацию нового пользователя с возможностью выбора или
    создания новой организации. Доступно только для администраторов.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Рендер шаблона регистрации пользователя.
    """
    template_name = 'users/register.html'

    def get(self, request):
        form = CustomUserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request):
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
        return render(request, self.template_name, {'form': form})


class UserLogoutView(View):
    """
    Выполняет перенаправление пользователя на страницу входа при его выходе
    из системы.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponseRedirect: Перенаправление на страницу входа.
    """
    def get(self, request):
        logout(request)
        return redirect('users:login')
