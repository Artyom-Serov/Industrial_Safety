import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from .forms import DocumentGenerationForm
from .document_generation import generate_document
from facility.models import Examination


def document_generate_view(request, examination_id):
    """
    Обрабатывает запрос на генерацию документа для выбранной записи проверки.

    Получает информацию о проверке из модели Examination по идентификатору.
    Затем обрабатывает POST-запрос с формой выбора шаблона,
    генерирует документ в формате .docx и отправляет его пользователю для
    загрузки.

    Параметры:
    - request: HttpRequest объект, содержащий данные запроса.
    - examination_id: int, идентификатор проверки в базе данных.

    Возвращает:
    - HttpResponse с прикрепленным документом в формате .docx для загрузки.
    """
    examination = Examination.objects.get(id=examination_id)

    if request.method == 'POST':
        form = DocumentGenerationForm(request.POST)
        if form.is_valid():
            template = form.cleaned_data['template']
            template_path = os.path.join(
                settings.BASE_DIR, 'documents', 'templates',
                f"{template}.docx"
            )
            output_name = f"{template}_{examination_id}.docx"
            output_path = os.path.join(
                settings.BASE_DIR, 'generated_documents', output_name
            )
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            generate_document(examination_id, template_path, output_path)

            with open(output_path, 'rb') as file:
                response = HttpResponse(
                    file.read(),
                    content_type='application/vnd.openxmlformats-'
                                 'officedocument.wordprocessingml.document'
                )
                response['Content-Disposition'] = (f'attachment; filename="'
                                                   f'{output_name}"')
                return response

    else:
        form = DocumentGenerationForm()
    return render(
        request, 'documents/document_generate_form.html',
        {'form': form, 'examination': examination}
    )
