from datetime import date

import pytest
from django.conf import settings
from django.core.cache import cache
from django.urls import reverse
from facility.models import Briefing, Commission, Course, Examination, Examined
from users.models import Organization, User


@pytest.fixture
def create_user(db):
    """Фикстура создания обычного пользователя."""
    organization = Organization.objects.create(name='Test organization')
    return User.objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='password123',
        organization=organization
    )


@pytest.fixture
def create_superuser(db):
    """Фикстура создания суперпользователя."""
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpassword'
    )


@pytest.fixture
def create_examination(db, create_user):
    """Фикстура создания тестовой проверки."""
    briefing = Briefing.objects.create(name="Первичный")
    course = Course.objects.create(
        course_number='001', course_name="Машинист крана автомобильного"
    )
    commission = Commission.objects.create(
        chairman_name="Иван Иванов",
        chairman_position="Директор",
        member1_name="Пётр Петров",
        member1_position="Главный инженер",
        member2_name="Николай Сидоров",
        member2_position="Техник",
        safety_officer_name="Анна Алексеева",
        safety_officer_position="Электрик"
    )
    examined = Examined.objects.create(
        full_name="Антонио Фагундес",
        position="инженер",
        brigade="Цех №1",
        safety_group='III',
        work_experience="5 лет",
        user=create_user
    )
    return Examination.objects.create(
        current_check_date=date(2024, 1, 15),
        next_check_date=date(2025, 1, 15),
        protocol_number='123/2024',
        reason="Повторная",
        briefing=briefing,
        course=course,
        commission=commission,
        examined=examined,
    )


@pytest.mark.django_db
def test_index_view_superuser(client, create_superuser, create_examination):
    """Тестирование отображения всех записей для суперпользователя."""
    client.login(username=create_superuser.username, password='adminpassword')
    url = reverse('facility:index')
    response = client.get(url)
    assert response.status_code == 200
    assert 'facility/index.html' in [t.name for t in response.templates]
    assert len(response.context['examinations']) == 1


@pytest.mark.django_db
def test_index_view_user(client, create_user, create_examination):
    """Тестирование фильтрации записей для обычного пользователя."""
    client.login(username=create_user.username, password='password123')
    url = reverse('facility:index')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['examinations']) == 1


@pytest.mark.django_db
def test_pagination_in_index_view(client, create_user):
    """Тестирование работы пагинации списка проверок."""
    cache.clear()
    client.login(username=create_user.username, password='password123')
    display_count = settings.DISPLAY_COUNT
    total_records = display_count + 5
    for i in range(total_records):
        briefing = Briefing.objects.create(name="Первичный")
        course = Course.objects.create(
            course_number='001', course_name="Машинист крана автомобильного"
        )
        commission = Commission.objects.create(
            chairman_name=f"Член {i}",
            chairman_position="Директор",
            member1_name=f"Петров {i}",
            member1_position="Главный инженер",
            member2_name=f"Сидоров {i}",
            member2_position="Техник",
            safety_officer_name=f"Анна {i}",
            safety_officer_position="Электрик"
        )
        examined = Examined.objects.create(
            full_name=f"Тестируемый {i}",
            position="Инженер",
            brigade=f"Цех №{i}",
            safety_group='III',
            work_experience="5 лет",
            user=create_user
        )
        Examination.objects.create(
            current_check_date=date(2024, 1, 15),
            next_check_date=date(2025, 1, 15),
            protocol_number=f'123/2024-{i}',
            reason="Повторная",
            briefing=briefing,
            course=course,
            commission=commission,
            examined=examined,
        )

    cache.clear()
    url = reverse('facility:index')
    response = client.get(url)
    assert response.status_code == 200
    assert len(response.context['examinations']) == display_count
    assert response.context['is_paginated'] is True
    assert response.context['page_obj'].number == 1

    response = client.get(url + '?page=2')
    assert response.status_code == 200

    remaining_items = total_records - display_count
    assert len(
        response.context['examinations']
    ) == min(
        display_count, remaining_items
    )
    assert response.context['page_obj'].number == 2


@pytest.mark.django_db
def test_create_examination_view(client, create_user, create_superuser):
    """Тестирование создания новой проверки."""
    client.login(username=create_superuser.username, password='adminpassword')
    briefing = Briefing.objects.create(name="Первичный")
    course = Course.objects.create(
        course_number='001', course_name="Машинист крана автомобильного"
    )
    url = reverse('facility:create_examination')
    data = {
        'current_check_date': date(2024, 1, 15),
        'next_check_date': date(2025, 1, 15),
        'protocol_number': '123/2024',
        'reason': "Повторная",
        'briefing': briefing.id,
        'course': course.id,
        'full_name': "Антонио Фагундес",
        'position': "Инженер",
        'brigade': "Цех №1",
        'safety_group': 'III',
        'work_experience': "5 лет",
        'chairman_name': "Иван Иванов",
        'chairman_position': "Директор",
        'member1_name': "Пётр Петров",
        'member1_position': "Главный инженер",
        'member2_name': "Николай Сидоров",
        'member2_position': "Техник",
        'safety_officer_name': "Анна Алексеева",
        'safety_officer_position': "Электрик",
        'company_name': create_user.organization.id,
        'user': create_user.id
    }
    response = client.post(url, data)
    assert response.status_code == 302
    assert Examination.objects.count() == 1


@pytest.mark.django_db
def test_update_examination_view(client, create_superuser, create_examination):
    """Тестирование обновления существующей проверки."""
    client.login(username=create_superuser.username, password='adminpassword')
    url = reverse('facility:update_examination', args=[create_examination.id])
    data = {
        'current_check_date': date(2024, 1, 15),
        'next_check_date': date(2025, 1, 15),
        'protocol_number': '456/2024',
        'reason': "Первичная",
        'briefing': create_examination.briefing.id,
        'course': create_examination.course.id,
        'full_name': "Антонио Фагундес",
        'position': "Инженер",
        'brigade': "Цех №1",
        'safety_group': 'III',
        'work_experience': "5 лет",
        'chairman_name': "Иван Иванов",
        'chairman_position': "Директор",
        'member1_name': "Пётр Петров",
        'member1_position': "Главный инженер",
        'member2_name': "Николай Сидоров",
        'member2_position': "Техник",
        'safety_officer_name': "Анна Алексеева",
        'safety_officer_position': "Электрик"
    }
    response = client.post(url, data)
    assert response.status_code == 302

    updated_examination = Examination.objects.get(id=create_examination.id)
    assert updated_examination.protocol_number == '456/2024'


@pytest.mark.django_db
def test_delete_examination_view(client, create_superuser, create_examination):
    """Тестирование удаления проверки."""
    client.login(username=create_superuser.username, password='adminpassword')
    url = reverse('facility:delete_examination', args=[create_examination.id])
    response = client.post(url)
    assert response.status_code == 302
    assert Examination.objects.count() == 0
