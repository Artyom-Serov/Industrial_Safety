from django.test import TestCase
from facility.forms import ExaminationCreateForm, ExaminationUpdateForm
from facility.models import Briefing, Commission, Course, Examination, Examined
from users.models import Organization, User
from datetime import date


class ExaminationCreateFormTest(TestCase):
    # тесты для формы создания записи о проверке
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
        self.briefing = Briefing.objects.create(name="Первичный")
        self.course = Course.objects.create(
            course_number='001', course_name="Машинист крана автомобильного"
        )
        self.valid_data = {
            'previous_check_date': date(2023, 1, 15),
            'current_check_date': date(2024, 1, 15),
            'next_check_date': date(2025, 1, 15),
            'protocol_number': '123/2024',
            'reason': "Повторная",
            'briefing': self.briefing.id,
            'course': self.course.id,
            'certificate_number': 'ABC123',
            'full_name': "Антонио Фагундес",
            'position': "Инженер",
            'brigade': "Цех №1",
            'previous_safety_group': 'III',
            'safety_group': 'IV',
            'work_experience': "5 лет",
            'chairman_name': "Иван Иванов",
            'chairman_position': "Начальник отдела",
            'member1_name': "Сидор Сидоров",
            'member1_position': "Мастер",
            'member2_name': "Анна Алексеева",
            'member2_position': "Техник",
            'safety_officer_name': "Дмитрий Дмитриев",
            'safety_officer_position': "Инженер-электрик"
        }

    def test_form_valid_data(self):
        # тестирование валидности формы при корректных данных
        form = ExaminationCreateForm(data=self.valid_data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_without_previous_group(self):
        # тестирование не валидности формы без предыдущей группы
        # электробезопасности, при указании даты предыдущей проверки
        data = self.valid_data.copy()
        data['previous_safety_group'] = ''
        form = ExaminationCreateForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())
        self.assertIn('previous_safety_group', form.errors)

    def test_save_create_related_objects(self):
        # тестирование метода 'save', который должен создавать связанные
        # объекты Examined и Commission
        form = ExaminationCreateForm(data=self.valid_data, user=self.user)
        if form.is_valid():
            examination = form.save()
            self.assertEqual(Examination.objects.count(), 1)
            self.assertEqual(Examined.objects.count(), 1)
            self.assertEqual(Commission.objects.count(), 1)
            self.assertEqual(examination.examined.full_name, "Антонио Фагундес")
            self.assertEqual(examination.commission.chairman_name, "Иван Иванов")


class ExaminationUpdateFormTest(TestCase):
    # тесты для формы обновления записи о проверке
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
        self.briefing = Briefing.objects.create(name="Первичный")
        self.course = Course.objects.create(
            course_number='001', course_name="Машинист крана автомобильного"
        )
        self.commission = Commission.objects.create(
            chairman_name="Пётр Петров",
            chairman_position="Начальник отдела",
            member1_name="Сидор Сидоров",
            member1_position="Мастер",
            member2_name="Анна Алексеева",
            member2_position="Техник",
            safety_officer_name="Дмитрий Дмитриев",
            safety_officer_position="Инженер-электрик"
        )
        self.examined = Examined.objects.create(
            full_name="Иван Иванов",
            position="Инженер",
            brigade="Цех №1",
            previous_safety_group='III',
            safety_group='IV',
            work_experience="5 лет",
            user=self.user
        )
        self.examination = Examination.objects.create(
            current_check_date=date(2024, 1, 15),
            next_check_date=date(2025, 1, 15),
            protocol_number='123/2024',
            reason="Повторная",
            commission=self.commission,
            examined=self.examined,
            briefing=self.briefing,
            course=self.course
        )

    def test_form_loads_initial_data(self):
        # тестирование загрузки в форму начальных данных из связной записи
        form = ExaminationUpdateForm(instance=self.examination)
        self.assertEqual(form.initial['full_name'], "Иван Иванов")
        self.assertEqual(form.initial['chairman_name'], "Пётр Петров")

    def test_form_updates_data(self):
        #
        data = {
            'previous_check_date': date(2023, 1, 15),
            'current_check_date': date(2024, 2, 15),
            'next_check_date': date(2025, 2, 15),
            'protocol_number': "123/2024",
            'reason': "Первичная",
            'briefing': self.briefing.id,
            'course': self.course.id,
            'certificate_number': 'ABC123',
            'full_name': "Алексей Алексеев",
            'position': "Техник",
            'brigade': "Цех 2",
            'previous_safety_group': 'II',
            'safety_group': 'III',
            'work_experience': "3 года",
            'chairman_name': "Сергей Сергеев",
            'chairman_position': "Инженер",
            'member1_name': "Иван Иванов",
            'member1_position': "Мастер",
            'member2_name': "Анна Петрова",
            'member2_position': "Электрик",
            'safety_officer_name': "Ольга Ольгина",
            'safety_officer_position': "Энергетик"
        }
        form = ExaminationUpdateForm(data=data, instance=self.examination)
        if form.is_valid():
            updated_examination = form.save()
            self.assertEqual(
                updated_examination.examined.full_name, "Алексей Алексеев"
            )
            self.assertEqual(
                updated_examination.commission.chairman_name, "Сергей Сергеев"
            )
