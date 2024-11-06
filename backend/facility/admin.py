"""
Модуль администрирования для управления моделями Commission, Examined,
Briefing, Course и Examination в интерфейсе Django Admin.

Классы:
    ExaminedAdmin — Настройка отображения и фильтрации данных модели Examined
        в Django Admin.
    CourseAdmin — Настройка отображения и фильтрации данных модели Course
        в Django Admin.
    ExaminationAdmin — Настройка отображения и фильтрации данных модели
        Examination в Django Admin.
"""
from django.contrib import admin
from .models import Commission, Examined, Briefing, Course, Examination


class ExaminedAdmin(admin.ModelAdmin):
    """
    Класс для настройки отображения и фильтрации данных модели Examined
    в Django Admin.

    Атрибуты:
        list_display (tuple): Определяет поля модели Examined, отображаемые в
            списке записей.
        list_filter (tuple): Определяет поля для фильтрации в Django Admin
            списка записей по названию цеха (участка) аттестуемого, по
            наименованию компании и группе безопасности аттестуемого.
    """
    list_display = (
        'full_name', 'position', 'brigade',
        'company_name', 'safety_group', 'work_experience'
    )
    list_filter = ('brigade', 'company_name', 'safety_group')


class CourseAdmin(admin.ModelAdmin):
    """
    Класс для настройки отображения и фильтрации данных модели Course
    в Django Admin.

    Атрибуты:
        list_display (tuple): Определяет поля модели Course, отображаемые
            в списке записей.
        list_filter (tuple): Определяет поля для фильтрации в Django Admin
            списка записей по номеру и наименованию курса.
    """
    list_display = ('course_number', 'course_name')
    list_filter = ('course_number', 'course_name')


class ExaminationAdmin(admin.ModelAdmin):
    """
    Класс для настройки отображения и фильтрации данных модели Examination
    в Django Admin.

    Атрибуты:
        list_display (tuple): Определяет поля модели Examination,
            отображаемые в списке записей.
        list_filter (tuple): Определяет поля для фильтрации в Django Admin
            списка записей по текущей дате и дате следующей проверки.
    """
    list_display = (
        'created_at', 'current_check_date', 'next_check_date',
        'protocol_number', 'examined', 'commission', 'briefing',
        'certificate_number', 'course'
    )
    list_filter = ('current_check_date', 'next_check_date')


admin.site.register(Commission)
admin.site.register(Examined, ExaminedAdmin)
admin.site.register(Briefing)
admin.site.register(Course, CourseAdmin)
admin.site.register(Examination, ExaminationAdmin)
