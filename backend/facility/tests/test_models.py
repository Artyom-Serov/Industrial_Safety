from django.test import TestCase
from facility.models import (
Commission, Examined, Briefing, Course, Examination
)
from users.models import User, Organization
from datetime import date


class CommissionModelTest(TestCase):
    # тесты модели Commission
    def setUp(self):
        self.commission = Commission.objects.create(
            chairman_name="Иван Иванов",
            chairman_position="Директор",
            member1_name="Пётр Петров",
            member1_position="Главный инженер",
            member2_name="Николай Сидоров",
            member2_position="Техник",
            safety_officer_name="Анна Алексеева",
            safety_officer_position="Электрик"
        )

    def test_organization_saved_to_db(self):
        # тестирование сохранения созданной комиссии в базе данных
        self.assertEqual(Commission.objects.count(), 1)
        self.assertEqual(Commission.objects.first(), self.commission)

    def test_commission_str(self):
        # тестирование строкового представления Commission
        self.assertEqual(str(self.commission), "Комиссия: Иван Иванов")


class ExaminedModelTest(TestCase):
    # тесты модели Examined
    def setUp(self):
        self.organization = Organization.objects.create(
            name='Test organization'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
            organization=self.organization
        )
        self.examined = Examined.objects.create(
            full_name="Антонио Фагундес",
            position="инженер",
            brigade="Цех №1",
            safety_group='III',
            work_experience="5 лет",
            user=self.user
        )

    def test_examined_saved_to_db(self):
        # тестирование сохранения созданного аттестуемого в базе данных
        self.assertEqual(Examined.objects.count(), 1)

    def test_examined_save(self):
        # тестирование присвоения компании пользователя при создании
        # нового аттестуемого
        new_examined = Examined.objects.create(
            full_name="Флавио Кортес",
            position="Мастер",
            brigade="Цех №3",
            safety_group='II',
            work_experience="7 лет",
            user=self.user
        )
        self.assertEqual(new_examined.company_name, self.organization)

    def test_examined_str(self):
        # тестирование строкового представления Examined
        self.assertEqual(str(self.examined), "Антонио Фагундес")


class BriefingModelTest(TestCase):
    # тесты модели Briefing
    def setUp(self):
        self.briefing = Briefing.objects.create(name="Первичный")

    def test_briefing_saved_to_db(self):
        # тестирование сохранения созданного инструктажа в базе данных
        self.assertEqual(Briefing.objects.count(), 1)
        self.assertEqual(Briefing.objects.first(), self.briefing)

    def test_briefing_name_max_length(self):
        # тестирование длины поля 'name'
        max_length = self.briefing._meta.get_field('name').max_length
        self.assertEqual(max_length, 255)

    def test_briefing_str(self):
        # тестирование строкового представления Briefing
        self.assertEqual(str(self.briefing), "Первичный")


class CourseModelTest(TestCase):
    # тесты модели Course
    def setUp(self):
        self.course = Course.objects.create(
            course_number='001', course_name="Машинист крана автомобильного"
        )

    def test_course_saved_to_db(self):
        # тестирование сохранения созданного курса в базе данных
        self.assertEqual(Course.objects.count(), 1)
        self.assertEqual(Course.objects.first(), self.course)

    def test_course_number_max_length(self):
        # тестирование длины поля 'course_number'
        max_length = self.course._meta.get_field('course_number').max_length
        self.assertEqual(max_length, 255)

    def test_course_name_max_length(self):
        # тестирование длины поля 'course_name'
        max_length = self.course._meta.get_field('course_name').max_length
        self.assertEqual(max_length, 255)

    def test_course_str(self):
        # тестирование строкового представления Course
        self.assertEqual(str(self.course), "Машинист крана автомобильного")


class ExaminationModelTest(TestCase):
    # тесты модели Examination
    def setUp(self):
        self.commission = Commission.objects.create(
            chairman_name="Иван Иванов",
            chairman_position="Директор",
            member1_name="Пётр Петров",
            member1_position="Главный инженер",
            member2_name="Николай Сидоров",
            member2_position="Техник",
            safety_officer_name="Анна Алексеева",
            safety_officer_position="Электрик"
        )
        self.organization = Organization.objects.create(
            name='Test organization'
        )
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='password123',
            organization=self.organization
        )
        self.examined = Examined.objects.create(
            full_name="Антонио Фагундес",
            position="инженер",
            brigade="Цех №1",
            safety_group='III',
            work_experience="5 лет",
            user=self.user
        )
        self.briefing = Briefing.objects.create(name="Первичный")
        self.course = Course.objects.create(
            course_number='001', course_name="Машинист крана автомобильного"
        )
        self.examination = Examination.objects.create(
            current_check_date=date(2024, 1,15),
            next_check_date=date(2025, 1,15),
            protocol_number='123/2024',
            reason="Повторная",
            commission=self.commission,
            examined=self.examined,
            briefing=self.briefing,
            course=self.course
        )

    def test_examination_saved_to_db(self):
        # тестирование сохранения созданной проверки в базе данных
        self.assertEqual(Examination.objects.count(), 1)
        self.assertEqual(Examination.objects.first(), self.examination)

    def test_examination_str(self):
        # тестирование строкового представления Examination
        self.assertEqual(str(self.examination), "Проверка 123/2024")
