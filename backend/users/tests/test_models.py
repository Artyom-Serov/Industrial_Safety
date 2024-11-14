from django.test import TestCase
from users.models import Organization, User


class OrganizationModelTest(TestCase):
    # тестирование модели организаций
    def setUp(self):
        # создание тестовой организации
        self.organization = Organization.objects.create(
            name='Test organization'
        )

    def test_organization_name_max_length(self):
        # проверка длины поля
        max_length = self.organization._meta.get_field('name').max_length
        self.assertEqual(max_length, 255)

    def test_organization_saved_to_db(self):
        # проверка сохранения созданной организации в базе данных
        self.assertEqual(Organization.objects.count(), 1)
        self.assertEqual(Organization.objects.first(), self.organization)

    def test_organization_str(self):
        # проверка строкового представления
        self.assertEqual(str(self.organization), 'Test organization')


class UserModelTest(TestCase):
    # тестирование модели пользователя
    def setUp(self):
        # создание тестового пользователя и организации
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
        # проверка сохранения пользователя в базе
        self.assertEqual(User.objects.count(), 1)
        self.assertEqual(User.objects.first(), self.user)

    def test_user_str(self):
        # проверка строкового представления
        self.assertEqual(str(self.user), 'testuser')

    def test_user_email_unique(self):
        # проверка уникальности эл.почты
        with self.assertRaises(Exception):
            User.objects.create_user(
                username='testuser2',
                email='testuser@example.com',
                password='password123'
            )

    def test_user_default_ordering(self):
        # проверка сортировки по умолчанию
        self.assertEqual(list(User.objects.all().order_by('id')), [self.user])

    def test_user_organization(self):
        # проверка связи пользователя с организацией
        self.assertEqual(self.user.organization, self.organization)
