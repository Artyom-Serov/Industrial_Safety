from django import forms
from .models import Examination


class ExaminationForm(forms.ModelForm):
    class Meta:
        model = Examination
        fields = [
            'previous_check_date', 'current_check_date', 'next_check_date',
            'protocol_number', 'reason', 'commission', 'examined',
            'briefing', 'course'
        ]
