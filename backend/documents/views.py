import os

from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render
from docx2pdf import convert
from .forms import DocumentGenerationForm
from .document_generation import generate_document
from facility.models import Examination


def document_generate_view(request, examination_id):
    # получаем запись проверки
    examination = Examination.objects.get(id=examination_id)

    # обработка формы
    if request.method == 'POST':
        form = DocumentGenerationForm(request.POST)
        if form.is_valid():
            # получаем выбранный шаблон и формат файла
            template = form.cleaned_data['template']
            file_format = form.cleaned_data['file_format']

            # путь к шаблону и временное имя файла для сохранения
            template_path = os.path.join(settings.BASE_DIR, 'documents', 'templates', f"{template}.docx")
            output_name = f"{template}_{examination_id}.{file_format}"
            output_path = os.path.join(settings.BASE_DIR, 'generated_documents', output_name)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # генерация документа в формате .docx
            generate_document(examination_id, template_path, output_path)

            # если выбран формат PDF, конвертируем .docx в .pdf
            if file_format == 'pdf':
                convert(output_path)
                output_path = output_path.replace('.docx', '.pdf')

            # отправляем сгенерированный файл в ответ
            with open(output_path, 'rb') as file:
                response = HttpResponse(file.read(), content_type='application/pdf' if file_format == 'pdf' else 'application/vnd.openxmlformats-officedocument.wordprocessingml.document')
                response['Content-Disposition'] = f'attachment; filename="{output_name}"'
                return response

    else:
        form = DocumentGenerationForm()
    return render(
        request, 'documents/document_generate_form.html',
        {'form': form, 'examination': examination}
    )
