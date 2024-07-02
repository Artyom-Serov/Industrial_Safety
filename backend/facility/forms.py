from django import forms
from .models import Examination, Examined


class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = [
            'previous_check_date', 'current_check_date', 'next_check_date',
            'protocol_number', 'reason', 'commission', 'examined',
            'briefing', 'course'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(ExaminationForm, self).__init__(*args, **kwargs)

        if user and not user.is_superuser:
            self.fields['examined'].queryset = Examined.objects.filter(
                company_name=user.organization
            )
