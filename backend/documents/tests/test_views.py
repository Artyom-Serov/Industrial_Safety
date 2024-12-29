import os
import shutil
from email.header import decode_header
from unittest.mock import mock_open, patch

import pytest
from django.conf import settings
from django.urls import reverse
from documents.forms import DocumentGenerationForm
from documents.views import document_generate_view
from facility.models import Briefing, Commission, Course, Examination, Examined
from users.models import User


@pytest.fixture
def setup_examination():
    """Фикстура создания необходимых объектов проверки."""
    user = User.objects.create_user(
        username='testuser', password='password123'
    )
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
        user=user
    )
    examination = Examination.objects.create(
        previous_check_date=None,
        current_check_date='2024-1-15',
        next_check_date='2025-1-15',
        protocol_number='123/2024',
        reason="Первичная",
        certificate_number="67890",
        commission=commission,
        examined=examined,
        briefing=briefing,
        course=course,
    )
    return examination


@pytest.fixture
def url(setup_examination):
    """Фикстура URL представления генерации документа."""
    return reverse("documents:document_generate", args=[setup_examination.id])


@pytest.mark.django_db
@patch('documents.views.generate_document')
def test_document_generation(generate_mock, setup_examination, url, rf):
    """Тест успешной генерации документа."""
    data = {'template': "протокол_проверки_по_ОТ"}
    request = rf.post(url, data)

    output_name = f"протокол_проверки_по_ОТ_{setup_examination.id}.docx"
    output_path = os.path.join(
        settings.BASE_DIR, 'generated_documents', output_name
    )
    generated_dir = os.path.dirname(output_path)

    os.makedirs(generated_dir, exist_ok=True)
    with open(output_path, "wb") as temp_file:
        temp_file.write(b'Test document content')

    response = document_generate_view(request, setup_examination.id)

    generate_mock.assert_called_once_with(
        setup_examination.id,
        f"{settings.BASE_DIR}/documents/templates/"
        f"протокол_проверки_по_ОТ.docx",
        output_path,
    )
    assert response.status_code == 200

    header = response['Content-Disposition']
    decoded_header = decode_header(header)
    decoded_filename = "".join(
        part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
        for part, charset in decoded_header
    )
    expected_filename = f'attachment; filename="{output_name}"'
    assert expected_filename in decoded_filename
    shutil.rmtree(generated_dir, ignore_errors=True)


@pytest.mark.django_db
def test_invalid_form_submission(setup_examination, url, rf):
    """Тест отправки пустой формы."""
    data = {}
    request = rf.post(url, data)
    response = document_generate_view(request, setup_examination.id)
    assert response.status_code == 200
    if hasattr(response, 'context') and response.context:
        assert isinstance(response.context['form'], DocumentGenerationForm)
        assert response.context['form'].errors


@pytest.mark.django_db
@patch('documents.views.cache.get')
@patch('documents.views.cache.set')
def test_cache_usage(mock_cache_set, mock_cache_get,
                     setup_examination, url, rf):
    """Тестирование использования кэша."""
    mock_cache_get.return_value = setup_examination
    request = rf.get(url)
    response = document_generate_view(request, setup_examination.id)
    assert response.status_code == 200
    assert mock_cache_get.called
    mock_cache_get.assert_called_with(f'examination_{setup_examination.id}')
    assert setup_examination.protocol_number in response.content.decode()
    assert setup_examination.examined.full_name in response.content.decode()


@pytest.mark.django_db
@patch('documents.views.open',
       new_callable=mock_open,
       read_data=b'Test document content')
@patch('documents.views.cache.get')
@patch('documents.views.cache.set')
def test_cached_document_response(mock_cache_set, mock_cache_get, mock_open,
                                  setup_examination, url, rf):
    """Тест возврата кэшированного документа."""
    mock_cache_get.side_effect = [None, b'Test document content']
    data = {'template': "протокол_проверки_по_ОТ"}
    request = rf.post(url, data)
    response = document_generate_view(request, setup_examination.id)

    assert response.status_code == 200
    assert response.content == b'Test document content'

    header = response['Content-Disposition']
    decoded_header = decode_header(header)
    decoded_filename = "".join(
        part.decode(charset or 'utf-8') if isinstance(part, bytes) else part
        for part, charset in decoded_header
    )
    expected_filename = (f'attachment; filename='
                         f'"протокол_проверки_по_ОТ_'
                         f'{setup_examination.id}.docx"')
    assert expected_filename in decoded_filename
