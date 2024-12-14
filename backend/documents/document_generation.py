from docxtpl import DocxTemplate
from facility.models import Examination


def generate_document(examination_id, template_path, output_path):
    """
    Генерирует документ на основе выбранного шаблона и данных проверки.

    Параметры:
    - examination_id (int): Идентификатор проверки, для которой создается
        документ.
    - template_path (str): Путь к шаблону документа (.docx).
    - output_path (str): Путь для сохранения сгенерированного документа.

    Ключи контекста:
    - company_name (str): Наименование компании.
    - protocol_number (str): Номер протокола.
    - examined__check_date (str): Дата текущей проверки (протокола).
    - chairman_name (str): ФИО председателя комиссии.
    - chairman_position (str): Должность председателя комиссии.
    - member1_name (str): ФИО первого члена комиссии.
    - member1_position (str): Должность первого члена комиссии.
    - member2_name (str): ФИО второго члена комиссии.
    - member2_position (str): Должность второго члена комиссии.
    - examined_full_name (str): ФИО аттестуемого.
    - examined_position (str): Должность аттестуемого.
    - examined_brigade (str): Цех, участок, бригада аттестуемого.
    - examination_reason (str): Причина проверки.
    - course_number (str): Номер программы.
    - course_name (str): Наименование программы.
    - certificate_number (str): Номер удостоверения.
    - safety_group (str): Группа электробезопасности.
    - safety_officer_name (str): ФИО ответственного за электробезопасность.
    - safety_officer_position (str): Должность ответственного за
        электробезопасность.
    - work_experience (int): Стаж.
    - next_check_date (str): Дата следующей проверки.
    - briefings_name (str): Вид инструктажа.
    """
    examination = Examination.objects.select_related(
        'examined', 'commission', 'briefing', 'course'
    ).get(id=examination_id)

    # Подготовка данных для шаблона
    context = {
        'company_name': examination.examined.company_name,
        'protocol_number': examination.protocol_number,
        'examined__check_date': examination.current_check_date.strftime(
            '%d.%m.%Y'
        ),
        'chairman_name': examination.commission.chairman_name,
        'chairman_position': examination.commission.chairman_position,
        'member1_name': examination.commission.member1_name,
        'member1_position': examination.commission.member1_position,
        'member2_name': examination.commission.member2_name,
        'member2_position': examination.commission.member2_position,
        'examined_full_name': examination.examined.full_name,
        'examined_position': examination.examined.position,
        'examined_brigade': examination.examined.brigade,
        'examination_reason': examination.reason,
        'course_number': examination.course.course_number,
        'course_name': examination.course.course_name,
        'certificate_number': examination.certificate_number,
        'safety_group': examination.examined.safety_group,
        'safety_officer_name': examination.commission.safety_officer_name,
        'safety_officer_position': examination.commission.safety_officer_position,
        'work_experience': examination.examined.work_experience,
        'next_check_date': examination.next_check_date.strftime('%d.%m.%Y'),
        'briefings_name': examination.briefing.name
    }

    doc = DocxTemplate(template_path)
    doc.render(context)

    doc.save(output_path)
