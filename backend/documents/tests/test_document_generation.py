import pytest
from unittest.mock import patch, MagicMock
from documents.document_generation import generate_document
from facility.models import (
Examination, Commission, Examined, Briefing, Course
)
from users.models import Organization, User
from datetime import date


@pytest.fixture
def setup_examination(db):
    """Фикстура создания тестовой проверки."""
    organization = Organization.objects.create(name='Test organization')
    user = User.objects.create_user(
        username='testuser',
        organization=organization
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
        position="Инженер",
        brigade="Цех №1",
        safety_group='III',
        work_experience="5 лет",
        user=user
    )
    briefing = Briefing.objects.create(name="Первичный")
    course = Course.objects.create(
        course_number='001',
        course_name="Машинист крана автомобильного"
    )
    return Examination.objects.create(
        current_check_date=date(2024, 1, 15),
        next_check_date=date(2025, 1, 15),
        protocol_number='123/2024',
        reason="Повторная",
        commission=commission,
        examined=examined,
        briefing=briefing,
        course=course
    )


@pytest.mark.django_db
@patch('documents.document_generation.DocxTemplate')
def test_generate_document(mock_docxtemplate, setup_examination, tmp_path):
    """
    Тестирует генерацию документа.
    Проверяет корректность контекста и сохранение файла.
    """
    template_path = tmp_path / 'template.docx'
    output_path = tmp_path / 'output.docx'
    template_path.write_text('Fictitious template content')

    mock_doc = MagicMock()
    mock_docxtemplate.return_value = mock_doc

    generate_document(
        setup_examination.id,
        str(template_path),
        str(output_path)
    )

    mock_docxtemplate.assert_called_once_with(str(template_path))
    mock_doc.render.assert_called_once_with({
        'company_name': setup_examination.examined.company_name,
        'protocol_number': setup_examination.protocol_number,
        'examined__check_date': '15.01.2024',
        'chairman_name': setup_examination.commission.chairman_name,
        'chairman_position': setup_examination.commission.chairman_position,
        'member1_name': setup_examination.commission.member1_name,
        'member1_position': setup_examination.commission.member1_position,
        'member2_name': setup_examination.commission.member2_name,
        'member2_position': setup_examination.commission.member2_position,
        'examined_full_name': setup_examination.examined.full_name,
        'examined_position': setup_examination.examined.position,
        'examined_brigade': setup_examination.examined.brigade,
        'examination_reason': setup_examination.reason,
        'course_number': setup_examination.course.course_number,
        'course_name': setup_examination.course.course_name,
        'certificate_number': setup_examination.certificate_number,
        'safety_group': setup_examination.examined.safety_group,
        'safety_officer_name': setup_examination.commission.safety_officer_name,
        'safety_officer_position': setup_examination.commission.safety_officer_position,
        'work_experience': setup_examination.examined.work_experience,
        'next_check_date': '15.01.2025',
        'briefings_name': setup_examination.briefing.name,
    })
    mock_doc.save.assert_called_once_with(str(output_path))

