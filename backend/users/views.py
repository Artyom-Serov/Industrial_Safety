from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required, user_passes_test
from .forms import CustomUserCreationForm, CustomUserEditForm


def login_view(request):
    template = 'users/login.html'
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        organization = request.POST['organization']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('profile')
    return render(request, template)


@login_required
def profile_view(request):
    template = 'users/profile.html'
    return render(request, template, {'user': request.user})


@login_required
def edit_profile_view(request):
    template = 'users/edit_profile.html'
    if request.method == 'POST':
        form = CustomUserEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserEditForm(instance=request.user)
    return render(request, template, {'form': form})


def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)
def register_view(request):
    template = 'users/register.html'
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CustomUserCreationForm()
    return render(request, template, {'form': form})
