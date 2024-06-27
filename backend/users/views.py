from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomUserEditForm
from .models import User, Organization


def user_login(request):
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
            return redirect('profile')
        else:
            messages.error(request, 'Неверные имя пользователя, пароль или организация.')
    return render(request, template, {'organizations': organizations})


@login_required
def user_profile(request):
    template = 'users/profile.html'
    if request.user.is_superuser:
        users = User.objects.all()
    else:
        users = None
    return render(request, template, {'user': request.user, 'users': users})


@login_required
def edit_profile(request):
    template = 'users/edit_profile.html'
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserEditForm(instance=request.user)
    return render(request, template, {'form': form})


@login_required
def admin_edit_user_profile(request, user_id):
    user = get_object_or_404(User, id=user_id)
    template = 'users/edit_profile.html'
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserEditForm(instance=user)
    return render(request, template, {'form': form, 'edit_user': user})


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def user_register(request):
    template = 'users/register.html'
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, template, {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')
