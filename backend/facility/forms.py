from django import forms
from .models import Examination, Examined
from users.models import User, Organization


class ExaminationCreateForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = [
            'previous_check_date', 'current_check_date', 'next_check_date',
            'protocol_number', 'reason', 'commission', 'briefing', 'course'
        ]

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
        label="Участок (бригада) проверяемого",
        help_text="Введите участок или бригаду проверяемого"
    )
    previous_safety_group = forms.CharField(
        max_length=255,
        required=False,
        label="Предыдущая группа электробезопасности",
        help_text="Предыдущая группа электробезопасности (обязательно при указании даты предыдущей проверки)"
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

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExaminationCreateForm, self).__init__(*args, **kwargs)

        self.user = user

        if user:
            if user.is_superuser:
                self.fields['company_name'] = forms.ModelChoiceField(
                    queryset=Organization.objects.all(),
                    label="Наименование компании",
                    help_text="Выберите наименование компании"
                )
                self.fields['user'] = forms.ModelChoiceField(
                    queryset=User.objects.all(),
                    label="Пользователь",
                    help_text="Пользователь, создавший запись"
                )
            else:
                self.company_name = user.organization
                self.user = user

    def save(self, commit=True):
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
        instance.examined = examined
        instance.save()
        return instance
