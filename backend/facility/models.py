from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from users.models import User, Organization


class Commission(models.Model):
    """Модель комиссии."""
    chairman_name = models.CharField(
        max_length=255,
        verbose_name="ФИО председателя комиссии",
        help_text="Введите фамилию, имя и отчество председателя комиссии"
    )
    chairman_position = models.CharField(
        max_length=255,
        verbose_name="Должность председателя комиссии",
        help_text="Введите должность председателя комиссии"
    )
    member1_name = models.CharField(
        max_length=255,
        verbose_name="ФИО первого члена комиссии",
        help_text="Введите фамилию, имя и отчество первого члена комиссии"
    )
    member1_position = models.CharField(
        max_length=255,
        verbose_name="Должность первого члена комиссии",
        help_text="Введите должность первого члена комиссии"
    )
    member2_name = models.CharField(
        max_length=255,
        verbose_name="ФИО второго члена комиссии",
        help_text="Введите фамилию, имя и отчество второго члена комиссии"
    )
    member2_position = models.CharField(
        max_length=255,
        verbose_name="Должность второго члена комиссии",
        help_text="Введите должность второго члена комиссии"
    )
    safety_officer_name = models.CharField(
        max_length=255,
        verbose_name="ФИО ответственного за электробезопасность",
        help_text="Введите фамилию, имя и отчество ответственного "
                  "за электробезопасность"
    )
    safety_officer_position = models.CharField(
        max_length=255,
        verbose_name="Должность ответственного за электробезопасность",
        help_text="Введите должность ответственного за электробезопасность"
    )

    class Meta:
        verbose_name = "Комиссия"
        verbose_name_plural = "Комиссии"

    def __str__(self):
        return f"Комиссия: {self.chairman_name}"


class Examined(models.Model):
    """Модель аттестуемого."""
    full_name = models.CharField(
        max_length=255,
        verbose_name="ФИО проверяемого",
        help_text="Введите фамилию, имя и отчество проверяемого"
    )
    position = models.CharField(
        max_length=255,
        verbose_name="Должность проверяемого",
        help_text="Введите должность проверяемого"
    )
    brigade = models.CharField(
        max_length=255,
        verbose_name="Участок (бригада) проверяемого",
        help_text="Введите участок или бригаду проверяемого"
    )
    company_name = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="Наименование компании",
        help_text="Выберите наименование компании"
    )
    previous_safety_group = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Предыдущая группа электробезопасности",
        help_text="Предыдущая группа электробезопасности "
                  "(обязательно при указании даты предыдущей проверки)"
    )
    safety_group = models.CharField(
        max_length=255,
        verbose_name="Группа электробезопасности",
        help_text="Введите группу электробезопасности"
    )
    work_experience = models.CharField(
        max_length=255,
        verbose_name="Стаж работы",
        help_text="Введите стаж работы"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, создавший запись"
    )

    class Meta:
        verbose_name = "Аттестуемый"
        verbose_name_plural = "Аттестуемые"
        ordering = ['brigade']

    def save(self, *args, **kwargs):
        if not self.pk:  # on creation
            self.company_name = (
                self.user.organization) if self.user.organization else None
        super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name


class Briefing(models.Model):
    """Модель инструктажа."""
    name = models.CharField(
        max_length=255,
        verbose_name="Наименование инструктажа",
        help_text="Введите наименование инструктажа"
    )

    class Meta:
        verbose_name = "Инструктаж"
        verbose_name_plural = "Инструктажи"

    def __str__(self):
        return self.name


class Course(models.Model):
    """Модель программы обучения."""
    course_number = models.CharField(
        max_length=255,
        verbose_name="Номер программы",
        help_text="Введите номер программы"
    )
    course_name = models.CharField(
        max_length=255,
        verbose_name="Наименование программы",
        help_text="Введите наименование программы"
    )
    certificate_number = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Номер удостоверения по специальности",
        help_text="Введите номер удостоверения по специальности "
                  "(при необходимости)"
    )

    class Meta:
        verbose_name = "Программа обучения"
        verbose_name_plural = "Программы обучения"
        ordering = ['course_number', 'course_name']

    def __str__(self):
        return self.course_name


class Examination(models.Model):
    """Модель проверки."""
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время внесения записи",
        help_text="Дата и время внесения записи о проверке "
                  "(заполняется автоматически)"
    )
    previous_check_date = models.DateField(
        blank=True,
        null=True,
        verbose_name="Дата проведения предыдущей проверки",
        help_text="Укажите дату предыдущей проверки"
    )
    current_check_date = models.DateField(
        verbose_name="Дата проведения текущей проверки",
        help_text="Укажите дату текущей проверки"
    )
    next_check_date = models.DateField(
        verbose_name="Дата проведения следующей проверки",
        help_text="Укажите дату следующей проверки"
    )
    protocol_number = models.CharField(
        max_length=255,
        verbose_name="Номер протокола проверки",
        help_text="Номер протокола проверки"
    )
    reason = models.TextField(
        verbose_name="Причина проверки",
        help_text="Укажите причину проверки"
    )

    commission = models.ForeignKey(
        Commission,
        on_delete=models.CASCADE,
        verbose_name="Комиссия",
        help_text="Комиссия, проводящая проверку"
    )
    examined = models.ForeignKey(
        Examined,
        on_delete=models.CASCADE,
        verbose_name="Аттестуемый",
        help_text="Введите данные аттестуемого"
    )
    briefing = models.ForeignKey(
        Briefing,
        on_delete=models.CASCADE,
        verbose_name="Инструктаж",
        help_text="Выберите вид инструктажа"
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        verbose_name="Программа обучения",
        help_text="Выберите программу обучения"
    )

    class Meta:
        verbose_name = "Проверка"
        verbose_name_plural = "Проверки"
        ordering = ['current_check_date', 'next_check_date']

    def __str__(self):
        return f"Проверка {self.protocol_number}"

    def clean(self):
        if self.previous_check_date and not self.examined.previous_safety_group:
            raise ValidationError(
                'Предыдущая группа электробезопасности обязательна '
                'при указании даты предыдущей проверки.'
            )
