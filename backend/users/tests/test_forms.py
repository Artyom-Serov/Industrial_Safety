from django.test import TestCase
from users.forms import CustomUserCreationForm, CustomUserEditForm
from users.models import Organization, User


class CustomUserCreationFormTest(TestCase):
    # тесты формы создания пользователя
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Existing organization'
        )
        self.valid_data = {
            'username': 'testuser',
            'organization': self.organization.id,
            'email': 'testuser@example.com',
            'first_name': 'First',
            'last_name': 'Last',
            'password1': 'strongpassword123',
            'password2': 'strongpassword123',
            'new_organization': 'New organization',
        }

    def test_form_valid_with_existing_organization(self):
        # тестирование валидности формы при выборе существующей организации
        data = self.valid_data.copy()
        data['new_organization'] = ''
        form = CustomUserCreationForm(data)
        self.assertTrue(form.is_valid())

    def test_form_valid_with_new_organization(self):
        # тестирование валидности формы при вводе новой организации
        form = CustomUserCreationForm(self.valid_data)
        self.assertTrue(form.is_valid())

    def test_create_user_with_existing_organization(self):
        # тестирование создания пользователя с существующей организацией
        data = self.valid_data.copy()
        data['new_organization'] = ''
        form = CustomUserCreationForm(data)
        user = form.save()
        self.assertEqual(user.organization, self.organization)

    def test_create_user_with_new_organization(self):
        # тестирование создания пользователя с новой организацией
        form = CustomUserCreationForm(self.valid_data)
        user = form.save()
        self.assertEqual(user.organization.name, 'New organization')
        self.assertEqual(Organization.objects.count(), 2)


class CustomUserEditFormTest(TestCase):
    # тесты формы редактирования пользователя
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Existing organization'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
            organization=self.organization
        )
        self.valid_data = {
            'username': 'updateuser',
            'email': 'updated@example.com',
            'first_user': 'Updated',
            'last_name': 'User',
            'organization': self.organization.id,
            'new_organization': 'Updated organization',
            'password1': '',
            'password2': '',
        }

    def test_form_valid_without_password_change(self):
        # тестирование валидности формы без смены пароля
        form = CustomUserEditForm(self.valid_data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_form_valid_with_password_change(self):
        # тестирование валидности формы при смене пароля
        data = self.valid_data.copy()
        data['password1'] = 'newstrongpassword123'
        data['password2'] = 'newstrongpassword123'
        form = CustomUserEditForm(data, instance=self.user)
        self.assertTrue(form.is_valid())

    def test_update_user_with_new_organization(self):
        # тестирование обновления пользователя с новой организацией
        form = CustomUserEditForm(self.valid_data, instance=self.user)
        user = form.save()
        self.assertEqual(user.organization.name, 'Updated organization')
        self.assertEqual(Organization.objects.count(), 2)

    def test_form_invalid_with_mismatched_passwords(self):
        # тестирование не валидности формы при несовпадении паролей
        data = self.valid_data.copy()
        data['password1'] = 'newpassword123'
        data['password2'] = 'differentpassword123'
        form = CustomUserEditForm(data, instance=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        self.assertEqual(form.errors['password2'], ["Пароли не совпадают."])
