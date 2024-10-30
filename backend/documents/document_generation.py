from docxtpl import DocxTemplate
from facility.models import Examination


def generate_document(examination_id, template_path, output_path):
    examination = Examination.objects.select_related(
        'examined', 'commission', 'briefing', 'course'
    ).get(id=examination_id)

    # Подготовка данных для шаблона
    context = {
        'company_name': examination.examined.company_name, # наименование компании
        'protocol_number': examination.protocol_number, # номер протокола
        'examined__check_date': examination.current_check_date.strftime('%d.%m.%Y'), # дата текущей проверки (протокола)
        'chairman_name': examination.commission.chairman_name, # ФИО председателя комиссии
        'chairman_position': examination.commission.chairman_position, # должность председателя комиссии
        'member1_name': examination.commission.member1_name, # ФИО первого члена комиссии
        'member1_position': examination.commission.member1_position, # должность первого члена комиссии
        'member2_name': examination.commission.member2_name, # ФИО второго члена комиссии
        'member2_position': examination.commission.member2_position, # должность второго члена комиссии
        'examined_full_name': examination.examined.full_name, # ФИО аттестуемого
        'examined_position': examination.examined.position, # должность аттестуемого
        'examined_brigade': examination.examined.brigade, # цех, участок, бригада аттестуемого
        'examination_reason': examination.reason, # причина проверки
        'course_number': examination.course.course_number, # номер программы
        'course_name': examination.course.course_name, # наименование программы
        'certificate_number': examination.certificate_number, # номер удостоверения
        'safety_group': examination.examined.safety_group, # группа электробезопасности
        'safety_officer_name': examination.commission.safety_officer_name, # ФИО ответственного за электробезопасность
        'safety_officer_position': examination.commission.safety_officer_position, # должность ответственного за электробезопасность
        'work_experience': examination.examined.work_experience, # стаж
        'next_check_date': examination.next_check_date.strftime('%d.%m.%Y'), # дата следующей проверки
        'briefings_name': examination.briefing.name # вид инструктажа
    }

    # открываем шаблон документа
    doc = DocxTemplate(template_path)
    doc.render(context)

    # сохраняем сгенерированный документ
    doc.save(output_path)