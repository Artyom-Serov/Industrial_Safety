"""
Модуль форм для управления проверками, аттестуемыми и комиссией.
"""

from django import forms
from .models import Examination, Examined, Commission
from users.models import User, Organization


class ExaminationCreateForm(forms.ModelForm):
    """
    Форма для создания записи о проверке, включая информацию об аттестуемом и
    комиссии. Обрабатывает данные о предыдущей и текущей проверке, а также о
    членах комиссии. Поддерживает создание объектов Examined и Commission.
    """
    class Meta:
        model = Examination
        fields = [
            'previous_check_date', 'current_check_date', 'next_check_date',
            'protocol_number', 'reason', 'briefing', 'course',
            'certificate_number'
        ]

    # Поля формы для данных об аттестуемом
    full_name = forms.CharField(
        max_length=255,
        label="ФИО проверяемого",
        help_text="Введите фамилию, имя и отчество проверяемого"
    )
    position = forms.CharField(
        max_length=255,
        label="Должность проверяемого",
        help_text="Введите должность проверяемого"
    )
    brigade = forms.CharField(
        max_length=255,
        label="Цех (участок) проверяемого",
        help_text="Укажите цех или участок проверяемого"
    )
    previous_safety_group = forms.CharField(
        max_length=255,
        required=False,
        label="Предыдущая группа электробезопасности",
        help_text="Укажите предыдущую группу электробезопасности "
                  "(обязательно при указании даты предыдущей проверки)"
    )
    safety_group = forms.CharField(
        max_length=255,
        label="Группа электробезопасности",
        help_text="Введите группу электробезопасности"
    )
    work_experience = forms.CharField(
        max_length=255,
        label="Стаж работы",
        help_text="Введите стаж работы"
    )
    # Поля формы для данных о членах комиссии
    chairman_name = forms.CharField(
        max_length=255,
        label="ФИО председателя комиссии",
        help_text="Введите фамилию, имя и отчество председателя комиссии"
    )
    chairman_position = forms.CharField(
        max_length=255,
        label="Должность председателя комиссии",
        help_text="Введите должность председателя комиссии"
    )
    member1_name = forms.CharField(
        max_length=255,
        label="ФИО первого члена комиссии",
        help_text="Введите фамилию, имя и отчество первого члена комиссии"
    )
    member1_position = forms.CharField(
        max_length=255,
        label="Должность первого члена комиссии",
        help_text="Введите должность первого члена комиссии"
    )
    member2_name = forms.CharField(
        max_length=255,
        label="ФИО второго члена комиссии",
        help_text="Введите фамилию, имя и отчество второго члена комиссии"
    )
    member2_position = forms.CharField(
        max_length=255,
        label="Должность второго члена комиссии",
        help_text="Введите должность второго члена комиссии"
    )
    safety_officer_name = forms.CharField(
        max_length=255,
        label="ФИО ответственного за электробезопасность",
        help_text="Введите фамилию, имя и отчество ответственного "
                  "за электробезопасность"
    )
    safety_officer_position = forms.CharField(
        max_length=255,
        label="Должность ответственного за электробезопасность",
        help_text="Введите должность ответственного за электробезопасность"
    )

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму создания проверки, добавляя поля для выбора
        компании и пользователя, если пользователь — суперпользователь.
        """
        user = kwargs.pop('user', None)
        super(ExaminationCreateForm, self).__init__(*args, **kwargs)

        self.user = user

        if user:
            if user.is_superuser:
                self.fields['company_name'] = forms.ModelChoiceField(
                    queryset=Organization.objects.all(),
                    label="Наименование компании",
                    help_text="Укажите компанию аттестуемого и автора записи"
                )
                self.fields['user'] = forms.ModelChoiceField(
                    queryset=User.objects.all(),
                    label="Пользователь",
                    help_text="Укажите автора записи"
                )
            else:
                self.company_name = user.organization
                self.user = user

    def clean(self):
        """
        Проверка валидности данных формы. Убедитесь, что
        дата предыдущей проверки и предыдущая группа электробезопасности
        указаны, если одно из полей заполнено.
        """
        cleaned_data = super().clean()
        previous_check_date = cleaned_data.get('previous_check_date')
        previous_safety_group = cleaned_data.get('previous_safety_group')

        if previous_check_date and not previous_safety_group:
            self.add_error('previous_safety_group',
                           "Предыдущая группа электробезопасности обязательна"
                           "при указании даты предыдущей проверки.")

        if previous_safety_group and not previous_check_date:
            self.add_error('previous_check_date',
                           "Дата проведения предыдущей проверки обязательна"
                           "при указании предыдущей группы"
                           "электробезопасности.")

    def save(self, commit=True):
        """
        Сохраняет запись о проверке, создает объекты Examined и Commission
        для текущей проверки.
        """
        instance = super(ExaminationCreateForm, self).save(commit=False)

        examined = Examined(
            full_name=self.cleaned_data['full_name'],
            position=self.cleaned_data['position'],
            brigade=self.cleaned_data['brigade'],
            previous_safety_group=self.cleaned_data['previous_safety_group'],
            safety_group=self.cleaned_data['safety_group'],
            work_experience=self.cleaned_data['work_experience'],
            user=self.user
        )

        if self.user.is_superuser:
            examined.company_name = self.cleaned_data['company_name']
            examined.user = self.cleaned_data['user']
        else:
            examined.company_name = self.company_name
            examined.user = self.user

        examined.save()

        commission = Commission(
            chairman_name=self.cleaned_data['chairman_name'],
            chairman_position=self.cleaned_data['chairman_position'],
            member1_name=self.cleaned_data['member1_name'],
            member1_position=self.cleaned_data['member1_position'],
            member2_name=self.cleaned_data['member2_name'],
            member2_position=self.cleaned_data['member2_position'],
            safety_officer_name=self.cleaned_data['safety_officer_name'],
            safety_officer_position=self.cleaned_data[
                'safety_officer_position'
            ]
        )

        commission.save()

        instance.examined = examined
        instance.commission = commission
        instance.save()
        return instance


class ExaminationUpdateForm(forms.ModelForm):
    """
    Форма для обновления информации о проверке, аттестуемом и комиссии.
    Загружает существующие данные для редактирования, обновляет связанные
    объекты Examined и Commission.
    """
    class Meta:
        model = Examination
        fields = [
            'previous_check_date', 'current_check_date', 'next_check_date',
            'protocol_number', 'reason', 'briefing', 'course',
            'certificate_number'
        ]

    # Поля формы для данных об аттестуемом
    full_name = forms.CharField(max_length=255, label="ФИО проверяемого")
    position = forms.CharField(max_length=255, label="Должность проверяемого")
    brigade = forms.CharField(
        max_length=255, label="Участок (бригада) проверяемого"
    )
    previous_safety_group = forms.CharField(
        max_length=255, required=False,
        label="Предыдущая группа электробезопасности"
    )
    safety_group = forms.CharField(
        max_length=255, label="Группа электробезопасности"
    )
    work_experience = forms.CharField(max_length=255, label="Стаж работы")
    # Поля формы для данных о членах комиссии
    chairman_name = forms.CharField(
        max_length=255, label="ФИО председателя комиссии"
    )
    chairman_position = forms.CharField(
        max_length=255, label="Должность председателя комиссии"
    )
    member1_name = forms.CharField(
        max_length=255, label="ФИО первого члена комиссии"
    )
    member1_position = forms.CharField(
        max_length=255, label="Должность первого члена комиссии"
    )
    member2_name = forms.CharField(
        max_length=255, label="ФИО второго члена комиссии"
    )
    member2_position = forms.CharField(
        max_length=255, label="Должность второго члена комиссии"
    )
    safety_officer_name = forms.CharField(
        max_length=255, label="ФИО ответственного за электробезопасность"
    )
    safety_officer_position = forms.CharField(
        max_length=255,
        label="Должность ответственного за электробезопасность"
    )

    def __init__(self, *args, **kwargs):
        """
        Инициализирует форму обновления проверки, заполняя поля начальными
        значениями из существующих объектов Examined и Commission, если они
        связаны с текущей записью.
        """
        super().__init__(*args, **kwargs)
        if (self.instance and hasattr(self.instance, 'examined') and
                self.instance.examined):
            self.initial.update({
                'full_name': self.instance.examined.full_name,
                'position': self.instance.examined.position,
                'brigade': self.instance.examined.brigade,
                'previous_safety_group':
                    self.instance.examined.previous_safety_group,
                'safety_group': self.instance.examined.safety_group,
                'work_experience': self.instance.examined.work_experience,
            })

        if (self.instance and hasattr(self.instance, 'commission') and
                self.instance.commission):
            self.initial.update({
                'chairman_name': self.instance.commission.chairman_name,
                'chairman_position':
                    self.instance.commission.chairman_position,
                'member1_name': self.instance.commission.member1_name,
                'member1_position': self.instance.commission.member1_position,
                'member2_name': self.instance.commission.member2_name,
                'member2_position': self.instance.commission.member2_position,
                'safety_officer_name':
                    self.instance.commission.safety_officer_name,
                'safety_officer_position':
                    self.instance.commission.safety_officer_position,
            })

    def clean(self):
        """
        Валидирует данные, проверяя наличие предыдущей даты и группы при
        необходимости.
        """
        cleaned_data = super().clean()
        previous_check_date = cleaned_data.get('previous_check_date')
        previous_safety_group = cleaned_data.get('previous_safety_group')

        if previous_check_date and not previous_safety_group:
            self.add_error('previous_safety_group',
                           "Предыдущая группа электробезопасности обязательна"
                           "при указании даты предыдущей проверки.")

        if previous_safety_group and not previous_check_date:
            self.add_error('previous_check_date',
                           "Дата проведения предыдущей проверки обязательна"
                           "при указании предыдущей группы"
                           "электробезопасности.")

    def save(self, commit=True):
        """
        Сохраняет изменения в записи о проверке и обновляет объекты Examined
        и Commission.
        """
        examination = super().save(commit=False)
        examined_data = {
            'full_name': self.cleaned_data['full_name'],
            'position': self.cleaned_data['position'],
            'brigade': self.cleaned_data['brigade'],
            'previous_safety_group': self.cleaned_data.get(
                'previous_safety_group'
            ),
            'safety_group': self.cleaned_data['safety_group'],
            'work_experience': self.cleaned_data['work_experience'],
        }
        commission_data = {
            'chairman_name': self.cleaned_data['chairman_name'],
            'chairman_position': self.cleaned_data['chairman_position'],
            'member1_name': self.cleaned_data['member1_name'],
            'member1_position': self.cleaned_data['member1_position'],
            'member2_name': self.cleaned_data['member2_name'],
            'member2_position': self.cleaned_data['member2_position'],
            'safety_officer_name': self.cleaned_data['safety_officer_name'],
            'safety_officer_position': self.cleaned_data[
                'safety_officer_position'
            ],
        }

        if examination.examined:
            for key, value in examined_data.items():
                setattr(examination.examined, key, value)
            examination.examined.save()

        if examination.commission:
            for key, value in commission_data.items():
                setattr(examination.commission, key, value)
            examination.commission.save()

        if commit:
            examination.save()
        return examination
