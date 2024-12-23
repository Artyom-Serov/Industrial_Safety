from django.test import TestCase
from users.models import Organization, User


class OrganizationModelTest(TestCase):
    """Тесты модели организаций."""
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test organization'
        )

    def test_organization_name_max_length(self):
        """Тестирование длины поля."""
        max_length = self.organization._meta.get_field('name').max_length
        self.assertEqual(max_length, 255)

    def test_organization_saved_to_db(self):
        """Тестирование сохранения созданной организации в базе данных."""
        self.assertEqual(Organization.objects.count(), 1)
        self.assertEqual(Organization.objects.first(), self.organization)

    def test_organization_str(self):
        """Тестирование строкового представления."""
        self.assertEqual(str(self.organization), 'Test organization')


class UserModelTest(TestCase):
    """Тесты модели пользователя."""
    def setUp(self):
        self.organization = Organization.objects.create(
            name='User organization'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
            organization=self.organization
        )

    def test_user_saved_to_db(self):
        """Тестирование сохранения пользователя в базе."""
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first(), self.user)

    def test_user_str(self):
        """Тестирование строкового представления."""
        self.assertEqual(str(self.user), 'testuser')

    def test_user_email_unique(self):
        """Тестирование уникальности электронной почты."""
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser2',
                email='testuser@example.com',
                password='password123'
            )

    def test_user_default_ordering(self):
        """Тестирование сортировки по умолчанию."""
        self.assertEqual(list(User.objects.all().order_by('id')), [self.user])

    def test_user_organization(self):
        """Тестирование связи пользователя с организацией."""
        self.assertEqual(self.user.organization, self.organization)
