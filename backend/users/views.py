"""
Модуль представлений, управляющих пользователями и организациями.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import User, Organization


def user_login(request):
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
    template = 'users/login.html'
    organizations = Organization.objects.all()
    if request.method == 'POST':
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
    return render(request, template, {'organizations': organizations})


@login_required
def user_profile(request):
    """
    Отображает профиль текущего пользователя. Если пользователь — администратор,
    также отображает список всех пользователей.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Рендер шаблона страницы профиля пользователя.
    """
    template = 'users/profile.html'
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = None
    return render(request, template, {'user': request.user, 'users': users})


@login_required
def edit_profile(request):
    """
    Обрабатывает редактирование профиля текущего пользователя. При успешной
    валидации формы сохраняет изменения и перенаправляет на профиль пользователя.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Рендер шаблона редактирования профиля.
    """
    template = 'users/edit_profile.html'
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = CustomUserEditForm(instance=request.user)
    return render(request, template, {'form': form})


@login_required
def admin_edit_user_profile(request, user_id):
    """
    Позволяет администратору редактировать профиль любого пользователя.

    Параметры:
        request (HttpRequest): Объект запроса.
        user_id (int): Идентификатор пользователя для редактирования.

    Возвращает:
        HttpResponse: Рендер шаблона редактирования профиля указанного
        пользователя.
    """
    user = get_object_or_404(User, id=user_id)
    template = 'users/edit_profile.html'
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = CustomUserEditForm(instance=user)
    return render(request, template, {'form': form, 'edit_user': user})


def is_admin(user):
    """
    Проверяет, является ли пользователь администратором.

    Параметры:
        user (User): Пользователь для проверки.

    Возвращает:
        bool: True, если пользователь — администратор, иначе False.
    """
    return user.is_superuser


@user_passes_test(is_admin)
def user_register(request):
    """
    Обрабатывает регистрацию нового пользователя с возможностью выбора или
    создания новой организации. Доступно только для администраторов.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponse: Рендер шаблона регистрации пользователя.
    """
    template = 'users/register.html'
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('users:profile')
    else:
        form = CustomUserCreationForm()
    return render(request, template, {'form': form})


def user_logout(request):
    """
    Выполняет перенаправление пользователя на страницу входа при его выходе
    из системы.

    Параметры:
        request (HttpRequest): Объект запроса.

    Возвращает:
        HttpResponseRedirect: Перенаправление на страницу входа.
    """
    logout(request)
    return redirect('users:login')
