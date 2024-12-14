from django.test import SimpleTestCase
from documents.forms import DocumentGenerationForm


class DocumentGenerationFormTest(SimpleTestCase):
    # тестирование формы выбора шаблона для генерации документа

    def setUp(self):
        self.valid_data = {
            'template': "протокол_проверки_по_ОТ"
        }
        self.invalid_data = {
            'template': "несуществующий_шаблон"
        }

    def test_form_valid(self):
        # тестирование валидности формы при корректных данных
        form = DocumentGenerationForm(data=self.valid_data)
        self.assertTrue(form.is_valid())

    def test_form_invalid_with_incorrect_template(self):
        # тестирование не валидности формы при некорректных данных
        form = DocumentGenerationForm(data=self.invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('template', form.errors)

    def test_form_template_choice(self):
        # тестирование содержание в форме всех доступных вариантов
        form = DocumentGenerationForm()
        choices = dict(form.fields['template'].choices)
        expected_choices = {
            'протокол_проверки_по_БДД':
                'Протокол проверки по безопасности дорожного движения',
            'протокол_проверки_по_ОТ':
                'Протокол проверки по охране труда',
            'протокол_проверки_по_ПБ':
                'Протокол проверки по охране труда',
            'протокол_проверки_по_первой_помощи':
                'Протокол проверки оказания первой медицинской помощи',
            'удостоверение_пороверки_по_ОТ':
                'Удостоверение проверки по охране труда',
            'удостоверение_по_ЭБ':
                'Удостоверение проверки по электробезопасности',
        }
        self.assertEqual(choices, expected_choices)
