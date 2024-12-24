import pytest
from django.urls import reverse
from users.models import User, Organization


@pytest.fixture
def organization():
    """Фикстура тестовой организации."""
    return Organization.objects.create(name='Test organization')


@pytest.fixture
def admin_user(organization):
    """Фикстура суперпользователя, связанного с тестовой организацией."""
    user = User.objects.create_superuser(
        username='admin', email='admin@example.com', password='password123',
        organization=organization
    )
    return user


@pytest.fixture
def regular_user(organization):
    """Фикстура обычного пользователя, связанного с тестовой организацией."""
    user = User.objects.create_user(
        username='testuser', email='testuser@example.com', password='password123',
        organization=organization
    )
    return user


@pytest.fixture
def client_with_logged_in_admin(client, admin_user):
    """Фикстура аутентификации суперпользователя в клиенте тестирования."""
    client.login(username=admin_user.username, password='password123')
    return client


@pytest.fixture
def client_with_logged_in_user(client, regular_user):
    """Фикстура аутентификации обычного пользователя в клиенте тестирования."""
    client.login(username=regular_user.username, password='password123')
    return client



@pytest.mark.django_db
def test_user_login(client, organization, regular_user):
    """Тест входа пользователя."""
    url = reverse('users:login')
    data = {
        'username': regular_user.username,
        'password': 'password123',
        'organization': organization.id,
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('facility:index')


@pytest.mark.django_db
def test_user_login_invalid_credentials(client, organization):
    """Тест входа пользователя с некорректными данными."""
    url = reverse('users:login')
    data = {
        'username': 'wrongname',
        'password': 'wrongpassword',
        'organization': organization.id,
    }
    response = client.post(url, data)
    assert response.status_code == 200
    assert ("Неверные имя пользователя, пароль или организация." in
            response.content.decode())


@pytest.mark.django_db
def test_user_profile(client_with_logged_in_user):
    """Тест просмотра профиля пользователя."""
    url = reverse('users:profile')
    response = client_with_logged_in_user.get(url)
    assert response.status_code == 200
    assert "Имя пользователя: testuser" in response.content.decode()


@pytest.mark.django_db
def test_edit_profile(client_with_logged_in_user):
    """Тест редактирования профиля пользователя."""
    url = reverse('users:edit_profile')
    data = {
        'username': 'updateduser',
        'email': 'updateduser@example.com',
        'first_name': 'Updated',
        'lst_name': 'User',
    }
    response = client_with_logged_in_user.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('users:profile')


@pytest.mark.django_db
def test_admin_edit_user_profile(client_with_logged_in_admin, regular_user):
    """Тест редактирования профиля пользователя администратором."""
    url = reverse('users:edit_user_profile', args=[regular_user.id])
    data = {
        'username': 'adminupdated',
        'email': 'adminupdated@example.com',
    }
    response = client_with_logged_in_admin.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('users:profile')


@pytest.mark.django_db
def test_user_register_with_existing_organization(
client_with_logged_in_admin, organization
):
    """Тест регистрации нового пользователя с существующей организацией."""
    url = reverse('users:register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'password456',
        'password2': 'password456',
        'organization': organization.id,
    }
    response = client_with_logged_in_admin.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('users:profile')
    new_user = User.objects.filter(username='newuser').first()
    assert new_user is not None
    assert new_user.organization == organization


@pytest.mark.django_db
def test_user_register_with_new_organization(client_with_logged_in_admin):
    """Тест регистрации нового пользователя с новой организацией."""
    url = reverse('users:register')
    data = {
        'username': 'newuser',
        'email': 'newuser@example.com',
        'password1': 'password456',
        'password2': 'password456',
        'new_organization': 'New organization',
    }
    response = client_with_logged_in_admin.post(url, data)
    assert response.status_code == 302
    assert response.url == reverse('users:profile')
    new_user = User.objects.filter(username='newuser').first()
    new_organization = Organization.objects.filter(
        name='New organization'
    ).first()
    assert new_user is not None
    assert new_organization is not None
    assert new_user.organization == new_organization


@pytest.mark.django_db
def test_user_logout(client_with_logged_in_user):
    """Тест выхода пользователя из системы."""
    url = reverse('users:logout')
    response = client_with_logged_in_user.get(url)
    assert response.status_code == 302
    assert response.url == reverse('users:login')